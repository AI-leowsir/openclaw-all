#!/usr/bin/env python3
"""Fetch official Hangzhou weather from China Weather and push morning summary.

Data source: 中国天气网 / 中央气象台 weather.com.cn pages.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

CITY_CODE = "101210101"  # Hangzhou 城区, 中国天气网
SEVEN_DAY_URL = f"https://www.weather.com.cn/weather/{CITY_CODE}.shtml"
ONE_DAY_URL = f"https://www.weather.com.cn/weather1d/{CITY_CODE}.shtml"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 Chrome Safari/537.36"
RAIN_WORDS = ("雨", "阵雨", "雷阵雨", "暴雨", "大雨", "中雨", "小雨", "雨夹雪")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read()
    for enc in ("utf-8", "gbk", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def clean_html_text(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = re.sub(r"&nbsp;|&#160;", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def parse_daily_by_label(html: str, label: str = "今天") -> dict:
    text = clean_html_text(html)
    m = re.search(rf"(\d{{1,2}}日（{re.escape(label)}）)\s*\n+\s*([^\n]+)\s*\n+\s*(\d+)\s*\n+\s*/\s*\n+\s*(-?\d+)℃\s*(?:\n+\s*([^\n]+))?", text)
    if not m:
        raise RuntimeError(f"未能从中国天气网7天预报解析{label}天气")
    wind = (m.group(5) or "风力未识别").strip()
    return {
        "date_label": m.group(1),
        "weather": m.group(2).strip(),
        "temp": f"{m.group(3).strip()}/{m.group(4).strip()}℃",
        "wind": wind,
    }


def parse_today_daily(html: str) -> dict:
    return parse_daily_by_label(html, "今天")


def parse_tomorrow_daily(html: str) -> dict:
    return parse_daily_by_label(html, "明天")


def parse_update_text(html: str) -> str | None:
    text = clean_html_text(html)
    m = re.search(r"(\d{1,2}:\d{2}更新\s*\|\s*数据来源\s*中央气象台)", text)
    if m:
        return m.group(1)
    m = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}更新)", text)
    return m.group(1) if m else None


def parse_hourly(html: str) -> list[dict]:
    m = re.search(r'var\s+hour3data\s*=\s*(\{[\s\S]*?\})\s*</script>', html, flags=re.I)
    if not m:
        m = re.search(r'var\s+hour3data\s*=\s*(\{[\s\S]*?\})\s*\n\s*var\s+observe24h_data', html)
    if not m:
        m = re.search(r"var\s+hour3data\s*=\s*(\{[\s\S]*?\});", html)
    if not m:
        return []
    data = json.loads(m.group(1))
    rows = []
    for s in data.get("1d", []):
        parts = s.split(",")
        if len(parts) >= 6:
            dm = re.match(r"(\d{1,2})日(\d{1,2})时", parts[0])
            if dm:
                rows.append({
                    "day": int(dm.group(1)),
                    "hour": int(dm.group(2)),
                    "weather": parts[2],
                    "temp": parts[3],
                    "wind_dir": parts[4],
                    "wind_level": parts[5],
                    "raw": s,
                })
    return rows


def has_rain(weather: str) -> bool:
    return any(w in weather for w in RAIN_WORDS)


def build_message() -> str:
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    seven = fetch(SEVEN_DAY_URL)
    one = fetch(ONE_DAY_URL)
    daily = parse_today_daily(seven)
    hourly = parse_hourly(one)
    update_text = parse_update_text(one) or parse_update_text(seven) or "更新时间未识别"

    dm = re.match(r"(\d{1,2})日", daily["date_label"])
    target_day = int(dm.group(1)) if dm else (now + timedelta(days=1)).day

    morning = [r for r in hourly if r["day"] == target_day and 7 <= r["hour"] <= 9]
    nearby = [r for r in hourly if r["day"] == target_day and 5 <= r["hour"] <= 11]

    if morning:
        rain_slots = [r for r in morning if has_rain(r["weather"])]
        rain_line = "会下雨" if rain_slots else "官方分时段未显示下雨"
        slot_desc = "；".join(f"{r['hour']:02d}:00 {r['weather']} {r['temp']}" for r in morning)
    else:
        rain_line = "官方未给出7–9点精确逐小时；按附近分时段+全天预报判断，需带伞"
        slot_desc = "；".join(f"{r['hour']:02d}:00 {r['weather']} {r['temp']}" for r in nearby) or "未取到7–9点附近分时段"

    advice = "带伞" if (has_rain(daily["weather"]) or any(has_rain(r["weather"]) for r in morning + nearby)) else "暂不必带伞"
    return (
        "杭州天气早报（官方口径）\n"
        "来源：中国天气网 / 中央气象台\n"
        f"{update_text}\n"
        f"{daily['date_label']}：{daily['weather']}，{daily['temp']}，{daily['wind']}\n"
        f"7–9点是否下雨：{rain_line}\n"
        f"分时段参考：{slot_desc}\n"
        f"建议：{advice}。"
    )


def send_feishu(target: str, message: str) -> None:
    subprocess.run([
        "openclaw", "message", "send",
        "--channel", "feishu",
        "--target", target,
        "--message", message,
    ], check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--target", default="user:ou_da3fa0f8362b148f6f331adacfc07607")
    args = ap.parse_args()
    try:
        msg = build_message()
    except Exception as e:
        msg = f"杭州天气官方数据获取失败：{e}。请手动查看中国天气网：{SEVEN_DAY_URL}"
    print(msg)
    if args.send:
        send_feishu(args.target, msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
