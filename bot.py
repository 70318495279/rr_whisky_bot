import os
import asyncio
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

BUSCA = "whisky site:shopee.com.br"


def buscar_ofertas():

    consulta = quote(BUSCA)

    url = f"https://www.google.com/search?q={consulta}&num=10"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9"
    }

    print("🔎 Procurando ofertas da Shopee...")

    resposta = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print(f"📡 Status da busca: {resposta.status_code}")

    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, "html.parser")

    ofertas = []
    vistos = set()

    for resultado in soup.select("a"):

        href = resultado.get("href", "")

        if "shopee.com.br" not in href:
            continue

        if href in vistos:
            continue

        titulo = resultado.get_text(" ", strip=True)

        if not titulo:
            continue

        # Evita links gerais da Shopee
        partes_invalidas = [
            "/search",
            "/m/",
            "/mall",
            "/buyer",
            "/seller"
        ]

        if any(parte in href for parte in partes_invalidas):
            continue

        vistos.add(href)

        ofertas.append({
            "titulo": titulo[:200],
            "link": href
        })

        if len(ofertas) >= 5:
            break

    print(f"🛒 Links da Shopee encontrados: {len(ofertas)}")

    return ofertas


def criar_mensagem(oferta):

    return (
        "🥃🔥 *OFERTA DE WHISKY*\n\n"
        f"*{oferta['titulo']}*\n\n"
        "🛒 [VER OFERTA]("
        f"{oferta['link']}"
        ")\n\n"
        "⚠️ Preço e disponibilidade podem mudar.\n"
        "🔞 Venda de bebidas alcoólicas somente para maiores de 18 anos."
    )


async def main():

    if not TOKEN:
        raise SystemExit(
            "❌ TELEGRAM_BOT_TOKEN não configurado."
        )

    if not CHAT_ID:
        raise SystemExit(
            "❌ TELEGRAM_CHAT_ID não configurado."
        )

    print("🥃 RR WHISKY BOT")
    print("🔎 Procurando promoções na Shopee...")

    ofertas = buscar_ofertas()

    if not ofertas:
        print("⚠️ Nenhum resultado da Shopee encontrado.")
        return

    print(f"✅ {len(ofertas)} resultados encontrados.")

    bot = Bot(TOKEN)

    enviadas = 0

    for oferta in ofertas:

        try:

            mensagem = criar_mensagem(oferta)

            await bot.send_message(
                chat_id=CHAT_ID,
                text=mensagem,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )

            enviadas += 1

            print(
                f"📨 Enviada: {oferta['titulo']}"
            )

            await asyncio.sleep(3)

        except Exception as erro:

            print(
                f"❌ Erro ao enviar: {erro}"
            )

    print(
        f"✅ Finalizado. {enviadas} ofertas enviadas ao Telegram."
    )


if __name__ == "__main__":
    asyncio.run(main())
