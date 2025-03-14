import logging

from google_news import fetch_google_news
from yandex_news import fetch_yandex_news




def fetch_news():
    """
    Получает новости из Google News и Yandex News и объединяет результаты.
    Возвращает список новостей или пустой список, если ничего не найдено.
    """
    search = 'вебкам-индустрия'
    google_news_results = fetch_google_news(search)
    yandex_news_results = fetch_yandex_news(search)

    # Преобразуем None в пустой список, чтобы избежать ошибок при сложении
    if google_news_results is None:
        google_news_results = []
    if yandex_news_results is None:
        yandex_news_results = []

    combined_results = google_news_results + yandex_news_results

    if combined_results:
        logging.info(f'Найдено новостей: {len(combined_results)}')
        return combined_results
    else:
        logging.info('Ничего не найдено')


