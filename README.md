# Travel Memory Bot

Приватный Telegram-бот для двух пользователей. Каждый день бот отправляет одно ещё не использованное фото с датой, местом и случайной тёплой фразой.

## Что умеет бот

Администратор видит две кнопки:

- `❤️ Отправить воспоминание` — отправляет следующее фото обоим пользователям и записывает его в историю;
- `🎲 Случайное фото` — отправляет случайное фото только нажавшему и не меняет историю.

Второй пользователь видит только кнопку `🎲 Случайное фото`.

Когда все фотографии будут отправлены, бот напишет:

```text
❤️ Мы посмотрели все наши воспоминания. Пора создавать новые.
```

## Формат фотографий

Название файла должно иметь вид:

```text
YYYY-MM-DD__trip-name__place-name__001.jpg
```

Пример:

```text
2026-09-29__beijing-2026__universal-studios__001.jpg
```

Поддерживаются `.jpg`, `.jpeg`, `.png` и `.webp`.

---

# Локальный запуск

## 1. Распакуй проект

Перейди в папку проекта, где находятся `Dockerfile` и `docker-compose.yml`.

## 2. Создай `.env`

Linux/macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Открой `.env` и заполни:

```env
BOT_TOKEN=токен_бота
ALLOWED_USER_IDS=твой_id,id_второго_пользователя
ADMIN_USER_ID=твой_id
SEND_TIME=09:00
TIMEZONE=Europe/Moscow
DATA_DIR=/app/data
HOST_DATA_DIR=./data
```

`ADMIN_USER_ID` обязательно должен входить в `ALLOWED_USER_IDS`.

## 3. Добавь фотографии

Положи их в:

```text
data/photos/
```

Фразы находятся в:

```text
data/phrases.json
```

## 4. Запусти бота

```bash
docker compose up -d --build
```

Проверь контейнер:

```bash
docker compose ps
```

Посмотри логи:

```bash
docker compose logs -f travel-memory-bot
```

Остановить просмотр логов: `Ctrl+C`. Контейнер продолжит работать.

Остановить бота:

```bash
docker compose down
```

---

# Запуск на VPS без хранения фото в Git

На VPS код и пользовательские данные должны лежать отдельно:

```text
/opt/travel-memory-bot/     # Git-репозиторий
/opt/travel-memory-data/    # фотографии, phrases.json и история отправок
```

Так `git pull` обновляет только код и не касается фотографий.

## 1. Клонируй репозиторий

```bash
cd /opt
git clone URL_РЕПОЗИТОРИЯ travel-memory-bot
cd /opt/travel-memory-bot
```

## 2. Создай внешнюю папку данных

```bash
sudo mkdir -p /opt/travel-memory-data/photos
sudo chown -R "$USER":"$USER" /opt/travel-memory-data
```

## 3. Создай `.env`

```bash
cp .env.example .env
nano .env
```

Укажи:

```env
BOT_TOKEN=токен_бота
ALLOWED_USER_IDS=твой_id,id_второго_пользователя
ADMIN_USER_ID=твой_id
SEND_TIME=09:00
TIMEZONE=Europe/Moscow
DATA_DIR=/app/data
HOST_DATA_DIR=/opt/travel-memory-data
```

Важно:

- `HOST_DATA_DIR` — реальный путь на VPS;
- `DATA_DIR=/app/data` — путь внутри Docker-контейнера;
- менять `DATA_DIR` на `/opt/travel-memory-data` не нужно.

## 4. Загрузи фотографии с Windows

На компьютере открой PowerShell и выполни:

```powershell
scp "C:\путь\к\фотографиям\*" USER@IP_СЕРВЕРА:/opt/travel-memory-data/photos/
```

Пример:

```powershell
scp "C:\Users\Ivan\Pictures\travel-memory\*" root@192.0.2.10:/opt/travel-memory-data/photos/
```

Для вложенных папок используй `-r`:

```powershell
scp -r "C:\Users\Ivan\Pictures\travel-memory\*" root@192.0.2.10:/opt/travel-memory-data/photos/
```

## 5. Проверь фотографии на VPS

```bash
find /opt/travel-memory-data/photos -maxdepth 1 -type f
```

Количество файлов:

```bash
find /opt/travel-memory-data/photos -maxdepth 1 -type f | wc -l
```

## 6. Запусти бота

```bash
cd /opt/travel-memory-bot
docker compose up -d --build
```

При первом запуске контейнер автоматически создаст:

```text
/opt/travel-memory-data/phrases.json
/opt/travel-memory-data/bot.sqlite3
```

Если `phrases.json` уже существует, контейнер его не перезаписывает.

## 7. Проверь, что контейнер видит данные

```bash
docker compose exec travel-memory-bot ls -lah /app/data/photos
```

Проверь логи:

```bash
docker compose logs -f travel-memory-bot
```

---

# Обновление через Git

Фотографии и база истории находятся вне репозитория, поэтому обновление выполняется так:

```bash
cd /opt/travel-memory-bot
git pull
docker compose up -d --build
```

Папка `/opt/travel-memory-data` при этом не удаляется и не изменяется Git.

Проверка после обновления:

```bash
docker compose ps
docker compose logs --tail=100 travel-memory-bot
```

---

# Где хранятся данные

На VPS:

```text
/opt/travel-memory-data/
├── photos/
├── phrases.json
└── bot.sqlite3
```

- `photos/` — личные фотографии;
- `phrases.json` — список случайных подписей;
- `bot.sqlite3` — история уже отправленных фотографий.

Не удаляй `bot.sqlite3`, иначе бот забудет историю и сможет повторно отправлять старые фотографии.
