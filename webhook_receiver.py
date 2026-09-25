import os

from fastapi import FastAPI, Request, HTTPException
import httpx


app = FastAPI(title="TradingView → Telegram Webhook")


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print(
        "WARNING: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID "
        "are not configured."
    )


def format_message(data: dict) -> str:
    raw = data.get("message", "")

    if isinstance(raw, str) and raw:
        parts = raw.split("|")

        if len(parts) >= 4 and parts[0] == "EMA_MTF":
            signal = parts[1]
            stage = parts[2]
            symbol = parts[3]
            price = parts[4] if len(parts) > 4 else "N/A"

            return (
                "📊 EMA 8/50/200 MTF ALERT\n\n"
                f"Signal: {signal}\n"
                f"Stage: {stage}\n"
                f"Symbol: {symbol}\n"
                f"Price: {price}"
            )

    return "📊 TradingView ALERT\n\n" + "\n".join(
        f"{key}: {value}" for key, value in data.items()
    )


@app.get("/")
async def health():
    return {
        "status": "ok",
        "service":
