# api-tests — API-автотесты на Python (requests + pytest)

Учебный проект: API-автотесты на Python. Пишу по мере прохождения курса, каждый урок —
новый набор проверок. Живой репозиторий, а не выставочный: тесты добавляются и правятся.

UI-часть (Selenium + pytest, Page Object) — в отдельном репозитории:
https://github.com/dimer1883-crypto/saucedemo-test

## Стенды

- https://dummyjson.com — основной тренировочный стенд. Открытый API без ключа,
  лимит запросов около 100 в минуту, умеет отдавать реальные ошибки с текстом
  (404 «User with id ... not found», 400 «Invalid credentials»).
- https://api.github.com — реальный публичный API с авторизацией по токену.
  Используется для проверки работы с заголовками и токенами.

## Что уже покрыто

| Файл | Что проверяется |
| --- | --- |
| tests/test_create_user.py | POST /users/add — создание пользователя, код 201, поля в ответе, генерация id |
| tests/test_negative.py | Негативные сценарии: 404 на несуществующего пользователя, 400 при логине без пароля и с неверным паролем |
| tests/test_users_parametrized.py | Параметризация (@pytest.mark.parametrize): выборка пользователей по id через набор данных |
| tests/test_structure.py | Контракт ответа: обязательные поля и их типы (id, firstName, lastName, email, username, age) |
| tests/test_auth.py | Авторизация на GitHub REST API: запрос с токеном, без токена (401), несуществующий пользователь (404) |

## Структура

```
api-tests/
├── conftest.py                        # фикстура base_url (общий стенд)
├── requirements.txt
├── pytest.ini
├── LESSONS.md                         # конспект курса: уроки, прогресс, заметки
├── tests/
│   ├── test_create_user.py
│   ├── test_negative.py
│   ├── test_users_parametrized.py
│   ├── test_structure.py
│   └── test_auth.py
└── .vscode/settings.json              # запуск pytest из панели тестов VS Code
```

## Как запустить

Нужен Python 3.13 и git. На Windows интерпретатор запускается командой `py`.

1. Клонировать репозиторий и перейти в него:

```
git clone https://github.com/dimer1883-crypto/api-tests.git
cd api-tests
```

2. Создать виртуальное окружение и активировать его:

```
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1     # PowerShell
.venv\Scripts\activate.bat       # cmd
```

3. Установить зависимости:

```
pip install -r requirements.txt
```

4. Запустить тесты:

```
pytest -v
```

## Тесты GitHub API

Три теста из `tests/test_auth.py` обращаются к api.github.com и требуют токена.
Если переменная окружения не задана, они не падают, а пропускаются (`skipped`) —
остальной набор работает без токена.

Задать токен (PowerShell, на текущую сессию):

```
$env:GITHUB_TOKEN = "ghp_..."
```

Токен нужен только на чтение профиля, права на запись не требуются. Ключ в код
не хардкодится: тест читает его через `os.environ`.

## Дальше в планах

- CI в GitHub Actions: прогон pytest на каждый push
- Проверка JSON-схем ответов (jsonschema)
- Публикация Allure-отчёта по прогону

## Заметки по курсу

Подробный конспект уроков, прогресс и разбор ошибок — в [LESSONS.md](LESSONS.md).
