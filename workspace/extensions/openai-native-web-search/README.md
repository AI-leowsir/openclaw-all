# openai-native-web-search

A local OpenClaw plugin that routes `web_search` to an OpenAI-compatible Responses API with native `tools:[{type:"web_search"}]`.

## What it does

- Registers a custom web search provider: `openai-native`
- Forwards OpenClaw `web_search` calls to:
  - `POST <baseUrl>/responses`
  - `tools: [{"type":"web_search"}]`
- Returns the model answer back to OpenClaw
- Encourages the upstream model to include official/authoritative source links in the answer text

## Plugin location

```text
extensions/openai-native-web-search
```

## Files

- `openclaw.plugin.json` — plugin manifest
- `package.json` — package metadata
- `index.js` — plugin entry + provider implementation

## Current behavior

Working:
- `web_search` routes through provider `openai-native`
- OpenAI-compatible Responses API web search works
- Answer text can include source links

Known limitation:
- If upstream does not return structured citations / sources, OpenClaw `results` may remain empty
- In that case, links appear in `answer` text only

## Required OpenClaw config

Example plugin config under `openclaw.json`:

```json
{
  "tools": {
    "web": {
      "search": {
        "enabled": true,
        "provider": "openai-native"
      }
    }
  },
  "plugins": {
    "entries": {
      "openai-native-web-search": {
        "enabled": true,
        "config": {
          "webSearch": {
            "baseUrl": "https://tarotap.pro/v1",
            "apiKey": "YOUR_API_KEY",
            "model": "gpt-5.4",
            "timeoutSeconds": 30
          }
        }
      }
    }
  }
}
```

## Reload

After changes, reload gateway:

```bash
systemctl --user restart openclaw-gateway.service
```

## Notes

- This plugin currently imports some OpenClaw internal runtime modules by absolute path.
- That means it is tied to the installed OpenClaw version and may need updates after upgrades.
- Best suited as a local custom plugin for this machine.
