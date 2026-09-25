import os

import httpx
from fastapi import FastAPI, HTTPException, Request


app = FastAPI(title="TradingView Telegram Webhook")


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


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

    lines = [
        f"{key}: {value}"
        for key, value in data.items()
    ]

    return "📊 TradingView ALERT\n\n" + "\n".join(lines)


@app.get("/")
async def health():
    return {
        "status": "ok",
        "service": "TradingView Telegram webhook",
    }


@app.post("/tradingview")
async def tradingview(request: Request):

    if WEBHOOK_SECRET:
        supplied_secret = request.headers.get(
            "X-Webhook-Secret",
            "",
        )

        if supplied_secret != WEBHOOK_SECRET:
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook secret",
            )

    content_type = request.headers.get(
        "content-type",
        "",
    )

    if "application/json" in content_type:
        data = await request.json()

        if not isinstance(data, dict):
            data = {
                "message": str(data),
            }

    else:
        body = (
            await request.body()
        ).decode(
            "utf-8",
            errors="replace",
        )

        data = {
            "message": body,
        }

    message = format_message(data)

    telegram_url = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    async with httpx.AsyncClient(
        timeout=15
    ) as client:

        response = await client.post(
            telegram_url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=(
                "Telegram API error: "
                f"{response.text[:500]}"
            ),
        )

    return {
        "status": "sent",
    }
