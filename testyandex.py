import logging
import requests
from bs4 import BeautifulSoup
import time
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API-ключ от RuCaptcha
API_KEY = "api-key"

# Заголовки для запросов
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://yandex.ru/",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Максимальное количество попыток
MAX_RETRIES = 6

# Задержка между попытками (в секундах)
RETRY_DELAY = 20


def solve_yandex_captcha(api_key, page_url):
    """
    Решение Яндекс SmartCaptcha через RuCaptcha.
    """
    # URL для создания задачи в RuCaptcha
    create_task_url = "https://rucaptcha.com/in.php"

    # Параметры для создания задачи
    params = {
        "key": api_key,
        "method": "yandex",  # Метод для Яндекс SmartCaptcha
        "pageurl": page_url,  # URL страницы с капчей
        "json": 1  # Получить ответ в формате JSON
    }

    # Отправляем запрос на создание задачи
    response = requests.post(create_task_url, data=params)
    if response.status_code != 200:
        logging.error(f"Ошибка при создании задачи: {response.status_code}, {response.text}")
        return None

    # Парсим JSON-ответ
    task_response = response.json()
    if task_response.get("status") != 1:
        logging.error(f"Ошибка: {task_response.get('request')}")
        return None

    # Получаем ID задачи
    task_id = task_response.get("request")
    logging.info(f"Задача создана, ID: {task_id}")

    # URL для получения результата
    get_result_url = "https://rucaptcha.com/res.php"

    # Ожидаем решения капчи
    while True:
        time.sleep(5)  # Пауза перед повторным запросом
        result_params = {
            "key": api_key,
            "action": "get",
            "id": task_id,
            "json": 1
        }

        result_response = requests.get(get_result_url, params=result_params)
        if result_response.status_code != 200:
            logging.error(f"Ошибка при получении результата: {result_response.status_code}, {result_response.text}")
            return None

        result_data = result_response.json()
        if result_data.get("status") == 1:
            # Капча решена, возвращаем токен
            return result_data.get("request")
        elif result_data.get("request") == "CAPCHA_NOT_READY":
            logging.info("Капча ещё не решена, ожидаем...")
        else:
            logging.error(f"Ошибка: {result_data.get('request')}")
            return None


def fetch_yandex_news(query, retries=MAX_RETRIES):
    """
    Получение новостей с Яндекса с обработкой капчи и повторными попытками.
    """
    url = f"https://yandex.ru/search/?text={query}&lr=45&clid=10472851-77&win=683&within=77"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://yandex.ru/",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    for attempt in range(retries):
        try:
            # Случайная пауза перед запросом
            time.sleep(random.uniform(5, 25))

            # Использование сессии для сохранения куки
            session = requests.Session()
            response = session.get(url, headers=headers)
            response.encoding = 'utf-8'  # Указываем кодировку

            if response.status_code != 200:
                logging.error(f"Ошибка: статус код {response.status_code}")
                raise Exception(f"Ошибка HTTP: {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')

            # Сохраняем HTML для отладки
            with open('debug.html', 'w', encoding='utf-8') as file:
                file.write(str(soup))

            # Проверка на капчу
            captcha_form = soup.find('form', id='checkbox-captcha-form')
            if captcha_form:
                logging.info("Обнаружена капча, решаем...")

                # Решаем капчу через RuCaptcha
                captcha_token = solve_yandex_captcha(API_KEY, url)
                if not captcha_token:
                    logging.error("Не удалось решить капчу")
                    raise Exception("Не удалось решить капчу")

                # Отправляем решение капчи на сервер
                captcha_response = captcha_token
                response = session.post(url, headers=headers, data={'smart-token': captcha_response})

                if response.status_code != 200:
                    logging.error(f"Ошибка при отправке решения капчи: статус код {response.status_code}")
                    raise Exception(f"Ошибка HTTP: {response.status_code}")

                soup = BeautifulSoup(response.text, 'html.parser')
            else:
                logging.info("Капча не обнаружена")

            # Парсинг новостей
            articles = []
            for item in soup.find_all('a', class_='link serp-item__title-link'):
                # Проверяем, есть ли отметка "вчера" в родительском блоке
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

        except Exception as e:
            logging.error(f"Попытка {attempt + 1} из {retries} не удалась: {e}")
            if attempt < retries - 1:
                logging.info(f"Повторная попытка через {RETRY_DELAY} секунд...")
                time.sleep(RETRY_DELAY)
            else:
                logging.error("Все попытки завершились неудачей.")
                return []


if __name__ == "__main__":
    # Получение новостей с Яндекса
    query = "вебкам-индустрия"
    news = fetch_yandex_news(query)

    # Выводим результаты
    for title, link in news:
        print(f"Заголовок: {title}")
        print(f"Ссылка: {link}")
        print()