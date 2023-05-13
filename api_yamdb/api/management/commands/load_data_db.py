import csv
import os
import sys

from django.core.management.base import BaseCommand

from reviews.models import (
    Category, Comment, Genre, GenreTitle, Review, Title, User)

FILE_NAMES_MODELS = {
    'category.csv': Category,
    'genre.csv': Genre,
    'users.csv': User,
    'titles.csv': Title,
    'genre_title.csv': GenreTitle,
    'review.csv': Review,
    'comments.csv': Comment,
}
HOME_DIR = os.getcwd()
FILES_DIR = os.path.join(HOME_DIR, 'static', 'data')


def lost_files(files, path):
    """Проверяет, есть ли потерянные файлы."""
    res = []
    files_in_dir = os.listdir(path)
    for file in files:
        if file not in files_in_dir:
            res.append(file)
    return res


def create_obj(data, model):
    try:
        model.objects.create(**data)
    except Exception as error:
        print(f'Ошибка записи в БД: {error}')


def load_row_to_bd(row, model):
    if model == Title:
        pass
        data = {
            'id': row['id'],
            'name': row['name'],
            'year': row['year'],
            'category': Category.objects.get(id=row['category'])
        }
        create_obj(data, model)

    elif model == GenreTitle:
        data = {
            'id': row['id'],
            'title_id': Title.objects.get(id=row['title_id']),
            'genre_id': Genre.objects.get(id=row['genre_id'])
        }
        create_obj(data, model)
    elif model == Review:
        data = {
            'id': row['id'],
            'title': Title.objects.get(id=row['title_id']),
            'text': row['text'],
            'author': User.objects.get(id=row['author']),
            'score': row['score'],
            'pub_date': row['pub_date']
        }
        create_obj(data, model)
    elif model == Comment:
        data = {
            'id': row['id'],
            'review': Review.objects.get(id=row['review_id']),
            'text': row['text'],
            'author': User.objects.get(id=row['author']),
            'pub_date': row['pub_date']
        }
        create_obj(data, model)
    else:
        create_obj(row, model)


class Command(BaseCommand):
    help = 'Для загрузки данных в БД'

    def handle(self, *args, **options):
        if (files := lost_files(FILE_NAMES_MODELS.keys(), FILES_DIR)):
            print(f"Отсутствуют необходимые файлы: "
                  f"{', '.join(x for x in files)}.")
            sys.exit('Работа завершена с ошибками.')

        for file_name, model in FILE_NAMES_MODELS.items():
            file = os.path.join(FILES_DIR, file_name)
            print(f'Запись из файла: {file_name}')
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    # print(rows)
                    for row in reader:
                        load_row_to_bd(row, model)

            except Exception as error:
                print(
                    f'Ошибка чтения файла {file_name} и записи в БД: {error}')
