import os
import requests
import asyncio
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"


def buscar_ofertas():
    params = {
        "q": "whisky",
        "limit": 20,
        "sort": "price_asc"
    }

    response = requests.get(
        SEARCH_URL,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    produtos = response.json().get("results", [])

    ofertas = []

    for produto in produtos:
        titulo = produto.get("title", "")
        preco = produto.get("price")
        link = produto.get("permalink")

        if not titulo or not preco or not link:
            continue

        ofertas.append({
            "titulo": titulo,
            "preco": preco,
            "link": link
        })

    return ofertas[:5]


def criar_mensagem(oferta):
    return (
        "🥃🔥 *OFERTA DE WHISKY*\n\n"
        f"*{oferta['titulo']}*\n\n"
        f"💰 *R$ {oferta['preco']:.2f}*\n\n"
        f"🛒 [VER OFERTA]({oferta['link']})\n\n"
        "⚠️ Preço e disponibilidade podem mudar.\n"
        "🔞 Venda de bebidas alcoólicas somente para maiores de 18 anos."
    )


async def main():

    if not TOKEN or not CHAT_ID:
        raise SystemExit(
            "ERRO: configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID."
        )

    bot = Bot(TOKEN)

    ofertas = buscar_ofertas()

    if not ofertas:
        print("Nenhuma oferta encontrada.")
        return

    for oferta in ofertas:

        mensagem = criar_mensagem(oferta)

        await bot.send_message(
            chat_id=CHAT_ID,
            text=mensagem,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )

        print(f"Enviado: {oferta['titulo']}")

        await asyncio.sleep(3)

    print("✅ Ofertas enviadas com sucesso.")


if __name__ == "__main__":
    asyncio.run(main())
