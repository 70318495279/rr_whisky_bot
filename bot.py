import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

URL = "https://shopee.com.br/search?keyword=whisky"


def buscar_ofertas():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Accept": "text/html,application/xhtml+xml,"
                  "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }

    print("🌐 Acessando Shopee...")

    resposta = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    print(f"📡 Status Shopee: {resposta.status_code}")
    print(f"📦 Tamanho da resposta: {len(resposta.text)} caracteres")

    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, "html.parser")

    # Procuramos links de produtos.
    links = soup.find_all("a", href=True)

    ofertas = []
    vistos = set()

    for link in links:

        href = link.get("href", "")

        if "/product/" not in href:
            continue

        titulo = link.get_text(" ", strip=True)

        if not titulo:
            continue

        if href.startswith("/"):
            href = "https://shopee.com.br" + href

        if href in vistos:
            continue

        vistos.add(href)

        ofertas.append({
            "titulo": titulo,
            "link": href
        })

        if len(ofertas) >= 5:
            break

    print(f"🔎 Produtos encontrados: {len(ofertas)}")

    return ofertas


def criar_mensagem(oferta):

    return (
        "🥃🔥 *OFERTA DE WHISKY NA SHOPEE*\n\n"
        f"*{oferta['titulo']}*\n\n"
        f"🛒 [VER OFERTA]({oferta['link']})\n\n"
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
    print("🔎 Procurando ofertas na Shopee...")

    ofertas = buscar_ofertas()

    if not ofertas:
        print("⚠️ A Shopee respondeu, mas não entregou links de produtos.")
        print("ℹ️ Isso pode acontecer quando a Shopee exige JavaScript ou bloqueia o acesso automático.")
        return

    bot = Bot(TOKEN)

    enviadas = 0

    for oferta in ofertas:

        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=criar_mensagem(oferta),
                parse_mode="Markdown",
                disable_web_page_preview=False
            )

            enviadas += 1

            print(f"📨 Enviada: {oferta['titulo']}")

            await asyncio.sleep(3)

        except Exception as erro:
            print(f"❌ Erro no Telegram: {erro}")

    print(f"✅ Finalizado. {enviadas} ofertas enviadas.")


if __name__ == "__main__":
    asyncio.run(main())
