import logging

import requests
from bs4 import BeautifulSoup


# Функция для поиска новостей на Google News
def fetch_google_news(query):
    """
    Получает новости из Google News по заданному запросу.
    Возвращает список кортежей (заголовок, ссылка, дата).
    """
    # Формируем URL для запроса (qdr:d — за последний день)
    url = f"https://www.google.com/search?q={query}&tbm=nws&tbs=qdr:d"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "DNT": "1",
    }

    try:
        # Выполняем GET-запрос
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'

        # Проверяем статус ответа
        if response.status_code != 200:
            logging.error(f"Ошибка: статус код {response.status_code}")
            return []

        # Парсим HTML-страницу
        soup = BeautifulSoup(response.text, 'html.parser')

        with open('google.html', 'a', encoding='utf-8') as file:
            file.write(str(soup))

        # Сохраняем HTML для отладки (опционально)

        news_articles = soup.find_all('div', class_='SoAPf')  # Пример класса для контейнера новости
        articles = []
        if news_articles:
            for article in news_articles:
                # Извлекаем источник
                news_source = article.find('div', class_='MgUUmf NUnG9d')
                if news_source:
                    news_source = news_source.text.strip()
                else:
                    news_source = "Источник не найден"

                # Извлекаем ссылку
                try:
                    news_url = article.find_parent('a')['href']  # Ищем ссылку в родительском теге <a>
                except (TypeError, KeyError):  # Обрабатываем возможные ошибки, если 'a' не найден или не имеет 'href'
                    news_url = "Ссылка не найдена"

                # Извлекаем название новости
                news_name = article.find('div', class_='n0jPhd ynAwRc MBeuO nDgy9d')
                if news_name:
                    news_name = news_name.text.strip()
                else:
                    news_name = "Название не найдено"

                # Извлекаем дату публикации
                news_date = article.find('span', class_='OSrXXb rbYSKb LfVVr')
                if news_date:
                    news_date = news_date.text.strip()  # Извлекаем текст даты
                else:
                    news_date = "Дата не найдена"

                # Логируем и добавляем данные в список
                logging.info(f"Новость: {news_name}, Ссылка: {news_source}, Дата: {news_date}")
                articles.append((news_name, news_source, news_url, news_date))
            return articles
        else:
            logging.info("Новостей не найдено")
            print("Новостей нету Google News")
            return False
    except Exception as e:
        logging.error(f"Ошибка при получении новостей: {str(e)}")