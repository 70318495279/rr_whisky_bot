
import os
import asyncio
import requests
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"
INTERVALO_MINUTOS = 30

enviados = set()


def buscar_ofertas():
    params = {
        "q": "whisky",
        "limit": 20,
        "sort": "price_asc"
    }

    response = requests.get(SEARCH_URL, params=params, timeout=20)
    response.raise_for_status()

    produtos = response.json().get("results", [])

    ofertas = []

    for produto in produtos:
        titulo = produto.get("title", "")
        preco = produto.get("price")
        link = produto.get("permalink")
        produto_id = produto.get("id")

        if not titulo or not preco or not link:
            continue

        # Evita produtos repetidos
        if produto_id in enviados:
            continue

        ofertas.append({
            "id": produto_id,
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
        "🛒 [VER OFERTA]("
        f"{oferta['link']}"
        ")\n\n"
        "⚠️ Preço e disponibilidade podem mudar.\n"
        "🔞 Venda de bebidas alcoólicas somente para maiores de 18 anos."
    )


async def enviar_ofertas():
    bot = Bot(TOKEN)

    ofertas = buscar_ofertas()

    for oferta in ofertas:
        mensagem = criar_mensagem(oferta)

        await bot.send_message(
            chat_id=CHAT_ID,
            text=mensagem,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )

        enviados.add(oferta["id"])

        await asyncio.sleep(3)


async def main():
    if not TOKEN or not CHAT_ID:
        raise SystemExit(
            "Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID."
        )

    while True:
        try:
            await enviar_ofertas()
        except Exception as erro:
            print(f"Erro: {erro}")

        await asyncio.sleep(INTERVALO_MINUTOS * 60)


if __name__ == "__main__":
    asyncio.run(main())
