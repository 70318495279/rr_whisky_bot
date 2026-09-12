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
    url = "https://lista.mercadolivre.com.br/" + quote(BUSCA)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    print(f"🌐 Acessando: {url}")

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print(f"📡 Status Mercado Livre: {response.status_code}")

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    ofertas = []

    # Estrutura atual do Mercado Livre
    itens = soup.select(".poly-card")

    print(f"🔎 Produtos encontrados na página: {len(itens)}")

    for item in itens:

        titulo_elemento = item.select_one(
            ".poly-component__title"
        )

        preco_elemento = item.select_one(
            ".poly-price__current .andes-money-amount__fraction"
        )

        link_elemento = item.select_one(
            "a.poly-component__title"
        )

        if not titulo_elemento:
            continue

        if not preco_elemento:
            continue

        if not link_elemento:
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

        ofertas.append({
            "titulo": titulo,
            "preco": preco,
            "link": link
        })

        if len(ofertas) >= 5:
            break

    return ofertas


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

    print("🥃 RR WHISKY BOT")
    print("🔎 Procurando ofertas de whisky...")

    ofertas = buscar_ofertas()

    if not ofertas:
        print("⚠️ Nenhuma oferta encontrada.")
        return

    print(f"✅ {len(ofertas)} ofertas encontradas!")

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
                f"📨 Oferta enviada: {oferta['titulo']}"
            )

            await asyncio.sleep(3)

        except Exception as erro:

            print(
                f"❌ Erro ao enviar oferta: {erro}"
            )

    print(
        f"✅ Finalizado! {enviadas} ofertas enviadas para o Telegram."
    )


if __name__ == "__main__":
    asyncio.run(main())
