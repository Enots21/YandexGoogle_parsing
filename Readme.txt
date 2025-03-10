# Парсинг новостей о вебкам-индустрии

Этот проект представляет собой инструмент для автоматического сбора новостей по запросу "вебкам-индустрия" из двух популярных поисковых систем: **Google News** и **Яндекс.Новости**. Программа парсит заголовки и ссылки на статьи, удаляет дубликаты и возвращает уникальные новости в удобном формате.

---

## Основные функции

### 1. **Парсинг новостей**
   - **Google News**: Программа ищет новости по запросу "вебкам-индустрия" и извлекает заголовки и ссылки на статьи.
   - **Яндекс.Новости**: Аналогично, программа парсит новости из Яндекса, исключая статьи с отметкой "вчера".

### 2. **Решение капчи**
   - Если Яндекс требует ввода капчи, программа автоматически решает её с помощью сервиса **CapMonster Cloud** и продолжает парсинг.

### 3. **Удаление дубликатов**
   - Новости из Google и Яндекс объединяются, после чего удаляются дубликаты. Результат — уникальный список статей.

### 4. **Форматирование результата**
   - Новости выводятся в формате:
     ```
     Новость № 1: Заголовок статьи: Ссылка
     Новость № 2: Заголовок статьи: Ссылка
     ```

---

## Как это работает

1. **Парсинг Google News**:
   - Программа отправляет запрос на Google News и извлекает заголовки и ссылки с помощью библиотеки `BeautifulSoup`.

2. **Парсинг Яндекс.Новости**:
   - Программа отправляет запрос на Яндекс и проверяет наличие капчи. Если капча обнаружена, она решается с помощью CapMonster Cloud.
   - Новости фильтруются: статьи с отметкой "вчера" пропускаются.

3. **Объединение и удаление дубликатов**:
   - Новости из Google и Яндекс объединяются в один список. Дубликаты удаляются с помощью множества (`set`).

4. **Вывод результата**:
   - Уникальные новости нумеруются и выводятся в удобном формате.

---

## Пример вывода

```plaintext
Новость № 1: Вебкам-индустрия в 2023 году: тренды и прогнозы: https://example.com/news1
Новость № 2: Новые технологии в вебкам-бизнесе: https://example.com/news2
Новость № 3: Как начать карьеру в вебкам-индустрии: https://example.com/news3
```

---

## Технологии

- **Python**: Основной язык программирования.
- **BeautifulSoup**: Библиотека для парсинга HTML.
- **Requests**: Библиотека для отправки HTTP-запросов.
- **CapMonster Cloud**: Сервис для автоматического решения капчи.

---

## Как использовать

1. Установите зависимости:
   ```bash
   pip install requests beautifulsoup4
   ```

2. Замените `API_KEY` в функции `check_captcha` на ваш ключ от CapMonster Cloud.

3. Запустите программу:
   ```python
   news = get_webcam_news()
   for item in news:
       print(item)
   ```

---

## Преимущества

- **Автоматизация**: Программа самостоятельно собирает новости, решает капчи и удаляет дубликаты.
- **Гибкость**: Легко адаптируется под другие поисковые системы или запросы.
- **Удобство**: Результат выводится в читаемом формате.

---

## Будущие улучшения

- Добавление поддержки других поисковых систем (например, Bing).
- Интеграция с базой данных для хранения новостей.
- Реализация уведомлений о новых статьях (например, через Telegram Bot).

---

Этот инструмент идеально подходит для мониторинга новостей в нише вебкам-индустрии. Он экономит время и предоставляет актуальную информацию в удобном формате.


Телеграмм бот ===============================

# Telegram Bot для получения новостей о вебкам-индустрии

Этот проект представляет собой Telegram-бота, который помогает пользователям получать актуальные новости о вебкам-индустрии. Бот использует парсинг данных из **Google News** и **Яндекс.Новости**, а также предоставляет удобный интерфейс для взаимодействия через Telegram.

---

## Основные функции

### 1. **Команда `/start`**
   - При запуске бота пользователь получает приветственное сообщение и клавиатуру с двумя кнопками:
     - **"Привет!"**: Бот отвечает приветствием, упоминая имя пользователя.
     - **"Новости"**: Бот выводит список новостей, связанных с вебкам-индустрией.

### 2. **Парсинг новостей**
   - Бот использует функцию `get_webcam_news()`, которая:
     - Ищет новости по запросу "вебкам-индустрия" в Google News и Яндекс.Новости.
     - Удаляет дубликаты и возвращает уникальные новости в формате:
       ```
       Новость № 1: Заголовок статьи: Ссылка
       Новость № 2: Заголовок статьи: Ссылка
       ```

### 3. **Решение капчи**
   - Если Яндекс требует ввода капчи, бот автоматически решает её с помощью сервиса **CapMonster Cloud**.

---

## Как это работает

1. **Запуск бота**:
   - Пользователь отправляет команду `/start`.
   - Бот приветствует пользователя и показывает клавиатуру с кнопками.

2. **Кнопка "Привет!"**:
   - Бот отправляет сообщение с приветствием, используя имя пользователя.

3. **Кнопка "Новости"**:
   - Бот вызывает функцию `get_webcam_news()`, которая:
     - Парсит новости из Google и Яндекс.
     - Удаляет дубликаты.
     - Возвращает список новостей.
   - Бот отправляет каждую новость пользователю в отдельном сообщении.

---

## Технологии

- **Python**: Основной язык программирования.
- **Aiogram**: Библиотека для создания Telegram-ботов.
- **BeautifulSoup**: Библиотека для парсинга HTML.
- **Requests**: Библиотека для отправки HTTP-запросов.
- **CapMonster Cloud**: Сервис для автоматического решения капчи.

---

## Как использовать

1. Установите зависимости:
   ```bash
   pip install aiogram requests beautifulsoup4
   ```

2. Создайте файл `config.py` и добавьте туда ваш токен:
   ```python
   TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"
   ```

3. Запустите бота:
   ```bash
   python bot.py
   ```

4. Взаимодействуйте с ботом через Telegram:
   - Отправьте команду `/start`.
   - Используйте кнопки для получения приветствия или новостей.

---

## Пример взаимодействия

### Пользователь:
```
/start
```

### Бот:
```
Привет! Я ваш бот. Выберите действие:
[Кнопка "Привет!"] [Кнопка "Новости"]
```

### Пользователь:
```
Привет!
```

### Бот:
```
Привет, Иван!
```

### Пользователь:
```
Новости
```

### Бот:
```
Новость № 1: Вебкам-индустрия в 2023 году: тренды и прогнозы: https://example.com/news1
Новость № 2: Новые технологии в вебкам-бизнесе: https://example.com/news2
```

---

## Преимущества

- **Автоматизация**: Бот самостоятельно собирает новости и решает капчи.
- **Удобство**: Новости выводятся в читаемом формате.
- **Гибкость**: Легко адаптируется под другие запросы или поисковые системы.

---
