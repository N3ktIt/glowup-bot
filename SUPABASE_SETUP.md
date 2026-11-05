# Настройка Supabase (бесплатно)

## 1) Создай проект
1. Зайди на [supabase.com](https://supabase.com/) и зарегистрируйся
2. Нажми **New project**
3. Выбери организацию, задай имя проекта (например `glowup-bot`) и пароль для базы
4. Выбери регион ближе к тебе (Europe) и нажми **Create new project**

## 2) Получи строку подключения
1. В проекте открой **Project Settings** (шестерёнка слева) -> **Database**
2. Найди раздел **Connection string** -> вкладка **URI** (или Session pooler / Transaction pooler)
3. Скопируй строку вида:
   `postgresql://postgres.[ref]:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres`
4. Замени `[YOUR-PASSWORD]` на пароль, который ты задал при создании проекта

## 3) Добавь в Render
1. В Render открой сервис `glowup-bot` -> **Environment**
2. Добавь/измени переменную:
   - `DATABASE_URL` = твоя строка подключения из Supabase
3. Удали старую переменную `DATABASE_NAME`, если она есть
4. Сохрани и сделай **Deploy latest commit**

## Готово
После этого инструкции, покупки и настройки языка будут сохраняться навсегда.
