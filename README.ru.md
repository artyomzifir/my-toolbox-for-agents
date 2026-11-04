# Goose Research Kit для Ubuntu

Новый способ установки описан в [README.md](README.md). Ниже сохранена ручная инструкция из архива, сверенная 2 ноября 2026 года.

Архив объединяет установку Goose, настройки Playwright и Docling, шаблоны состояния и библиотеку из 194 исходных навыков. Правила поиска по библиотеке уже входят в `.goosehints`. В разделе 9 описаны Caveman, RTK OSS и сравнение расхода по API.

Распакуй `goose-research-kit.zip`. Команды проекта запускай из появившейся папки `goose-research-kit`. Если Goose уже установлен, переходи к отсутствующим зависимостям и настройкам.

## 1. Системные зависимости и Goose

Команды ниже выполняются в терминале Ubuntu от обычного пользователя. `sudo` используется только для системных пакетов и зависимостей браузера.

```bash
sudo apt update
sudo apt install -y curl ca-certificates git python3 python3-venv poppler-utils unzip

curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh -o /tmp/goose-install.sh
CONFIGURE=false bash /tmp/goose-install.sh
export PATH="$HOME/.local/bin:$PATH"
goose --version
goose configure
```

В `goose configure` настрой API-провайдера, введи его ключ и выбери доступную модель с поддержкой tool calling. Подойдут прямые API-провайдеры или поддерживаемый агрегатор. Ключ вводи в интерфейсе настройки Goose; в файлах этого комплекта ключей нет.

Для desktop скачай DEB по ссылке Linux на [официальной странице установки](https://goose-docs.ai/docs/getting-started/installation/). Перейди в каталог скачивания и выполни `sudo apt install ./ИМЯ_СКАЧАННОГО_ФАЙЛА.deb`, подставив точное имя. `apt` сможет установить зависимости пакета. CLI и desktop запускаются отдельно.

Если CLI уже установлен, сначала выполни `goose update`. Эта инструкция опирается на актуальные функции, включая встроенный `web-search`.

## 2. Node.js и браузер

Если у тебя уже есть рабочий Node.js 20+ и npm, установку nvm можно пропустить. Предлагаемый вариант для чистой системы — Node.js 24 через nvm:

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh -o /tmp/research-nvm-install.sh
bash /tmp/research-nvm-install.sh
```

Открой новый терминал, затем:

```bash
nvm install 24
nvm use 24
node --version
npm --version
```

Установи Playwright MCP в отдельный каталог. Браузер устанавливается через Playwright из того же npm-дерева, чтобы использовать совместимую версию:

```bash
mkdir -p "$HOME/.local/share/goose-research-browser"
cd "$HOME/.local/share/goose-research-browser"
npm init -y
npm install @playwright/mcp@latest
./node_modules/.bin/playwright install --with-deps firefox
```

Используется управляемый Playwright Firefox. Он имеет отдельный профиль и не требует расширения в твоём обычном браузере. Подключение к уже открытым личным вкладкам — отдельная настройка.

Сохрани созданный `package-lock.json`: он фиксирует установленные зависимости. Последующее воспроизведение этой установки выполняется через `npm ci` и повторную установку браузера, а не новым выбором `latest`.

## 3. Python-инструменты и документы

Установи uv, если его ещё нет:

```bash
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/research-uv-install.sh
sh /tmp/research-uv-install.sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

Распакуй комплект и перейди в его каталог. Все дальнейшие команды проекта выполняются оттуда:

```bash
cd /ПУТЬ/К/goose-research-kit
uv init --bare --python 3.12 --vcs none
uv add docling python-docx openpyxl pandas matplotlib
uv run docling --help
```

Docling разбирает PDF и другие документы; python-docx/openpyxl нужны для создания Word/Excel, pandas/matplotlib — для анализа и графиков. Зависимости находятся в окружении этого проекта. `uv.lock` нужно сохранить.

Для проверки положи настоящий PDF в `papers/`:

```bash
mkdir -p papers extracted artifacts
uv run docling convert papers/example.pdf --to md --to json --output extracted --device cpu
```

Здесь `example.pdf` заменяется именем твоего файла. Первый запуск может загружать модели и занимать заметное время. Если установленная версия Docling использует старый интерфейс без подкоманды `convert`, проверь `uv run docling --help` и используй `uv run docling papers/example.pdf --to md --to json --output extracted --device cpu`.

Для визуальной сверки страницы PDF:

```bash
pdftoppm -f 1 -singlefile -scale-to 1600 -png papers/example.pdf artifacts/page-1
```

Сложные таблицы, формулы и графики нужно сверять с исходными страницами. Отдельный Docling MCP для этого старта не требуется: Developer запускает CLI.

## 4. Конфигурация Goose

Полностью закрой Goose Desktop перед ручным редактированием. Основной конфиг Ubuntu: `~/.config/goose/config.yaml`. Сначала сделай резервную копию:

```bash
cp -p "$HOME/.config/goose/config.yaml" "$HOME/.config/goose/config.yaml.before-research-$(date +%Y%m%d-%H%M%S)"
python3 print-config.py > goose-settings.generated.yaml
```

Генератор требует установленные `node`, `uv` и браузерный npm-каталог из шага 2. Его результат содержит реальные абсолютные пути, поэтому запуск браузерного MCP не зависит от загрузки nvm в GUI.

Открой `goose-settings.generated.yaml` и добавь его поля в существующий `config.yaml`:

- настройки `GOOSE_*` размещаются на корневом уровне;
- если `GOOSE_SEARCH_PATHS` уже есть, добавь пути в существующий список;
- запись `playwright` помести внутрь существующего `extensions`;
- сохрани API-провайдера, модель, ключи, другие расширения и настройки;
- обновляй существующие ключи вместо создания дубликатов.

Это фрагмент для объединения, а не замена всего конфига.

Начальные лимиты: 30 итераций основного агента, 10 — для дочернего, максимум один одновременно, сжатие при 60% контекста. Они служат стартом для испытаний, а не оптимумом для всех задач. Отдельные настройки дочерних задач могут переопределять их лимит. Показанная стоимость в CLI является оценкой. Эти настройки не создают жёсткий денежный лимит.

Перезапусти Desktop и CLI после изменения конфигурации.

## 5. Какие расширения включить

В Desktop открой `Extensions`. В CLI: `goose configure` → добавление/переключение расширений.

| Компонент | Действие | Зачем |
|---|---|---|
| Developer | Включить встроенный | Файлы, терминал, Python, Docling |
| Skills | Включить встроенный | Загрузка skill `web-search` |
| Todo | Включить встроенный | Текущий план |
| Chat Recall | Включить встроенный | Поиск по предыдущим сессиям |
| Top of Mind | Включить встроенный | Постоянная краткая инструкция и состояние для CLI-обёртки |
| Playwright | Добавить внешнюю stdio-запись из генератора | Навигация, динамические страницы, визуальная проверка |

В актуальном Goose `web-search` встроен: DuckDuckGo не требует API-ключа; skill также поддерживает Tavily и SearXNG. Проверь:

```bash
goose skills list
```

Если `web-search` отсутствует, обнови Goose и проверь Skills. В сессии можно явно попросить использовать `web-search`; CLI также поддерживает `/skills web-search`.

Tavily может потребовать отдельный ключ и оплату. SearXNG требует работающего инстанса. Для первого прогона используй доступный встроенный поиск; при проблемах с полнотой или доступностью подключай один альтернативный backend. Автоматический fallback и его настройки нужно проверять в установленной версии skill.

OpenAlex пока доступен агенту как веб-источник; отдельный структурированный OpenAlex-адаптер в комплект не входит.

## 6. Контекст проекта и запуск

В каталоге уже есть `.goosehints`, `PROJECT_STATE.md` и `SOURCES.md`. Заполни цель и ограничения в `PROJECT_STATE.md` перед началом. Состояние должно оставаться коротким: ориентир 1–2 тысячи токенов. Полные статьи и результаты инструментов сохраняются отдельными файлами.

Библиотека доступна для поиска сразу после распаковки. Подключи семь навыков `research-core`, если хочешь, чтобы Goose видел их как нативные skills. Начни новую сессию после подключения.

```bash
python3 portable-research-library/catalog.py verify
python3 portable-research-library/catalog.py activate \
  --profile research-core --project . --apply
goose skills list
```

Другие профили и зависимости описаны в руководстве библиотеки. [Руководство библиотеки](portable-research-library/README.ru.md)

Запуск CLI:

```bash
bash start-research.sh
```

Обёртка запускает сессию из каталога проекта, подмешивает `PROJECT_STATE.md` каждый ход через `GOOSE_MOIM_MESSAGE_FILE` и устанавливает лимит трёх одинаковых последовательных вызовов. Для продолжения:

```bash
bash start-research.sh --resume
```

В Desktop выбери этот же каталог как рабочую папку новой сессии. `.goosehints` загрузится как инструкция проекта. Запуск desktop из меню не наследует переменные обёртки CLI: постоянная инструкция из конфига просит читать состояние при начале и продолжении работы. Для инъекции самого файла каждый ход в Desktop можно дополнительно задать `GOOSE_MOIM_MESSAGE_FILE` абсолютным путём в конфиге, но тогда этот путь будет действовать и для других проектов до его изменения.

Файлы и инструкции помогают удерживать контекст; это не автоматическая система базы знаний. Сохранение состояния пока выполняет агент по инструкции. `--max-tool-repetitions` ловит одинаковые последовательные вызовы, а не все смысловые циклы. Одновременные CLI/Desktop-сессии не должны независимо перезаписывать общий `PROJECT_STATE.md`.

## 7. Первый проверочный запрос

Сначала попроси перечислить обнаруженные skills и инструменты Playwright и убедись, что модель действительно выполняет вызовы инструментов.

Затем дай маленькую задачу, например:

> Используй web-search. Найди три первоисточника по одной узкой теме моего проекта. Прочитай поддерживающие вывод фрагменты; одну страницу открой через Playwright. Сохрани источники и статус чтения в SOURCES.md. Сделай короткую сравнительную таблицу. Отдельно отметь гипотезы и неизвестное. Обнови PROJECT_STATE.md. Если инструмент не работает, покажи причину и частичный результат.

После этого проверь настоящий PDF, а затем перезапуск сессии и сохранность цели. Масштабный исследовательский прогон имеет смысл после этих проверок.

## 8. Windows

Goose поддерживает нативные Desktop и CLI на Windows. Используй Windows-инструкцию на официальной странице, Windows-версии Node и uv, затем повтори настройку расширения с Windows-путями. Bash-команды и `start-research.sh` из этого комплекта предназначены для Ubuntu. Для первого переноса можно использовать WSL2 и весь Linux-набор внутри него; соединение нативного Windows Desktop с инструментами внутри WSL — отдельная настройка, автоматически здесь не настроено.

## 9. Расход токенов

Базовая конфигурация подгружает несколько навыков под задачу, ограничивает повторы и просит сохранять длинные логи и извлечённые документы в файлы. Статусы остаются короткими. Для выводов сохраняются источники, оговорки и результаты проверки.

**Caveman.** В архиве исходный Apache-2.0 skill с закреплённой версией. Подключи его отдельно и начни новую сессию.

```bash
python3 portable-research-library/catalog.py activate \
  --profile token-style --project . --apply
```

В чате попроси «Используй skill caveman для коротких статусов. Итог исследования изложи обычным языком». Отключить стиль можно фразой `normal mode`. В небольшом тесте авторов разница базового Caveman с простой просьбой отвечать кратко была в пределах шума. Тест измерял длину ответа. [Тест Caveman](https://github.com/JuliusBrussee/caveman/blob/2e068f735253cce28256744804785f01887d9646/skills/caveman/README.md)

В профиле `focused-checks` доступны `investigate-first` для диагностики и `verify-and-stop` для достаточной проверки и остановки. Подключаются той же командой с другим именем профиля.

**RTK OSS.** Устанавливается отдельно и фильтрует вывод поддерживаемых Git, тестовых и сборочных команд до отправки модели. Если `rtk gain` уже работает, можно сразу пользоваться командами.

```bash
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh \
  -o /tmp/goose-rtk-install.sh
RTK_EDITION=oss sh /tmp/goose-rtk-install.sh
export PATH="$HOME/.local/bin:$PATH"
rtk gain
```

В Goose используй `rtk git status` в Git-репозитории или `rtk test uv run pytest` в проекте с pytest. Для спорных деталей проверь полный вывод. `rtk gain` оценивает сокращение вывода. Стоимость сравнивай по статистике API. [Инструкция RTK OSS](https://github.com/rtk-ai/rtk/blob/develop/INSTALL.md)

**MCP и контекст.** При большом числе подключённых расширений попробуй Code Mode, если он доступен в сборке Goose. Он подгружает описания нужных инструментов по запросу. Настройка видимости вывода в CLI регулирует отображение в терминале. Расход зависит от данных, отправленных модели. [Code Mode](https://goose-docs.ai/docs/guides/managing-tools/code-mode/) · [Видимость вывода](https://goose-docs.ai/docs/guides/managing-tools/adjust-tool-output/)

**Проверка расхода.** Возьми небольшой обзор и задачу с длинным логом. В свежих сессиях сохрани модель, reasoning и критерий завершения. Меняй по одному механизму за прогон. Сравни входные, кэшированные и выходные токены по метрикам провайдера, стоимость и сохранность доказательств.

## Источники

- [Goose: установка](https://goose-docs.ai/docs/getting-started/installation/)
- [Goose: API-провайдеры](https://goose-docs.ai/docs/getting-started/providers/)
- [Goose: конфигурация и stdio-расширения](https://goose-docs.ai/docs/guides/config-files/)
- [Goose: переменные окружения](https://goose-docs.ai/docs/guides/environment-variables/)
- [Goose: расширения](https://goose-docs.ai/docs/getting-started/using-extensions/)
- [Goose: встроенный web-search и skills](https://goose-docs.ai/docs/guides/context-engineering/using-skills/)
- [Goose: инструкции проекта](https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/)
- [Goose: постоянные инструкции](https://goose-docs.ai/docs/guides/context-engineering/using-persistent-instructions/)
- [Goose: CLI](https://goose-docs.ai/docs/guides/goose-cli-commands/)
- [nvm](https://github.com/nvm-sh/nvm)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Playwright MCP: package.json](https://github.com/microsoft/playwright-mcp/blob/main/package.json)
- [uv: установка](https://docs.astral.sh/uv/getting-started/installation/)
- [uv: инструменты](https://docs.astral.sh/uv/guides/tools/)
- [Docling: установка](https://docling-project.github.io/docling/getting_started/installation/)
- [Docling: CLI](https://docling-project.github.io/docling/reference/cli/)
