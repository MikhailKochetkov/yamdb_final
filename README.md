![api_yamdb workflow](https://github.com/MikhailKochetkov/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master&event=push)

## Описание
Сайт является базой данных отзывов о фильмах, книгах и музыке.
Пользователи могут оставлять рецензии на произведения, а также комментировать эти рецензии.
Администраторы ресурса добавляет новые произведения и категории (книга, фильм, музыка и т.д.)
Также присутствует файл docker-compose, позволяющий , быстро развернуть контейнер базы данных (PostgreSQL), контейнер проекта django + gunicorn и контейнер nginx

## Инструкция по запуску

Для запуска необходимо из корневой папки проекта ввести в консоль  команду:
```
sudo docker-compose up --build
```
Получаем id контейнера
```
sudo docker container ls
```
Запускаем контейнер
```
sudo docker exec -it <CONTAINER ID> sh
```
Делаем миграцию БД и сбор статики
```
python3 manage.py migrate
python3 manage.py collectstatic
```

## Как пользоваться

После запуска проекта подробную инструкцию можно будет посмотреть по адресу http://<IP-адрес сервера>/static/redoc/

## Автор

* **Михаил Кочетков** - https://github.com/MikhailKochetkov
