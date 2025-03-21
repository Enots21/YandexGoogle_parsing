import logging
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API-ключ от RuCaptcha
API_KEY = "44e6ce6ee80664a161334a32a10782e8"

# Настройка Selenium (headless-режим)
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # Отключаем GPU
chrome_options.add_argument("--no-sandbox")  # Отключаем sandbox
chrome_options.add_argument("--disable-dev-shm-usage")  # Решает проблемы с памятью
chrome_options.add_argument("--window-size=1920,1080")  # Устанавливаем размер окна

# Автоматическая установка и настройка ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def solve_yandex_captcha(api_key, site_key, page_url):
    """
    Решение Яндекс SmartCaptcha через RuCaptcha с использованием sitekey.
    """
    create_task_url = "https://rucaptcha.com/in.php"
    params = {
        "key": api_key,
        "method": "yandex",
        "sitekey": site_key,
        "pageurl": page_url,
        "json": 1
    }

    try:
        response = requests.post(create_task_url, data=params)
        response.raise_for_status()
        task_response = response.json()
        if task_response.get("status") != 1:
            logging.error(f"Ошибка: {task_response.get('request')}")
            return None

        task_id = task_response.get("request")
        logging.info(f"Задача создана, ID: {task_id}")

        get_result_url = "https://rucaptcha.com/res.php"
        while True:
            time.sleep(5)
            result_params = {
                "key": api_key,
                "action": "get",
                "id": task_id,
                "json": 1
            }

            result_response = requests.get(get_result_url, params=result_params)
            result_response.raise_for_status()
            result_data = result_response.json()

            if result_data.get("status") == 1:
                return result_data.get("request")
            elif result_data.get("request") == "CAPCHA_NOT_READY":
                logging.info("Капча ещё не решена, ожидаем...")
            else:
                logging.error(f"Ошибка: {result_data.get('request')}")
                return None
    except requests.RequestException as e:
        logging.error(f"Ошибка при работе с API RuCaptcha: {e}")
        return None

def fetch_yandex_news(query):
    """
    Получение новостей с Яндекса с использованием Selenium.
    """
    encoded_query = urllib.parse.quote(query)
    url = f"https://yandex.ru/search?text={encoded_query}&lr=45&within=77"
    logging.info(f"Запрос к URL: {url}")
    try:
        driver.get(url)
        logging.info("Страница успешно загружена")

        # Ожидание появления элементов
        WebDriverWait(driver, 10).until(  # Увеличьте таймаут до 20 секунд
            EC.presence_of_element_located((By.CSS_SELECTOR, '.serp-item'))
        )
        logging.info("Элементы на странице загружены")

        # Получаем HTML-содержимое страницы
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        with open('html.html', 'w', encoding='utf-8') as file:
            file.write(html_content)

        # Проверка на капчу
        captcha_div = driver.find_elements(By.CSS_SELECTOR, '.smart-captcha')
        if captcha_div:
            logging.info("Обнаружена капча, извлекаем sitekey...")
            sitekey = captcha_div[0].get_attribute('data-sitekey')
            if sitekey:
                logging.info(f"Извлечённый sitekey: {sitekey}")
            else:
                logging.error("Не удалось извлечь sitekey.")
                return []

            # Решаем капчу
            captcha_token = solve_yandex_captcha(API_KEY, sitekey, url)
            if not captcha_token:
                logging.error("Не удалось решить капчу")
                return []

            # Отправляем решение капчи
            driver.execute_script(f"document.querySelector('input[name=\"smart-token\"]').value = '{captcha_token}';")
            driver.execute_script("document.forms[0].submit();")

            # Ожидание загрузки новой страницы
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.serp-item'))
            )
            logging.info("Капча успешно решена, страница перезагружена")
        else:
            logging.info("Капча не обнаружена")

        news_items = soup.find_all('li', class_='serp-item serp-item_card')

        news_list = []

        for item in news_items:
            # Найти ссылку на новость
            link = item.find('a', class_='Link Link_theme_normal OrganicTitle-Link organic__url link')
            if link:
                href = link['href']  # Получить URL
                title = link.text  # Получить текст ссылки (заголовок)
                news_list.append((title, href))
                print(f"Заголовок: {title}")
                print(f"Ссылка: {href}")

            else:
                print("Ссылка не найдена в этой карточке.")
        return news_list

    except Exception as e:
        logging.error(f"Ошибка при получении новостей: {e}")

    finally:
        # Закрываем браузер
        driver.quit()