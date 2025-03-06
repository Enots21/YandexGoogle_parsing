import requests
from bs4 import BeautifulSoup
import logging
import time
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV2ProxylessRequest

# Функция для решения капчи с помощью CapMonster Cloud
def check_captcha(url, website_key, api_key):
    # URL API CapMonster Cloud
    api_url = "https://api.capmonster.cloud/createTask"

    # JSON-запрос для создания задачи
    payload = {
        "clientKey": api_key,
        "task": {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": url,
            "websiteKey": website_key
        }
    }

    # Отправляем запрос на создание задачи
    response = requests.post(api_url, json=payload) # Используем json
    if response.status_code != 200: # Если статус код не равен 200, то выбрасываем исключение
        raise Exception(f"Ошибка при создании задачи: {response.status_code}, {response.text}")

    # Получаем ID задачи
    task_id = response.json().get("taskId") # Получаем ID задачи из ответа
    if not task_id: # Если ID задачи не получен, то выбрасываем исключение
        raise Exception("Не удалось получить taskId из ответа")

    # Ожидаем решения капчи
    result_url = "https://api.capmonster.cloud/getTaskResult"
    while True:
        time.sleep(5)  # Ожидаем 5 секунд перед проверкой
        result_response = requests.post(result_url, json={"clientKey": api_key, "taskId": task_id})
        if result_response.status_code != 200:
            raise Exception(f"Ошибка при получении результата: {result_response.status_code}, {result_response.text}")

        result_data = result_response.json()
        if result_data.get("status") == "ready":
            # Возвращаем решение капчи
            return result_data.get("solution", {}).get("gRecaptchaResponse")
        elif result_data.get("status") == "processing":
            continue
        else:
            raise Exception(f"Ошибка в статусе задачи: {result_data.get('status')}")

def fetch_google_news(query): # Функция для поиска новостей на Google News
    url = f"https://www.google.com/search?q={query}&tbm=nws&tbs=qdr:d"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Ошибка: статус код {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    articles_google = []
    for item in soup.find_all('div', class_='vvjwJb'):  # Убрали точку перед классом
        title = item.text  # Получаем текст заголовка
        link = item.find_parent('a')['href']  # Ищем ссылку в родительском теге <a>
        if title and link:
            logging.info(f"Новость присутвует")  # Логируем заголовок
            articles_google.append((title, link))
        else:
            logging.info(f"Новость отсутствует")  # Логируем отсутствие новости

    return articles_google

# Функция для поиска новостей на Яндексе
def fetch_yandex_news(query):
    url = f"https://yandex.ru/search/?text={query}&lr=45&clid=10472851-77&win=683&within=77"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.example.com"
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"Ошибка: статус код {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Проверка на наличие капчи
    if soup.find('h2', class_='CheckboxCaptcha'):
        print("Обнаружена капча, решаем...")
        captcha_solution = check_captcha(url, "6Lcg7CMUAAAAANphynKgn9YAgA4tQ2KI_iqRyTwd")  # Замените на актуальный ключ сайта
        if captcha_solution:
            # Повторный запрос с решением капчи
            data = {
                'g-recaptcha-response': captcha_solution
            }
            response = requests.post(url, headers=headers, data=data)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
        else:
            print("Не удалось решить капчу")
            return

    # Парсинг новостей
    articles = []
    for item in soup.find_all('a', class_='link serp-item__title-link'):
        # Проверяем, есть ли отметка "вчера" в родительском блоке
        if item.find_parent('div', class_='serp-item__extra'):
            extra_div = item.find_parent('div', class_='serp-item__extra')
            if extra_div and extra_div.find('a', text='вчера'):
                logging.info(f"Новость пропущена: найдена отметка 'вчера'")
                continue  # Пропускаем эту новость

        title = item.text.strip()  # Извлекаем текст заголовка и убираем лишние пробелы
        link = item['href']  # Извлекаем ссылку напрямую из элемента <a>
        if title and link:
            logging.info(f"Новость присутствует: {title}")
            articles.append((title, link))
        else:
            logging.info("Новость отсутствует")

    return articles

# Функция для получения новостей из вебкам-индустрии
def get_webcam_news():
    query = "вебкам-индустрия"
    google_news = fetch_google_news(query)  # Предполагаем, что эта функция возвращает список кортежей (заголовок, ссылка)
    yandex_news = fetch_yandex_news(query)  # Предполагаем, что эта функция возвращает список кортежей (заголовок, ссылка)
    all_articles = google_news + yandex_news

    # Удаляем дубликаты
    unique_articles = []
    seen = set()  # Множество для отслеживания уже добавленных новостей
    for article in all_articles:
        if article not in seen:  # Проверяем, есть ли новость уже в множестве
            unique_articles.append(article)
            seen.add(article)

    # Формируем список новостей
    news = []
    if unique_articles:
        for bnew, (articl, links) in enumerate(unique_articles, start=1):
            news.append(f"Новость № {bnew}: {articl}: {links}")

    # Печатаем результат
    return news