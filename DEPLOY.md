# Деплой на Render (бесплатно)

## Шаг 1: Подготовка
1. Создай аккаунт на [render.com](https://render.com/)
2. Создай аккаунт на [github.com](https://github.com/) (если нет)
3. Загрузи папку `tg-course-bot` на GitHub

## Шаг 2: Создание бота
1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Напиши `/newbot`, выбери имя `GlowUp Center`
3. Скопируй токен бота

## Шаг 3: NOWPayments
1. Регистрируйся на [nowpayments.io](https://nowpayments.io/)
2. Перейди в API Keys -> создай ключ
3. Сохрани API ключ

## Шаг 4: Деплой на Render
1. На Render нажми New -> Web Service
2. Подключи свой GitHub репозиторий
3. Настройки:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
4. Добавь переменные окружения из `.env.example`:
   - BOT_TOKEN
   - NOWPAYMENTS_API_KEY
   - ADMIN_ID (твой Telegram ID, можно узнать у @userinfobot)
   - Остальное можно оставить как есть для старта

## Шаг 5: Добавить инструкции
После первого запуска на локалке или через консоль можно запустить `add_instruction.py` чтобы добавить инструкцию.

## Готово
Бот будет работать 24/7 бесплатно.
