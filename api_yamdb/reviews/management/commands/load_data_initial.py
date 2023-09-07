import csv
import os
import uuid

from dateutil import parser as dateutil_parser
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

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

        self.stdout.write(
            '--need_no_purge: [' + str(options['need_no_purge']) + ']')
        self.stdout.write('BASE_DIR: [' + str(settings.BASE_DIR) + ']')

        self.stdout.write('\ncheck_csv_files:')
        self.check_csv_files()

        if not options['need_no_purge']:
            self.stdout.write('\npurge_db:')
            self.purge_db()

        self.stdout.write('\nload_db:')
        self.load_db(options['need_no_purge'])

    def check_csv_files(self):
        """Check csv files presence"""

        csv_dir = str(settings.BASE_DIR) + '/static/data'
        dir_exists_and_is_dir = os.path.isdir(csv_dir)

        if not dir_exists_and_is_dir:
            raise CommandError(
                'Data files directory "%s" does not exist' % csv_dir)
        self.stdout.write(
            'Data files directory "%s" exists' % csv_dir)

        for file_name in self.required_files:
            file_path = csv_dir + '/' + file_name
            file_exists_and_is_file = os.path.isfile(file_path)
            if not file_exists_and_is_file:
                raise CommandError(
                    'Data file "%s" does not exist' % file_path)
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

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            user = None

        return user

    def get_category(self, category_id):
        try:
            category = Category.objects.get(pk=category_id)
        except ObjectDoesNotExist:
            category = None

        return category

    def get_title(self, title_id):
        try:
            title = Title.objects.get(pk=title_id)
        except ObjectDoesNotExist:
            title = None

        return title

    def get_genre(self, genre_id):
        try:
            genre = Genre.objects.get(pk=genre_id)
        except ObjectDoesNotExist:
            genre = None

        return genre

    def get_genre_title(self, id):
        try:
            gt = GenreTitle.objects.get(pk=id)
        except ObjectDoesNotExist:
            gt = None

        return gt

    def get_review(self, id):
        try:
            review = Review.objects.get(pk=id)
        except ObjectDoesNotExist:
            review = None

        return review

    def get_comment(self, id):
        try:
            comment = Comment.objects.get(pk=id)
        except ObjectDoesNotExist:
            comment = None

        return comment

    def load_db_users(self, csv_dir, need_no_purge):
        """Заливает пользоваетелей из csv

        Ожидает, что есть первая строка с заголовками
        'id', 'username', 'email', 'role', 'bio',
        'first_name', 'last_name',
        пропускает её

        TODO: buckets, need_no_purge
        """

        self.stdout.write('load_db: Users:')
        with open(csv_dir + '/users.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(csvreader, None)
            for row in csvreader:
                id = int(row[0])
                username = row[1]
                email = row[2]
                role = row[3]
                if role not in ('user', 'moderator', 'admin',):
                    role = 'user'
                bio = row[4]
                first_name = row[5]
                last_name = row[6]

                user = self.get_user(id)
                if user is None:
                    password = uuid.uuid4().__str__()
                    try:
                        User.objects.create(
                            id=id,
                            username=username,
                            email=email,
                            password=password,
                            role=role,
                            bio=bio,
                            first_name=first_name,
                            last_name=last_name
                        )
                        self.stdout.write(f'User: {username}: created')
                    except Exception:
                        self.stdout.write(f'error creating'
                                          f'User: {username}')
                else:
                    user.username = username
                    user.email = email
                    user.role = role
                    user.bio = bio
                    user.first_name = first_name
                    user.last_name = last_name
                    try:
                        user.save()
                        self.stdout.write(f'User: {username}: updated')
                    except Exception:
                        self.stdout.write(f'error updating'
                                          f'User: {username}')

    def load_db_categories(self, csv_dir, need_no_purge):
        """Заливает категории из csv

        Ожидает, что есть первая строка с заголовками
        id, name, slug,
        пропускает её

        TODO: buckets, need_no_purge
        """

        self.stdout.write('load_db: Category:')
        with open(csv_dir + '/category.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(csvreader, None)
            for row in csvreader:
                id = int(row[0])
                name = row[1]
                slug = row[2]
                category = self.get_category(id)
                if category is None:
                    try:
                        Category.objects.create(
                            pk=id,
                            name=name,
                            slug=slug
                        )
                        self.stdout.write(f'Category: {id}: created ({name})')
                    except Exception:
                        self.stdout.write(f'error creating'
                                          f'Category {id}: {name}')
                else:
                    category.name = name
                    category.slug = slug
                    try:
                        category.save()
                        self.stdout.write(f'Category: {id}: updated ({name})')
                    except Exception:
                        self.stdout.write(f'error updating'
                                          f'Category {id}: {name}')

    def load_db_genres(self, csv_dir, need_no_purge):
        """Заливает жанры из csv

        Ожидает, что есть первая строка с заголовками
        id, name, slug,
        пропускает её

        TODO: buckets, need_no_purge
        """

        self.stdout.write('load_db: Genre:')
        with open(csv_dir + '/genre.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(csvreader, None)
            for row in csvreader:
                id = int(row[0])
                name = row[1]
                slug = row[2]

                genre = self.get_genre(id)
                if genre is None:
                    try:
                        Genre.objects.create(
                            pk=id,
                            name=name,
                            slug=slug
                        )
                        self.stdout.write(
                            f'Genre: {id}: created ({name})')
                    except Exception:
                        self.stdout.write(f'error creating'
                                          f'Genre {id}: {name}')
                else:
                    genre.name = name
                    genre.slug = slug
                    try:
                        genre.save()
                        self.stdout.write(
                            f'Genre: {id}: updated ({name})')
                    except Exception:
                        self.stdout.write(f'error updating'
                                          f'Genre {id}: {name}')

    def load_db_one_title(self, row):
        id = int(row[0])
        name = row[1]
        year = int(row[2])
        if year < 1:
            year = 1
        category_id = int(row[3])

        category = self.get_category(category_id)
        if category is None:
            self.stdout.write(
                f'invalid category_id: {category_id}: '
                f'skipping record'
            )
            return

        title = self.get_title(id)
        if title is None:
            try:
                Title.objects.create(
                    pk=id,
                    name=name,
                    year=year,
                    category=category
                )
                self.stdout.write(f'Title: {id}: created ({name})')
            except Exception:
                self.stdout.write(
                    f'error creating Title: {id} ({name}): '
                    f'skipping record'
                )
        else:
            title.name = name
            title.year = year
            title.category = category
            try:
                title.save()
                self.stdout.write(f'Title: {id}: updated ({name})')
            except Exception:
                self.stdout.write(
                    f'error creating Title: {id} ({name}): '
                    f'skipping record'
                )

    def load_db_titles(self, csv_dir, need_no_purge):
        """Заливает произведения из csv

        Ожидает, что есть первая строка с заголовками
        id, name, year, category,
        пропускает её

        TODO: buckets, need_no_purge
        """

        self.stdout.write('load_db: Title:')
        with open(csv_dir + '/titles.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(csvreader, None)
            for row in csvreader:
                self. load_db_one_title(row)

    def load_db_one_genre_title(self, row):
        id = int(row[0])
        title_id = int(row[1])
        genre_id = int(row[2])

        title = self.get_title(title_id)
        if title is None:
            self.stdout.write(
                f'invalid title_id: {title_id}: '
                f'skipping record'
            )
            return

        genre = self.get_genre(genre_id)
        if genre is None:
            self.stdout.write(
                f'invalid genre_id: {genre_id}: '
                f'skipping record'
            )
            return

        gt = self.get_genre_title(id)
        if gt is None:
            try:
                GenreTitle.objects.create(
                    pk=id,
                    title=title,
                    genre=genre
                )
                self.stdout.write(
                    f'GenreTitle: {id}: created '
                    f'({genre_id}/{title_id})'
                )
            except Exception:
                self.stdout.write(
                    f'error creating GenreTitle: {id} '
                    f'({genre_id}/{title_id}): '
                    f'skipping record'
                )
        else:
            gt.title = title
            gt.genre = genre
            try:
                gt.save()
                self.stdout.write(
                    f'GenreTitle: {id}: updated '
                    f'({genre_id}/{title_id})'
                )
            except Exception:
                self.stdout.write(
                    f'error creating GenreTitle: {id} '
                    f'({genre_id}/{title_id}): '
                    f'skipping record'
                )
                return

    def load_db_genre_titles(self, csv_dir, need_no_purge):
        """Заливает связи GenreTitle из csv

        Ожидает, что есть первая строка с заголовками
        id, title_id, genre_id,
        пропускает её

        TODO: buckets, need_no_purge
        """

        self.stdout.write('load_db: GenreTitle:')
        with open(csv_dir + '/genre_title.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(csvreader, None)
            for row in csvreader:
                self.load_db_one_genre_title(row)

    def load_db_one_review(self, row):
        id = int(row[0])
        title_id = int(row[1])
        text = row[2]
        author_id = int(row[3])
        score = int(row[4])
        if score < 1 or int(row[3]) > 10:
            score = 5
        pub_date = row[5]
        if pub_date is None or pub_date == '':
            pub_date = timezone.now()
        else:
            pub_date = dateutil_parser.isoparse(pub_date)

        title = self.get_title(title_id)
        if title is None:
            self.stdout.write(
                f'invalid title_id: {title_id}: '
                f'skipping record'
            )
            return

        author = self.get_user(author_id)
        if author is None:
            self.stdout.write(
                f'invalid author_id: {author_id}: '
                f'skipping record'
            )
            return

        review = self.get_review(id)
        if review is None:
            try:
                Review.objects.create(
                    pk=id,
                    title=title,
                    text=text,
                    author=author,
                    score=score,
                    pub_date=pub_date
                )
                self.stdout.write(
                    f'Review: {id}: created'
                )
            except Exception:
                self.stdout.write(
                    f'error creating Review: {id} '
                )
                return
        else:
            review.title = title
            review.text = text
            review.author = author
            review.score = score
            review.pub_date = pub_date
            try:
                review.save()
                self.stdout.write(
                    f'Review: {id}: updated'
                )
            except Exception:
                self.stdout.write(
                    f'error updating Review: {id} '
                )
                return

    def load_db_reviews(self, csv_dir, need_no_purge):
        """Заливает отзывы из csv

        Ожидает, что есть первая строка с заголовками
        id, title_id, text, author, score, pub_date,
        пропускает её

        TODO: buckets, need_no_purge
        """

        self.stdout.write('load_db: Review:')
        with open(csv_dir + '/review.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(csvreader, None)
            for row in csvreader:
                self.load_db_one_review(row)

    def load_db_one_comment(self, row):
        id = int(row[0])
        review_id = int(row[1])
        text = row[2]
        author_id = int(row[3])
        pub_date = row[4]
        if pub_date is None or pub_date == '':
            pub_date = timezone.now()
        else:
            pub_date = dateutil_parser.isoparse(pub_date)

        review = self.get_review(review_id)
        if review is None:
            self.stdout.write(
                f'invalid review_id: {review_id}: '
                f'skipping record'
            )
            return

        author = self.get_user(author_id)
        if author is None:
            self.stdout.write(
                f'invalid author_id: {author_id}: '
                f'skipping record'
            )
            return

        comment = self.get_comment(id)
        if comment is None:
            try:
                Comment.objects.create(
                    pk=id,
                    review=review,
                    text=text,
                    author=author,
                    pub_date=pub_date
                )
                self.stdout.write(
                    f'Comment: {id}: created'
                )
            except Exception:
                self.stdout.write(
                    f'error creating Comment: {id} '
                )
                return
        else:
            comment.review = review
            comment.text = text
            comment.author = author
            comment.pub_date = pub_date
            try:
                comment.save()
                self.stdout.write(
                    f'Comment: {id}: updated'
                )
            except Exception:
                self.stdout.write(
                    f'error updating Comment: {id} '
                )
                return

    def load_db_comments(self, csv_dir, need_no_purge):
        """Заливает комментарии из csv

        Ожидает, что есть первая строка с заголовками
        id, review_id, text, author, pub_date,
        пропускает её

        TODO: buckets, need_no_purge
        """

        self.stdout.write('load_db: Comment:')
        with open(csv_dir + '/comments.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(csvreader, None)
            for row in csvreader:
                self.load_db_one_comment(row)

    def load_db(self, need_no_purge):
        """Заливка данных из csv-шек в бд

        Льём строго в определённом порядке
        (от юзверей и словарей до комментов).
        Юзверей upsert-им в любом случае, всё остальное - insert
        при need_no_purge == False и insert при True
        (в текущей реализации всем делаем не-пакетный (циклом)
        квази-апсерт (попытка чтения, далее вставка или обновление записи)).

        NB: Порядок заливки важен !

        TODO: buckets, need_no_purge
        """

        csv_dir = str(settings.BASE_DIR) + '/static/data'

        self.load_db_users(csv_dir, need_no_purge)
        self.load_db_categories(csv_dir, need_no_purge)
        self.load_db_genres(csv_dir, need_no_purge)
        self.load_db_titles(csv_dir, need_no_purge)
        self.load_db_genre_titles(csv_dir, need_no_purge)
        self.load_db_reviews(csv_dir, need_no_purge)
        self.load_db_comments(csv_dir, need_no_purge)
