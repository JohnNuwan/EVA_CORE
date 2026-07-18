# Discord Embed-to-Image Sending Pattern

When sending a rich report to a Discord webhook, use **two separate POSTs**:

## 1. Send the embed

```python
import requests

r = requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
# Expects HTTP 204
```

## 2. Send the chart image

```python
r2 = requests.post(
    WEBHOOK_URL,
    files={"file": ("chart.png", bytes_io_buffer, "image/png")},
    timeout=15
)
# Expects HTTP 204
```

## Why not multipart payload_json+files?

Discord's `payload_json` + `attachments` + `files` multipart upload is the documented approach, but in practice:

- The `attachment` ID referencing in the embed's `image.url` often fails with HTTP 400 `{"attachments": ["0"]}`
- The error is opaque — no detail on what's wrong with the attachment spec
- Sending embed and image separately is simpler and always works

## Example embed structure

```python
embed = {
    "title": "📊 Report Title",
    "description": "Mise à jour: ...",
    "color": 0x4ade80,  # green
    "fields": [
        {"name": "📋 SECTION", "value": "──────────────", "inline": False},
        {"name": "📈 Stock (TICKER)", "value": "**125.05€**\n📈 Jour: +0.50% | 1m: +3.4%\n⚪ RSI: 52.1", "inline": True},
    ],
    "footer": {"text": "Footer text"},
    "timestamp": "2026-07-08T14:00:00Z",
}
```

## Limits

- Discord embed field values: 1024 characters max
- Total embed: 6000 characters
- Webhook message: 2000 characters
- For long reports, split fields across multiple embeds in a single array
