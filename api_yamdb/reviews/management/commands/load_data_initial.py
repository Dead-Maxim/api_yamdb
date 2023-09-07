import csv
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title


User = get_user_model()

class Command(BaseCommand):
    """Заливка инит-данных из статичных файлов

    Файлы ищутся в директории {project}/static/data.
    База чистится в определённой последовательности
    согласно реляционной логике
    (отказ от зачистки - флаг --need_no_purge при вызове команды),
    далее заполняется (upsert-ом), тоже в определённом порядке,
    данными из файлов.
    При заливке из файлов данные валидизируются и санитайзятся
    согласно семантике проекта, моделей и т.п.
    """

    required_files = [
        'comments.csv',
        'review.csv',
        'genre_title.csv',
        'titles.csv',
        'genre.csv',
        'category.csv',
        'users.csv',
    ]

    help = 'Uploads initial data for project developement and testing'

    def add_arguments(self, parser):
        """Аргументы запуска из командной строки

        --need_no_purge флаг Не чистить бд перед заливкой.
        По умолчанию False, то есть команда (load_data_initial)
        почистит бд грамотно ото всего, кроме пользователей
        с флагом supervisor.
        В любом случае далее заливка будет производиться в режиме
        upsert (отсутствующее создаётся, имеющееся обновляется)
        """
        parser.add_argument(
            '--need_no_purge',
            action='store_true',
            dest='need_no_purge',
            default=False,
            help='Не зачищать бд перед наполнением',
        )

    def handle(self, *args, **options):

        self.stdout.write('\n--need_no_purge: [' + str(options['need_no_purge']) + ']\n')

        self.check_csv_files()

        if not options['need_no_purge']:
            self.purge_db()

        self.load_db(options['need_no_purge'])

    def check_csv_files(self):
        """Check csv files presence"""

        self.stdout.write('\nBASE_DIR: [' + str(settings.BASE_DIR) + ']\n')

        csv_dir = str(settings.BASE_DIR) + '/static/data'
        dir_exists_and_is_dir = os.path.isdir(csv_dir)

        if not dir_exists_and_is_dir:
            raise CommandError(
                'Data files directory "%s" does not exist' % csv_dir)
        else:
            self.stdout.write(
                'Data files directory "%s" exists' % csv_dir)

        for file_name in self.required_files:
            file_path = csv_dir + '/' + file_name
            file_exists_and_is_file = os.path.isfile(file_path)
            if not file_exists_and_is_file:
                raise CommandError(
                    'Data file "%s" does not exist' % file_path)
            else:
                self.stdout.write(
                    'Data file "%s" exists' % file_path)


    def purge_db(self):
        """Зачистка бд

        Чистим всё в обратном порядке (словари последними),
        кроме суперюзеров.

        Последовательность важна!

        Каждую модель чистим индивидуальным блоком кода,
        на всякий случай без типового цикла,
        ибо всегда возможны тонкости, возможно в будущем.

        Удаляем без truncate-ов: должны отрабатывать констрайнты.
        """

        Comment.objects.all().delete()
        self.stdout.write('Comment model is purged')

        Review.objects.all().delete()
        self.stdout.write('Review model is purged')

        GenreTitle.objects.all().delete()
        self.stdout.write('GenreTitle model is purged')

        Title.objects.all().delete()
        self.stdout.write('Title model is purged')

        Genre.objects.all().delete()
        self.stdout.write('Genre model is purged')

        Category.objects.all().delete()
        self.stdout.write('Category model is purged')

        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('User model (is_superuser=False) is purged')

    def load_db(self, need_no_purge):
        """Заливка данных из csv-шек в бд

        Льём строго в определённом порядке (от юзверей и словарей до комментов).
        Юзверей upsert-им в любом случае, всё остальное - insert
        при need_no_purge == False и insert при True.
        """

        # Users
        pass

        # Category
        if (need_no_purge):
            pass
        else:
            pass

        # Genre
        if (need_no_purge):
            pass
        else:
            pass

        # Title
        if (need_no_purge):
            pass
        else:
            pass

        # GenreTitle
        if (need_no_purge):
            pass
        else:
            pass

        # Review
        if (need_no_purge):
            pass
        else:
            pass

        # Comment
        if (need_no_purge):
            pass
        else:
            pass
