# Курс: API-автотесты (requests + pytest)

Учебный проект API-автотестов. Тренировочный стенд: https://reqres.in (учебный API,
аналог saucedemo для UI). Дальше — публичный реальный API (GitHub REST).
Репозиторий: https://github.com/dimer1883-crypto/api-tests

UI-курс (Selenium + pytest, saucedemo) — 10/10, отдельный репозиторий:
https://github.com/dimer1883-crypto/saucedemo-test

---

## Установка на новый ПК (или переустановка с нуля)

Нужно: Python 3.13 (запускается командой `py`), git.

1. Клонировать репозиторий:
```
git clone https://github.com/dimer1883-crypto/api-tests.git
cd api-tests
```

2. Создать виртуальное окружение (важно: команда `py`, а не `python`):
```
py -3.13 -m venv .venv
```

3. Активировать его:
- PowerShell: `.\.venv\Scripts\Activate.ps1`
- cmd: `.venv\Scripts\activate.bat`

4. Установить зависимости:
```
pip install requests pytest
```

5. Проверить, что всё работает:
```
pytest -v
```
Должно быть `1 passed`.

---

## Прогресс уроков

- [x] Урок 1. Что такое API-тест: GET-запрос, статус-код, JSON, библиотека requests
- [x] Урок 2. POST-запрос: создание ресурса и проверка ответа сервера
- [x] Урок 3. Фикстуры pytest и базовый URL (conftest.py в корне проекта)
- [x] Урок 4. Негативные проверки: 404 и 400 (как система отказывает)
- [x] Урок 5. Параметризация тестов (@pytest.mark.parametrize)
- [x] Урок 5.1. Лимит запросов (429) и смена стенда на dummyjson.com
- [x] Урок 6. Проверка структуры ответа (типы и обязательные поля)
- [ ] Урок 7. Авторизация: токены, заголовки (переход на GitHub REST API)
- [ ] Дальше по договорённости: CI (GitHub Actions), Allure

## Стенд для практики

Текущий стенд: https://dummyjson.com — открытый тестовый API без ключа, с реальными
ошибками (404 с текстом, 400 «Invalid credentials») и генерацией id. Лимит ~100
запросов в минуту, суточного потолка нет.

Почему ушли с reqres.in: у него лимит анонимного доступа 40 запросов в СУТКИ на IP
(заголовки X-Ratelimit-Limit: 40, X-Ratelimit-Remaining: 0), а один прогон pytest
съедает 7–9 запросов. Несколько прогонов — и весь стенд отдаёт 429 до полуночи по UTC
(04:00 по Саратову). Для ежедневной учёбы не годится.

Переходим на публичный реальный API — GitHub REST (авторизация по токену, живые данные, настоящие ошибки 401/404/422).

---

## Урок 1. Первый API-тест: GET /api/users/2

Что такое API-тест (коротко): вместо кликов по странице тест обращается к серверу
напрямую и проверяет его ответ — код статуса (200, 404, 500) и тело ответа в JSON.
Библиотека `requests` отправляет HTTP-запросы: GET — получить, POST — создать,
PUT/PATCH — изменить, DELETE — удалить.

Задача: запросить пользователя с id = 2 и проверить, что сервер вернул именно его.

Файл `tests/test_users.py`:

```python
import requests

def test_get_single_user():
    # 1. отправляем GET-запрос на https://reqres.in/api/users/2
    response = requests.get("https://reqres.in/api/users/2")

    # 2. проверяем код статуса (должен быть 200)
    assert response.status_code == 200

    # 3. тело ответа превращаем в словарь и достаём данные пользователя
    data = response.json()["data"]

    # 4. проверяем имя и фамилию
    assert data["first_name"] == "Janet"
    assert data["last_name"] == "Weaver"
```

Ожидаемые значения (Janet / Weaver) взяты из реального ответа сервера — их видно,
если открыть https://reqres.in/api/users/2 в браузере.

Запуск: `pytest -v` → `1 passed`.

Коммит: `Lesson 1: first API test (GET /api/users/2)` (a159147).

Заметка на будущее (PEP8): между `import` и первым `def` должно быть две пустые строки.

---

## Урок 2. POST-запрос: создание ресурса

Что такое POST (коротко): метод, которым тест просит сервер создать новый объект.
В отличие от GET, данные уезжают на сервер в теле запроса (payload) — в `requests`
это параметр `json=`. Успешное создание подтверждается кодом 201 (Created), а не 200.
Поля `id` и `createdAt` сервер генерирует сам (в реальной системе — база данных).

Задача: создать пользователя и проверить ответ сервера.

Файл `tests/test_create_user.py`:

```python
import requests

BASE_URL = "https://reqres.in/api"

def test_create_user():
    payload = {"name": "Dmitry", "job": "QA Engineer"}

    response = requests.post(f"{BASE_URL}/users", json=payload)

    # сервер должен ответить 201 Created
    assert response.status_code == 201

    body = response.json()
    assert body["name"] == "Dmitry"
    assert body["job"] == "QA Engineer"

    # id и createdAt сервер генерирует сам — их значение неизвестно,
    # поэтому проверяем только то, что они появились в ответе
    assert "id" in body
    assert "createdAt" in body
```

Главная логика урока: то, что задаём мы (name, job), проверяем на равенство; то, что
создаёт сервер (id, createdAt), — только на факт наличия. `BASE_URL` вынесен в
переменную наверху файла, чтобы при смене стенда править одну строку.

Запуск: `pytest -v` → `2 passed`.

Коммит: `Lesson 2: POST create user` (40da14b).

---

## Урок 3. Фикстуры pytest и conftest.py

Фикстура — подготовка, которую pytest выполняет перед тестом и подкладывает тесту по
имени параметра. `conftest.py` pytest читает автоматически, импортировать не нужно.
`scope="session"` — фикстура создаётся один раз на весь прогон (для неизменных данных,
например адреса стенда).

Файл `tests/conftest.py` (работает и в корне проекта — тогда фикстура видна вообще всем
подпапкам; в `tests/` она видна всем файлам внутри `tests`):

```python
import pytest

@pytest.fixture(scope="session")
def base_url():
    return "https://reqres.in/api"
```

Тесты получают адрес через параметр `base_url` вместо своей константы `BASE_URL`:

```python
import requests

def test_get_single_user(base_url):
    response = requests.get(f"{base_url}/users/2")

    assert response.status_code == 200

    data = response.json()["data"]
    assert data["first_name"] == "Janet"
    assert data["last_name"] == "Weaver"
```

```python
import requests

def test_create_user(base_url):
    payload = {"name": "Dmitry", "job": "QA Engineer"}

    response = requests.post(f"{base_url}/users", json=payload)

    assert response.status_code == 201

    body = response.json()
    assert body["name"] == "Dmitry"
    assert body["job"] == "QA Engineer"

    assert "id" in body
    assert "createdAt" in body
```

Связка работает по имени: параметр теста должен точно совпадать с именем фикстуры, иначе
pytest скажет `fixture '...' not found`. Полезная команда: `pytest --fixtures` — показать
все доступные фикстуры.

Запуск: `pytest -v` → `2 passed` (то же, что до рефакторинга — поведение не изменилось).

Коммит: `Lesson 3: base_url fixture in conftest` (1150188).

---

## Урок 4. Негативные проверки: 404 и 400

Позитивный тест проверяет, что система работает при верных данных; негативный — что она
корректно отказывает при неверных. Коды: 4xx — виноват клиент (неверный запрос, объект
не найден), 5xx — виноват сервер (это всегда баг). В негативных тестах проверяют не
только код ответа, но и текст ошибки: его показывает пользователю фронт, значит он тоже
часть контракта API.

Файл `tests/test_negative.py`:

```python
import requests

def test_user_not_found(base_url):
    # запрашиваем пользователя с заведомо несуществующим id
    response = requests.get(f"{base_url}/users/23")

    # сервер обязан честно ответить 404 Not Found
    assert response.status_code == 404

def test_login_without_password(base_url):
    # отправляем логин без пароля
    response = requests.post(f"{base_url}/login", json={"email": "dmitry@test.ru"})

    assert response.status_code == 400

    body = response.json()
    assert body["error"] == "Missing password"

def test_login_with_wrong_credentials(base_url):
    # логин есть, пароль неверный
    response = requests.post(
        f"{base_url}/login",
        json={"email": "dmitry@test.ru", "password": "wrong"},
    )

    assert response.status_code == 400

    assert response.json()["error"] == "user not found"
```

Запуск: `pytest -v` → `5 passed`.

Коммит: `Lesson 4: negative tests (404, 400)` (13dde2a).

---

## Урок 5. Параметризация: один тест, много данных

`@pytest.mark.parametrize` заставляет pytest вызвать одну функцию несколько раз с
разными данными. Первый аргумент — строка с именами параметров через запятую (имена
обязаны совпадать с параметрами функции), второй — список кортежей, один кортеж = один
запуск и одна строка в отчёте. Фикстуры и параметры живут в одной сигнатуре: pytest
собирает аргументы по именам из обоих источников.

`tests/test_users_parametrized.py`:

```python
import pytest
import requests

@pytest.mark.parametrize(
    "user_id, expected_first_name, expected_last_name",
    [
        (1, "Emily", "Johnson"),
        (2, "Michael", "Williams"),
        (3, "Sophia", "Brown"),
        (4, "James", "Davis"),
    ],
)
def test_get_user_by_id(base_url, user_id, expected_first_name, expected_last_name):
    response = requests.get(f"{base_url}/users/{user_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_id
    assert data["firstName"] == expected_first_name
    assert data["lastName"] == expected_last_name
```

В параметрах отчёта pytest показывает набор в имени теста, например
`test_get_user_by_id[2-Michael-Williams]`.

Коммит: `Lesson 5: parametrize tests` (724947b).

---

## Урок 5.1. Лимит запросов (429) и смена стенда

Первый прогон параметризованных тестов упал целиком: все 9 тестов вернули 429 вместо
ожидаемых кодов. Это не баг тестов и не баг API — это лимит: reqres.in разрешает 40
запросов в сутки на IP для анонимного доступа (заголовки `X-Ratelimit-Limit: 40`,
`X-Ratelimit-Remaining: 0`, сброс в 00:00 UTC). ПК и NAS выходят в интернет через один
публичный IP, поэтому лимит выбирается быстро.

Правило на будущее: 429 Too Many Requests — «слишком много запросов», лимит исчерпан.
У боевых API лимиты тоже есть, и автотесты должны их уважать, иначе CI краснеет из-за
лимита, а не из-за бага.

Замена стенда на https://dummyjson.com. Это и есть проверка урока 3: адрес живёт в одной
фикстуре, поменять нужно было одну строку — но эндпоинты и имена полей у нового API
другие, поэтому тесты переписаны.

`conftest.py`:

```python
import pytest

@pytest.fixture(scope="session")
def base_url():
    return "https://dummyjson.com"
```

`tests/test_users_parametrized.py` — см. урок 5 (данные уже от dummyjson).

`tests/test_create_user.py`:

```python
import requests

def test_create_user(base_url):
    payload = {"firstName": "Dmitry", "lastName": "Erakhtin"}

    response = requests.post(f"{base_url}/users/add", json=payload)

    # сервер должен ответить 201 Created
    assert response.status_code == 201

    body = response.json()
    assert body["firstName"] == "Dmitry"
    assert body["lastName"] == "Erakhtin"

    # id сервер генерирует сам — проверяем только наличие
    assert "id" in body
```

`tests/test_negative.py`:

```python
import requests

def test_user_not_found(base_url):
    # пользователя с таким id заведомо нет
    response = requests.get(f"{base_url}/users/9999")

    assert response.status_code == 404

    # у dummyjson вместе с кодом приходит и текст ошибки
    assert response.json()["message"] == "User with id '9999' not found"

def test_login_without_password(base_url):
    # отправляем логин без пароля
    response = requests.post(f"{base_url}/auth/login", json={"username": "emilys"})

    assert response.status_code == 400

    assert response.json()["message"] == "Username and password required"

def test_login_with_wrong_credentials(base_url):
    # логин есть, пароль неверный
    response = requests.post(
        f"{base_url}/auth/login",
        json={"username": "emilys", "password": "wrong"},
    )

    assert response.status_code == 400

    assert response.json()["message"] == "Invalid credentials"
```

Рабочие креды dummyjson (для урока про авторизацию): `emilys` / `emilyspass` → 200 и
`accessToken` в ответе.

Лимит dummyjson — около 100 запросов в минуту, суточного потолка нет.

Особенность: dummyjson стоит за Cloudflare и режет клиентов с «неродным» User-Agent.
`requests` и curl проходят, а голый `python-urllib` получает `403 error code: 1010`.

---

## Урок 6. Проверка структуры ответа

Тесты значений (статус, конкретное имя) не заметят, если бэкенд переименует поле или
поменяет его тип. Тест структуры проверяет контракт: обязательные поля на месте и у
каждого правильный тип. `isinstance(значение, тип)` отвечает, является ли значение
значением этого типа.

`tests/test_structure.py`:

```python
import requests

# контракт ответа: какие поля обязаны быть и какого они типа
USER_FIELDS = {
    "id": int,
    "firstName": str,
    "lastName": str,
    "email": str,
    "username": str,
    "age": int,
}

def test_user_response_structure(base_url):
    response = requests.get(f"{base_url}/users/1")

    assert response.status_code == 200

    data = response.json()

    for field, expected_type in USER_FIELDS.items():
        assert field in data, f"в ответе нет обязательного поля {field}"
        assert isinstance(data[field], expected_type), (
            f"поле {field}: ждали {expected_type.__name__}, "
            f"получили {type(data[field]).__name__}"
        )
```

Приёмы урока: словарь «поле → тип» как контракт в одном месте; второй аргумент `assert`
как текст сообщения в отчёте (без него видно только AssertionError); проверка «сломай
нарочно» — поменять `"age": int` на `"age": str` и убедиться, что тест краснеет.

Запуск: `pytest -v` → `9 passed`.

В промышленных проектах такую проверку делают библиотекой `jsonschema`, где схема лежит
отдельным файлом.

Коммит: `Lesson 6: response structure test; ignore allure-results` (a397c22).

