import { t as definePluginEntry } from "/root/.local/share/pnpm/global/5/node_modules/openclaw/dist/plugin-entry-D003nEZe.js";
import { t as enablePluginInConfig } from "/root/.local/share/pnpm/global/5/node_modules/openclaw/dist/enable-Dy2yeUXz.js";
import { c as setScopedCredentialValue, r as getScopedCredentialValue } from "/root/.local/share/pnpm/global/5/node_modules/openclaw/dist/provider-web-search-D9NXyLYm.js";
import { Type } from "/root/.local/share/pnpm/global/5/node_modules/openclaw/dist/extensions/feishu/node_modules/@sinclair/typebox/build/esm/index.mjs";

function normalizeBaseUrl(input) {
  const raw = (input || 'https://api.openai.com/v1').trim();
  return raw.endsWith('/') ? raw.slice(0, -1) : raw;
}

function resolveCfg(config) {
  const webSearch = config?.plugins?.entries?.['openai-native-web-search']?.config?.webSearch;
  return webSearch && typeof webSearch === 'object' && !Array.isArray(webSearch) ? webSearch : {};
}

function extractText(output) {
  if (!output) return '';
  if (typeof output.output_text === 'string' && output.output_text.trim()) return output.output_text.trim();
  const parts = [];
  for (const item of output.output || []) {
    if (item.type === 'message' && Array.isArray(item.content)) {
      for (const c of item.content) {
        if (c?.type === 'output_text' && c.text) parts.push(c.text);
      }
    }
  }
  return parts.join('\n').trim();
}

function extractCitations(output) {
  const refs = [];
  for (const item of output.output || []) {
    if (item.type === 'web_search_call' && Array.isArray(item.action?.sources)) {
      for (const s of item.action.sources) {
        refs.push({
          title: s.title || s.url || 'source',
          url: s.url || '',
          snippet: s.snippet || '',
          siteName: (() => { try { return s.url ? new URL(s.url).hostname : undefined; } catch { return undefined; } })()
        });
      }
    }
  }
  return refs;
}

const OpenAiNativeSearchSchema = Type.Object({
  query: Type.String({ description: 'Search query string.' }),
  count: Type.Optional(Type.Number({ description: 'Number of results to return (1-10).', minimum: 1, maximum: 10 }))
}, { additionalProperties: false });

function createOpenAiNativeWebSearchProvider() {
  return {
    id: 'openai-native',
    label: 'OpenAI Native Web Search',
    hint: 'Use OpenAI-compatible Responses API native web_search',
    requiresCredential: true,
    envVars: [],
    placeholder: 'Configure webSearch.apiKey',
    signupUrl: 'https://platform.openai.com/',
    docsUrl: 'https://platform.openai.com/docs/guides/tools-web-search',
    autoDetectOrder: 40,
    credentialPath: 'plugins.entries.openai-native-web-search.config.webSearch.apiKey',
    inactiveSecretPaths: [],
    getCredentialValue: (searchConfig) => getScopedCredentialValue(searchConfig, 'openai-native'),
    setCredentialValue: (searchConfigTarget, value) => setScopedCredentialValue(searchConfigTarget, 'openai-native', value),
    applySelectionConfig: (config) => enablePluginInConfig(config, 'openai-native-web-search').config,
    createTool: (ctx) => ({
      description: 'Search the web using an OpenAI-compatible Responses API native web_search tool.',
      parameters: OpenAiNativeSearchSchema,
      execute: async (args) => {
        const pluginCfg = resolveCfg(ctx.config);
        const apiKey = pluginCfg.apiKey;
        const baseUrl = normalizeBaseUrl(pluginCfg.baseUrl);
        const model = pluginCfg.model || 'gpt-5.4';
        const timeoutSeconds = Math.max(1, Number(pluginCfg.timeoutSeconds || 30));
        const count = Math.max(1, Math.min(10, Math.floor(Number(args?.count || 5))));
        if (!apiKey) {
          return { error: 'missing_openai_api_key', provider: 'openai-native' };
        }
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), timeoutSeconds * 1000);
        try {
          const resp = await fetch(`${baseUrl}/responses`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
              model,
              tools: [{ type: 'web_search' }],
              input: `${String(args.query || '')}\n\n请在回答末尾附上你实际使用到的来源链接；如果有官方或权威来源，优先给出。`,
              reasoning: { effort: 'low' }
            }),
            signal: controller.signal
          });
          const data = await resp.json();
          if (!resp.ok) {
            return { error: 'openai_native_web_search_error', provider: 'openai-native', status: resp.status, detail: data };
          }
          const results = extractCitations(data).slice(0, count);
          return {
            query: String(args.query || ''),
            provider: 'openai-native',
            count: results.length,
            externalContent: {
              untrusted: true,
              source: 'web_search',
              provider: 'openai-native',
              wrapped: true
            },
            answer: extractText(data),
            results
          };
        } finally {
          clearTimeout(timer);
        }
      }
    })
  };
}

export default definePluginEntry({
  id: 'openai-native-web-search',
  name: 'OpenAI Native Web Search',
  description: 'Route OpenClaw web_search to OpenAI-compatible Responses API native web_search.',
  register(api) {
    api.registerWebSearchProvider(createOpenAiNativeWebSearchProvider());
  }
});
