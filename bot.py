import os
import asyncio
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

BUSCA = "whisky"


def buscar_ofertas():
    url = (
        "https://lista.mercadolivre.com.br/"
        + quote(BUSCA)
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/18.0 Mobile/15E148 Safari/604.1"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    produtos = []

    itens = soup.select("li.ui-search-layout__item")

    for item in itens:

        titulo_elemento = item.select_one(
            "a.poly-component__title"
        )

        if not titulo_elemento:
            titulo_elemento = item.select_one(
                "h2.ui-search-item__title"
            )

        preco_elemento = item.select_one(
            "span.andes-money-amount__fraction"
        )

        link_elemento = item.select_one(
            "a.poly-component__title"
        )

        if not link_elemento:
            link_elemento = item.select_one(
                "a.ui-search-link"
            )

        if not titulo_elemento or not preco_elemento or not link_elemento:
            continue

        titulo = titulo_elemento.get_text(
            " ",
            strip=True
        )

        preco = preco_elemento.get_text(
            " ",
            strip=True
        )

        link = link_elemento.get("href")

        if not titulo or not preco or not link:
            continue

        produtos.append({
            "titulo": titulo,
            "preco": preco,
            "link": link
        })

        if len(produtos) >= 5:
            break

    return produtos


def criar_mensagem(oferta):

    return (
        "🥃🔥 *OFERTA DE WHISKY*\n\n"
        f"*{oferta['titulo']}*\n\n"
        f"💰 *R$ {oferta['preco']}*\n\n"
        f"🛒 [VER OFERTA]({oferta['link']})\n\n"
        "⚠️ Preço e disponibilidade podem mudar.\n"
        "🔞 Venda de bebidas alcoólicas somente para maiores de 18 anos."
    )


async def main():

    if not TOKEN:
        raise SystemExit(
            "ERRO: TELEGRAM_BOT_TOKEN não configurado."
        )

    if not CHAT_ID:
        raise SystemExit(
            "ERRO: TELEGRAM_CHAT_ID não configurado."
        )

    print("🔎 Procurando ofertas de whisky...")

    ofertas = buscar_ofertas()

    if not ofertas:
        print("⚠️ Nenhuma oferta encontrada.")
        return

    print(f"✅ {len(ofertas)} ofertas encontradas.")

    bot = Bot(TOKEN)

    for oferta in ofertas:

        mensagem = criar_mensagem(oferta)

        await bot.send_message(
            chat_id=CHAT_ID,
            text=mensagem,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )

        print(f"📨 Enviado: {oferta['titulo']}")

        await asyncio.sleep(3)

    print("✅ Todas as ofertas foram enviadas.")
    print("✅ BOT FINALIZADO COM SUCESSO.")


if __name__ == "__main__":
    asyncio.run(main())
