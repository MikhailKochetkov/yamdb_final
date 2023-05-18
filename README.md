![api_yamdb workflow](https://github.com/MikhailKochetkov/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master&event=push)

## Описание
Сайт является базой данных отзывов о фильмах, книгах и музыке.
Пользователи могут оставлять рецензии на произведения, а также комментировать эти рецензии.
Администраторы ресурса добавляет новые произведения и категории (книга, фильм, музыка и т.д.)
Также присутствует файл docker-compose, позволяющий , быстро развернуть контейнер базы данных (PostgreSQL), контейнер проекта django + gunicorn и контейнер nginx

### Как запустить проект:

Клонируем репозиторий:
```bash
git clone git@github.com:MikhailKochetkov/yamdb_final.git
```

Создаем и активируем виртуальное окружение:
```bash
python -m venv venv
source /venv/Scripts/activate
python -m pip install --upgrade pip
```

Ставим зависимости из requirements.txt:
```bash
pip install -r requirements.txt
```

Переходим в папку с файлом docker-compose.yaml:
```bash
cd infra
```

Поднимаем контейнеры:
```bash
docker-compose up -d --build
```

Выполняем миграции:
```bash
docker-compose exec web python manage.py makemigrations reviews
```
```bash
docker-compose exec web python manage.py migrate
```

Создаем суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

Србираем статику:
```bash
docker-compose exec web python manage.py collectstatic --no-input
```

Создаем дамп базы данных (нет в текущем репозитории):
```bash
docker-compose exec web python manage.py dumpdata > dumpPostrgeSQL.json
```

Останавливаем контейнеры:
```bash
docker-compose down -v
```

### Шаблон наполнения .env (не включен в текущий репозиторий) расположенный по пути infra/.env.sample

### Документация API YaMDb
Документация доступна по эндпойнту: http://51.250.6.237/redoc/

## Автор

* **Михаил Кочетков** - https://github.com/MikhailKochetkov
