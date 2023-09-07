# YaMDb API

## Описание

Бэкенд на DRF - YaMDb API для организации функционала отзывов на произведения
с комментариями, оценками, рейтингами и т.п.

Документация по API (доступна после установки):

- статичная (на момент последнего релиза) в ReDoc: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)
- динамическая, для разработчиков, в ReDoc: [http://127.0.0.1:8000/redoc_d/](http://127.0.0.1:8000/redoc_d/)
- динамическая, для разработчиков, в Swagger: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)

## Установка

Клонируем репозиторий, переходим в директорию проекта

```bash
$ git clone https://github.com/Dead-Maxim/api_yamdb.git
...
$ cd ./api_yamdb
$ ls
postman_collection  pytest.ini  README.md  requirements.txt  setup.cfg  tests  api_yamdb
```

Создаём вирт. окружение, заливаем библитотеки согласно requirements.txt

(NB: разработка и тестирование велось под python 3.9)

```bash
$ python3.9 -m venv venv
$ source ./venv/bin/activate
(venv) $ pip install -r requirements.txt
...
```

Переходим в директорию основного приложения,
делаем миграции, при желании создаём суперпользователя, запускаем сервер

```bash
(venv) $ cd ./api_yamdb
(venv) $ python manage.py makemigrations
...

(venv) $ python manage.py migrate
Operations to perform:
  Apply all migrations: ...
Running migrations:
...

(venv) $ python manage.py runserver
...
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.

```

Сервис доступен по указанному адресу по http.

Далее можно создать пользователей, отзывы и т.д.

## Как залить sample-данные для разработки, тестирования и т.п.


Так бд зачистится (кроме пользователей-супервизоров),
и данные зальются поверх пустых таблиц (рекомендованный вариант):

```bash
$ python manage.py load_data_initial
```

Так зальются новые поверх старых (строго не рекомендуется
в случае заливки данных из файлов, поставляемых с проектом,
но только если вы сами сознательно подготовили такие данные):

```bash
$ python manage.py load_data_initial --need_no_purge
```

Ожидаемое инструментом `load_data_initial` размещение файлов с данными:

```bash
BASE_DIR//static/data
- comments.csv
- review.csv
- genre_title.csv
- titles.csv
- genre.csv
- category.csv
- users.csv
```



## Примеры

### Создадим двух пользователей

Request:

```json
/*
POST http://127.0.0.1:8000/api/v1/auth/signup/

Content-Type: application/json
*/

{
"username": "Bob",
"email": "bob@example.com"
}
```

Response:

```json
/*
200 OK

Date: Tue, 05 Sep 2023 18:12:06 GMT
Server: WSGIServer/0.2 CPython/3.9.18
Content-Type: application/json
Vary: Accept
Allow: POST, OPTIONS
...
*/

{
  "username": "Bob",
  "email": "bob@example.com"
}
```

и аналогично второй:

```json
/*
POST http://127.0.0.1:8000/api/v1/auth/signup/

Content-Type: application/json
*/

{
"username": "Alice",
"email": "alice@example.com"
}
```

На емайл-адреса при этом были высланы коды подтверждения.

**NB:** в тестовой версии отправленные письма надо искать
в директории `sent_emails` внутри директории проекта

### Получим JWT-токены созданным пользователям

Request:

```json
/*
POST http://127.0.0.1:8000/api/v1/auth/token/

Content-Type: application/json
*/

{
"username": "Bob",
"confirmation_code": "274e0d37-6513-4800-809f-437314239ffa"
}
```

Response:

```json
/*
200 OK
*/

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl..."
}
```

и аналогично второй:

```json
/*
POST http://127.0.0.1:8000/api/v1/auth/token/

Content-Type: application/json
*/

{
"username": "Alice",
"confirmation_code": "b0896539-0269-4528-abd6-c86ccd7bd43e"
}

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl9..."
}
```

Далее все запросы к основному api должны снабжаться
заголовком `Authorization` со значением `Bearer {значение поля access из ответа выше}`
(для каждого пользователя своим).

### Например пользователь Alice может создать отзыв

Request:

```json
/*
POST http://127.0.0.1:8000/api/v1/titles/1/reviews/

Content-Type: application/json
Authorization: Bearer eyJ0e...
*/

{
"text": "намана",
"score": 5
}
```

Response:

```json
/*
201 Created
*/

{
  "id": 1,
  "author": "Alice",
  "text": "намана",
  "score": 5,
  "pub_date": "2023-08-13T11:59:32.308323Z",
  "title": 1
}
```

## а Bob увидеть его в ленте отзывов

Request:

```json
/*
GET http://127.0.0.1:8000/api/v1/titles/1/reviews/

Content-Type: application/json
Authorization: Bearer eyJ0e...
*/
```

Response:

```json
/*
200 OK
*/

{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "text": "намана",
      "author": "Alice",
      "score": 5,
      "pub_date": "2023-09-05T11:08:22.502346Z",
      "title": 1
    },
    {
      "id": 1,
      "text": "Удовлетворительно",
      "author": "vonbraun4",
      "score": 3,
      "pub_date": "2023-09-05T10:56:20.991347Z",
      "title": 1
    }
  ]
}
```

### Больше примеров

можно построить самим согласно документации:

- статичная (на момент последнего релиза) в ReDoc: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)
- динамическая, для разработчиков, в ReDoc: [http://127.0.0.1:8000/redoc_d/](http://127.0.0.1:8000/redoc_d/)
- динамическая, для разработчиков, в Swagger: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
