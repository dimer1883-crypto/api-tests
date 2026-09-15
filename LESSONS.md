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
- [x] Урок 3. Фикстуры pytest и базовый URL (conftest.py)
- [ ] Урок 4. Негативные проверки: 404 и 400 (как система отказывает)
- [ ] Урок 5. Параметризация тестов (@pytest.mark.parametrize)
- [ ] Урок 6. Схемы ответа (проверка структуры и типов JSON)
- [ ] Урок 7. Авторизация: токены, заголовки (переход на GitHub REST API)
- [ ] Дальше по договорённости: CI (GitHub Actions), Allure

## Целевой стенд для практики

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
