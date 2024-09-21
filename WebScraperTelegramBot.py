import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import logging

TOKEN = 'BOT_TOKEN'
CHAT_ID = 'CHAT_ID'
bot = telegram.Bot(token=TOKEN)

async def invia_comunicazione(href_circolare, testo_circolare):
    telegram_message = testo_circolare + "\n" + href_circolare
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=telegram_message)

async def main():
    while True:

        #Gestione della pagina web da monitorare
        url_main_circolari = "https://www.nomescuoladacontrollare.edu.it/circolare/"

        try:
            #E' importante gestire la try in quanto possono insorgere molteplici errori, da errore di connessione a errore di timeout.
            #Il programma non deve arrestarsi in caso di errore
            response_main_circolari = requests.get(url_main_circolari)
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"Errore HTTP: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Errore di connessione: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Errore generico nella richiesta: {req_err}")

        if response_main_circolari is not None:
            if response_main_circolari.status_code == 200:
                soup = BeautifulSoup(response_main_circolari.content, 'html.parser')
                articles = soup.find_all(class_='presentation-card-link')
                last_10_articles = articles[-10:]
                for article in last_10_articles:
                    #Le istruzioni interne a questo ciclo vanno verticalizzate per il sito che si sta prendendo in esame
                    href_a = article['href']
                    h2_article = article.find('h2')
                    testo_h2 = h2_article.text.strip()

                    with open('elenco_link_processati.txt', 'a+') as link_file_r:
                        contenuto = link_file_r.read()  # Leggi tutto il contenuto del file

                    if href_a not in contenuto:
                        await invia_comunicazione(href_a,testo_h2)
                        with open('elenco_link_processati.txt', 'a') as link_file_a:
                            link_file_a.write(href_a)

        await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(main())
