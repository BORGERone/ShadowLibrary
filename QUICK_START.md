# Быстрая публикация Shadow Library на GitHub

## Команды для первого коммита

Откройте PowerShell или Command Prompt в папке проекта и выполните по порядку:

```powershell
# Перейдите в папку проекта
cd "g:\python\Shadow Library"

# Инициализируйте репозиторий
git init

# Добавьте все файлы (gitignore исключит лишние)
git add .

# Сделайте первый коммит
git commit -m "Initial commit: Shadow Library v1.0.0"

# Привяжите удалённый репозиторий (замените BORGERone на ваш username)
git remote add origin https://github.com/BORGERone/ShadowLibrary.git

# Переименуйте ветку в main
git branch -M main

# Отправьте на GitHub
git push -u origin main
```

---

## Для обновлений в будущем

```powershell
cd "g:\python\Shadow Library"

# Проверка изменений
git status

# Добавление всех изменений
git add .

# Коммит с описанием
git commit -m "Описание изменений"

# Отправка на GitHub
git push
```

---

## Что будет закоммичено ✅

- ✅ web_server.py, app_window.py, run_server.py
- ✅ common/, templates/, locales/
- ✅ README*.md (все языковые версии)
- ✅ LICENSE, requirements.txt, build.spec
- ✅ .gitignore, .gitattributes
- ✅ icon.ico, *.bat файлы

## Что НЕ будет закоммичено ❌

- ❌ config.json (персональные настройки)
- ❌ cracked_games.json (база данных)
- ❌ logs/, manifests/ (кеши)
- ❌ dist/, build/, __pycache__/ (сборки)
- ❌ .vscode/ (настройки IDE)
- ❌ *.exe, *.dll, *.rar (бинарники)

---

## Создание тега версии

```powershell
# Создать тег
git tag -a v1.0.0 -m "Shadow Library v1.0.0"

# Отправить теги на GitHub
git push origin --tags
```

---

## Если Git не установлен

1. Скачайте с https://git-scm.com/download/win
2. Установите (настройки по умолчанию)
3. Настройте:
   ```bash
   git config --global user.name "BORGER"
   git config --global user.email "your-email@example.com"
   ```

---

## Создание репозитория на GitHub

1. https://github.com/new
2. Имя: `ShadowLibrary`
3. **НЕ** инициализировать с README
4. Create repository
5. Выполните команды выше

---

## Полная инструкция

Смотрите `GITHUB_GUIDE.md` для подробной документации.
