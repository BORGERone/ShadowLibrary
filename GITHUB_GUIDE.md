# Гайд по публикации Shadow Library на GitHub

## 0. Установка Git (если не установлен)

### Шаг 0.1: Скачивание

1. Перейдите на https://git-scm.com/download/win
2. Скачайте установщик для Windows
3. Запустите установщик

### Шаг 0.2: Установка

Запускайте установщик, оставляя настройки по умолчанию:
- Нажимайте "Next" на всех этапах
- Выберите "Git from the command line and also from 3rd-party software"
- Выберите "Use the OpenSSL library"
- Выберите "Checkout Windows-style, commit Unix-style line endings"
- Нажмите "Install"

### Шаг 0.3: Проверка установки

Откройте командную строку и введите:

```bash
git --version
```

Должно вывести версию, например: `git version 2.43.0.windows.1`

### Шаг 0.4: Настройка имени и email (первый запуск)

```bash
git config --global user.name "BORGER"
git config --global user.email "your-email@example.com"
```

---

## 1. Подготовка файлов для коммита

### Файлы и папки, которые НУЖНО коммитить:

```
✅ Исходный код:
   - web_server.py
   - app_window.py
   - run_server.py

✅ Папки с кодом:
   - common/ (все .py файлы)
   - templates/ (index.html и другие шаблоны)
   - locales/ (все .json файлы с переводами)

✅ Документация:
   - README.md
   - README.ru.md
   - README.*.md (все языковые версии)
   - LICENSE

✅ Конфигурация:
   - requirements.txt
   - build.spec
   - .gitignore
   - .gitattributes

✅ Ресурсы:
   - icon.ico
   - build_app.bat
   - build.bat
   - start_web.bat
```

### Файлы и папки, которые НЕ НУЖНО коммитить:

```
❌ Скомпилированные файлы:
   - __pycache__/
   - *.pyc
   - *.pyo

❌ Сборки и дистрибутивы:
   - dist/
   - build/
   - *.exe
   - *.rar
   - *.zip

❌ Логи и данные:
   - logs/
   - manifests/
   - cracked_games.json
   - config.json (содержит персональные пути)

❌ IDE настройки:
   - .vscode/
   - .idea/
   - *.swp

❌ Системные файлы:
   - Thumbs.db
   - .DS_Store
```

---

## 2. Создание .gitignore

Убедитесь, что ваш `.gitignore` файл содержит:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec.bak

# Логи и данные
logs/
*.log
manifests/
cracked_games.json

# Конфигурация с персональными данными
config.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Системные файлы
Thumbs.db
.DS_Store
```

---

## 3. Инициализация репозитория

### Шаг 3.1: Инициализация Git

Откройте командную строку в папке проекта:

```bash
cd "g:\python\Shadow Library"
git init
```

### Шаг 3.2: Проверка статуса

```bash
git status
```

Вы должны увидеть файлы, которые будут добавлены (и те, что игнорируются).

### Шаг 3.3: Добавление файлов

```bash
# Добавить все файлы (gitignore автоматически исключит ненужные)
git add .

# ИЛИ добавить конкретные файлы:
git add web_server.py app_window.py run_server.py
git add common/
git add templates/
git add locales/
git add README*.md
git add LICENSE
git add requirements.txt
git add build.spec
git add .gitignore
git add .gitattributes
git add icon.ico
git add *.bat
```

### Шаг 3.4: Первый коммит

```bash
git commit -m "Initial commit: Shadow Library v1.0.0

- Web interface for Steam game unlocking
- Support for SteamTools and GreenLuma
- Multi-language support (12 languages)
- Automatic manifest download from repositories
- Created with Python and FastAPI"
```

---

## 4. Создание репозитория на GitHub

### Шаг 4.1: Создайте репозиторий

1. Зайдите на https://github.com/new
2. Введите имя репозитория: `ShadowLibrary`
3. Описание: "Steam game unlock tool with web interface"
4. **НЕ** инициализируйте с README (вы уже сделали локальный коммит)
5. Выберите лицензию (если нужно)
6. Нажмите "Create repository"

### Шаг 4.2: Привязка удалённого репозитория

```bash
# Замените BORGERone на ваш username
git remote add origin https://github.com/BORGERone/ShadowLibrary.git
```

### Шаг 4.3: Проверка подключения

```bash
git remote -v
```

Должно вывести:
```
origin  https://github.com/BORGERone/ShadowLibrary.git (fetch)
origin  https://github.com/BORGERone/ShadowLibrary.git (push)
```

---

## 5. Публикация на GitHub

### Шаг 5.1: Переименование ветки (рекомендуется)

```bash
git branch -M main
```

### Шаг 5.2: Отправка файлов

```bash
git push -u origin main
```

Если используется двухфакторная аутентификация, используйте Personal Access Token вместо пароля.

---

## 6. Обновление проекта в будущем

### Когда вносите изменения:

```bash
# 1. Проверка изменений
git status

# 2. Добавление изменённых файлов
git add .
# или конкретные файлы:
# git add web_server.py README.md

# 3. Коммит с описанием изменений
git commit -m "Описание изменений"

# 4. Отправка на GitHub
git push
```

### Примеры хороших сообщений коммита:

```bash
# Исправление бага
git commit -m "Fix: Steam path reset after game add/remove

- Fixed get_steam_path() to read config.json on each call
- Updated SetupTools and SetupGreenLuma functions
- Added absolute paths for config files"

# Новая функция
git commit -m "Feature: Add Hindi language support

- Added README.hi.md translation
- Added hi.json locale file
- Updated language selector in all README files"

# Обновление документации
git commit -m "Docs: Update README with installation instructions

- Added SteamTools installation guide
- Updated requirements section
- Added links to official SteamTools website"
```

---

## 7. Работа с тегами (версии)

### Создание тега для версии:

```bash
# Создать тег
git tag -a v1.0.0 -m "Shadow Library v1.0.0 - Initial release"

# Отправить теги на GitHub
git push origin --tags
```

### Для будущих версий:

```bash
git tag -a v1.1.0 -m "Version 1.1.0 - New features"
git push origin --tags
```

---

## 8. Проверка перед публикацией

### Чеклист перед публикацией:

- [ ] `config.json` НЕ в коммите (содержит персональные пути)
- [ ] `cracked_games.json` НЕ в коммите
- [ ] Папки `dist/`, `build/`, `logs/`, `manifests/` НЕ в коммите
- [ ] `__pycache__/` НЕ в коммите
- [ ] Все README файлы на месте
- [ ] `requirements.txt` актуален
- [ ] `LICENSE` файл присутствует
- [ ] `.gitignore` настроен правильно

### Финальная проверка:

```bash
# Показать все файлы, которые будут закоммичены
git status

# Показать различия с последним коммитом
git diff HEAD

# Показать, что игнорируется
git status --ignored
```

---

## 9. Быстрые команды (шпаргалка)

```bash
# Инициализация
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main

# Ежедневная работа
git status          # Проверка изменений
git add .           # Добавить всё
git commit -m "..." # Коммит
git push            # Отправить

# Теги версий
git tag -a v1.0.0 -m "Release"
git push origin --tags
```

---

## 10. Решение проблем

### Если случайно закоммитили лишнее:

```bash
# Удалить файл из коммита, но оставить локально
git rm --cached config.json
git commit -m "Remove config.json from repository"
git push
```

### Если нужно изменить последний коммит:

```bash
git commit --amend -m "Новое сообщение"
git push --force
```

### Если GitHub требует логин/пароль:

Используйте Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (repo permissions)
3. Используйте токен вместо пароля при push

---

## 11. Ссылки

- [GitHub Docs](https://docs.github.com/)
- [Git Book](https://git-scm.com/book)
- [Keep a Changelog](https://keepachangelog.com/) - для ведения истории изменений
- [Semantic Versioning](https://semver.org/) - для версионирования
