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
- [x] Урок 7. Авторизация: токены, заголовки (GitHub REST API)
- [x] Урок 8. CI в GitHub Actions (прогон на каждый пуш, бейдж в README)
- [x] Урок 9. CI, часть 2: секрет репозитория API_TOKEN (в CI 12 passed, без skipped),
      Allure-результаты загружаются артефактом
- [x] Урок 10. Проверка контракта библиотекой jsonschema (14 тестов, CI зелёный)
- [x] Урок 11. Маркеры smoke/regression, ночной full-прогон, выбор группы при ручном запуске
- [ ] Урок 12. Фикстуры с yield: подготовка и уборка данных (setup/teardown)
- [ ] Дальше по договорённости: Allure-отчёт на GitHub Pages, реальное хранение данных (GitHub issues)

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

---

## Урок 7. Авторизация: токены и заголовки

Заголовки запроса (headers) — служебные поля, которые уезжают на сервер вместе с
запросом: `Authorization` (кто я), `Accept` (в каком формате хочу ответ). Закрытые
методы без токена отвечают 401; 403 — это «авторизован, но нет прав» или лимит.

Токен НИКОГДА не пишется в код: он живёт в переменной окружения, код его читает.
На Windows (PowerShell) постоянная запись для текущего пользователя:

    [Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "значение", "User")

После этого нужно ПОЛНОСТЬЮ перезапустить VSCode: процессы получают копию окружения
в момент запуска, поэтому старая копия токена не видит.

`tests/test_auth.py`:

```python
import os

import pytest
import requests

GITHUB_API = "https://api.github.com"


@pytest.fixture(scope="session")
def github_token():
    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        pytest.skip("переменная GITHUB_TOKEN не задана — тесты GitHub пропущены")

    return token


@pytest.fixture(scope="session")
def github_headers(github_token):
    return {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }


def test_get_my_profile(github_headers):
    response = requests.get(f"{GITHUB_API}/user", headers=github_headers)

    assert response.status_code == 200

    data = response.json()
    assert data["login"] == "dimer1883-crypto"


def test_request_without_token():
    response = requests.get(f"{GITHUB_API}/user")

    assert response.status_code == 401

    assert response.json()["message"] == "Requires authentication"


def test_github_user_not_found():
    response = requests.get(
        f"{GITHUB_API}/users/etot-polzovatel-tochno-ne-sushchestvuet-123"
    )

    assert response.status_code == 404

    assert response.json()["message"] == "Not Found"
```

Приёмы урока: `os.environ.get` читает переменную окружения; фикстура может зависеть от
другой фикстуры (`github_headers(github_token)`); `pytest.skip` внутри фикстуры помечает
тесты пропущенными, если секрета нет, — набор остаётся зелёным на чужой машине.

Права токена (classic): минимум. Для урока достаточно нуля галочек; для отправки кода и
файлов Actions взяты `public_repo` и `workflow`. Срок — 90 дней, значение сохраняется
в KeePass (шара `\\TRUENAS\vault`).

Запуск: `pytest -v` → `12 passed`.

Ошибка, которую поймали по ходу: `return token` оказался внутри `if not token:` (отступ в
8 пробелов вместо 4). Тогда при наличии токена функция возвращала None, а заголовок
получался `Bearer None` и сервер отвечал 401. В отчёте pytest это видно сразу: он печатает
значения фикстур над упавшим тестом. Второй признак: тест FAILED, а не SKIPPED, значит
токен в окружении был, а проблема в коде.

Коммит: `Lesson 7: GitHub API auth (token from env)` (fade968).

---

## Урок 8. CI в GitHub Actions

CI (Continuous Integration) — тесты запускаются автоматически на чужой чистой машине
при каждом пуше. У GitHub для этого есть Actions: в репозиторий кладётся файл-инструкция
`.github/workflows/tests.yml`, и GitHub на каждый пуш поднимает виртуалку с Ubuntu,
ставит Python и библиотеки и прогоняет тесты.

Состав: `requirements.txt` (список зависимостей с версиями — без него чистая машина не
знает, что ставить), `pytest.ini` (testpaths = tests), сам workflow и бейдж статуса в
README.

```yaml
name: Run tests

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest
```

Важно: `requirements.txt` в PowerShell делать через
`pip freeze | Out-File -Encoding utf8 requirements.txt` — оператор `>` пишет UTF-16,
который Linux не читает (это уже проходили в UI-курсе). Файл должен быть ASCII/UTF-8.

Коммиты: `Add README, requirements, pytest.ini` (d9f1937), `Add CI: run pytest on push`
(583c978). Прогон зелёный, но в логе `11 passed, 1 skipped`: тест `test_get_my_profile`
в CI пропускается, потому что секрет с токеном в репозитории не заведён, а фикстура
`github_token` при отсутствии переменной делает `pytest.skip`. Это тема урока 9 —
зелёный отчёт при фактически непроверенном сценарии.

---

## Урок 9. CI, часть 2: секрет репозитория и Allure-артефакт

Проблема, которую решали: в первом прогоне CI было `11 passed, 1 skipped` — тест с
токеном пропускался, потому что секрета в репозитории не было, а фикстура при отсутствии
переменной окружения делает `pytest.skip`. Зелёный отчёт при непроверенном сценарии —
типичная ловушка, смотреть надо не на цвет, а на строку итога.

Решения:

1. Секрет репозитория. Settings → Secrets and variables → Actions → New repository secret.
   Имя `API_TOKEN`, значение — токен. ВАЖНО: имена секретов не могут начинаться с
   `GITHUB_` (зарезервировано платформой), поэтому имя своё, а переменная окружения —
   по-прежнему `GITHUB_TOKEN`.

2. Имя секрета и имя переменной окружения — разные вещи, совпадать не обязаны:

   секрет `API_TOKEN` (где хранится) → переменная окружения `GITHUB_TOKEN` (что видит
   процесс) → `os.environ.get("GITHUB_TOKEN")` (что читает фикстура).

3. В workflow появились `env` с секретом, `--alluredir` и загрузка артефакта:

```yaml
      - name: Run tests
        env:
          GITHUB_TOKEN: <выражение доступа к секрету API_TOKEN>
        run: pytest --alluredir=./allure-results

      - name: Upload allure results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: allure-results
          path: allure-results
```

`if: always()` нужен, чтобы отчёт загружался и при упавших тестах — именно тогда он и
бывает нужен.

Итог: прогон зелёный, `12 passed in 0.84s`, без `skipped`. Отчёт забирается из блока
Artifacts прогона, локально открывается командой `allure serve ./allure-results`.

Коммит: `Lesson 9: pass token to CI and upload allure results` (cbf0277).

### Уроки по git, полученные по ходу

- Конфликт при `git pull --rebase` (файл правили и локально, и через веб-интерфейс
  GitHub) разрешается руками: убрать маркеры `<<<<<<<` / `=======` / `>>>>>>>`, оставить
  правильный текст → `git add <файл>` → `git rebase --continue` (и закрыть редактор с
  сообщением коммита).
- Во время rebase git находится в detached HEAD: `git commit` руками делать нельзя (уводит
  в «не на ветке»), коммит делает сам rebase.
- Если коммит всё же сделан в detached HEAD: `git rebase --quit` (выйти, не откатывая),
  затем `git branch -f main <коммит>` (ветку нельзя двигать, стоя на ней самой),
  `git checkout main`, `git push`.
- Правило гигиены: не править файлы проекта в веб-интерфейсе GitHub, пока работаешь с
  этим проектом локально — иначе получаешь две версии одного файла.

---

## Урок 10. Проверка контракта библиотекой jsonschema

JSON Schema — стандарт описания структуры JSON: какие поля обязательны, какие у них типы,
что вложено во что. Библиотека `jsonschema` сравнивает данные со схемой, а при расхождении
выбрасывает `ValidationError` с текстом и путём до проблемного поля (например
`'29' is not of type 'integer'` для `$.age`).

Схема описывает контракт декларативно: её можно хранить отдельным файлом, положить в
документацию и отдать бэкенду как договор. В уроке 6 то же самое делали вручную словарём
«поле → тип» — это был учебный вариант, jsonschema это промышленный стандарт.

`tests/test_schema.py`:

```python
import pytest
import requests
from jsonschema import ValidationError, validate


USER_SCHEMA = {
    "type": "object",
    "required": ["id", "firstName", "lastName", "age", "email", "hair"],
    "properties": {
        "id": {"type": "integer"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string"},
        "hair": {
            "type": "object",
            "required": ["color"],
            "properties": {
                "color": {"type": "string"},
                "type": {"type": "string"},
            },
        },
    },
}


def test_user_matches_schema(base_url):
    response = requests.get(f"{base_url}/users/1")

    assert response.status_code == 200

    validate(instance=response.json(), schema=USER_SCHEMA)


def test_schema_catches_broken_data():
    broken_user = {
        "id": 1,
        "firstName": "Emily",
        "lastName": "Johnson",
        "age": "29",
        "email": "emily.johnson@x.dummyjson.com",
        "hair": {"color": "Brown", "type": "Curly"},
    }

    with pytest.raises(ValidationError):
        validate(instance=broken_user, schema=USER_SCHEMA)
```

Приёмы урока: ключи схемы `type` / `required` / `properties`; вложенные объекты описываются
тем же способом внутри `properties`; `with pytest.raises(ValidationError)` — негативная
проверка самой валидации (если схема перестанет ловить испорченные данные, тест упадёт).

`jsonschema==4.26.0` добавлен в `requirements.txt` — иначе CI падает на чистой машине.

Коммит: `Lesson 10: validate response schema with jsonschema` (da4f47c).
CI: `14 passed in 1.82s`.

---

## Урок 11. Маркеры smoke/regression и режимы прогона в CI

Маркер (метка) — пометка на тесте: на обычный прогон не влияет, но позволяет запускать
группу (`pytest -m smoke`). Smoke — короткий набор ключевых сценариев на каждый пуш;
regression — всё остальное, обычно ночью.

Маркеры объявляются в pytest.ini (иначе PytestUnknownMarkWarning):

```ini
[pytest]
testpaths = tests
markers =
    smoke: быстрые проверки ключевых сценариев
    regression: полный набор проверок
```

Маркером `smoke` помечены пять тестов: создание пользователя, 404 на несуществующего,
структура ответа, схема ответа, авторизация на GitHub. Остальные девять — регрессионная
часть (`pytest -m "not smoke"`, кавычки обязательны — иначе PowerShell отдаёт `not` как
отдельный аргумент).

Запуски: `pytest -m smoke` → `5 passed, 9 deselected`; `pytest -m "not smoke"` →
`9 passed, 5 deselected`; `pytest` → `14 passed`.

В workflow два задания и четыре события:

| Событие | Что выполняется |
| --- | --- |
| push / pull_request | `smoke` (5 тестов, быстро) |
| расписание `0 3 * * *` (3:00 UTC = 7:00 МСК+1) | `full` (все тесты) |
| Run workflow, выбран `smoke` | `smoke` |
| Run workflow, выбран `full` | `full` |

Ключевые куски конфигурации: `schedule: cron` (пять полей: минута, часы, день, месяц,
день недели, время в UTC), `workflow_dispatch: inputs: type: choice` (выпадающий список в
окне ручного запуска), `if:` на уровне задания (условие по событию и выбранной группе через
`github.event.inputs.group`), разные имена артефактов (`allure-results-smoke` /
`allure-results-full`), иначе в одном прогоне они перезапишут друг друга.

Кнопка `Run workflow` живёт на странице workflow (`Actions` → в списке слева `Run tests`),
а не на странице отдельного прогона. Появляется только если в файле есть
`workflow_dispatch:` и файл лежит в ветке по умолчанию.

Коммиты: `Lesson 11: smoke/regression markers; nightly full run` (bd03cf1),
`Lesson 11: choose test group on manual run` (0e30ba6).

