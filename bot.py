import os
import asyncio
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
AFFILIATE_LINK = "https://meli.la/12Zus1f"

async def main():
    if not TOKEN or not CHAT_ID:
        raise SystemExit("Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID.")
    bot = Bot(TOKEN)
    text = (
        "🥃 *OFERTA DE WHISKY*\n\n"
        "*Teste do RR WHISKY*\n"
        "🔥 Oferta encontrada no Mercado Livre\n\n"
        f"👉 [VER OFERTA]({AFFILIATE_LINK})\n\n"
        "⚠️ Preço e disponibilidade podem mudar.\n"
        "🔞 Venda de bebidas alcoólicas somente para maiores de 18 anos."
    )
    await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        parse_mode="Markdown",
        disable_web_page_preview=False,
    )

if __name__ == "__main__":
    asyncio.run(main())
