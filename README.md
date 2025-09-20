# Telegram Chat Exporter Analyzer 🔍

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Export%20Analyzer-2CA5E0)](https://telegram.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Профессиональный инструмент для анализа экспортированных чатов из Telegram. Преобразуйте ваши JSON и HTML экспорты в структурированные данные и детальные отчеты.

## ✨ Возможности

- **📁 Мультиформатная поддержка** - работа с официальными JSON и HTML экспортами Telegram
- **👥 Анализ пользователей** - можно найти сообщения каждого участника чата
- **💬 Поиск по сообщениям** - мощная система фильтрации
- **📤 Гибкий экспорт** - JSON, HTML
- **🔍 Поиск по ключевым словам** - интеллектуальный поиск по содержимому (просто смотрит, есть ли это в сообщении :3)

## 📦 Быстрый старт

### Установка

1. Скачайте Python 3.8+ с [официального сайта](https://python.org)
2. Установите зависимости:
```bash
pip install bs4 jinja2
```

3. Скачайте скрипт:
```bash
git clone https://github.com/ArtemRum/telegram-chat-analyzer.git
cd telegram-chat-analyzer
```

### Как получить экспорт чата из Telegram

1. **Для личных чатов**: 
   - Откройте чат → три точки → Export chat history
   - Выберите формат JSON или HTML
   - Укажите диапазон дат

2. **Для групповых чатов**:
   - Требуются права администратора
   - Настройки группы → Export chat history

### Запуск анализа

```bash
python telegram_analyzer.py
```

## 🗂️ Поддерживаемые форматы экспорта

### ✅ JSON Export
```json
{
  "name": "Chat with User",
  "type": "personal_chat",
  "messages": [
    {
      "id": 123,
      "type": "message",
      "date": "2023-09-15T10:30:00",
      "from": "User Name",
      "text": "Hello world"
    }
  ]
}
```

### ✅ HTML Export
```html
<div class="message">
  <div class="from_name">User Name</div>
  <div class="date" title="15.09.2023 10:30:00 UTC+03:00">10:30</div>
  <div class="text">Hello world</div>
</div>
```

## 🎯 Ключевые функции анализа

### Статистика чата
- **Общее количество сообщений**

### Поиск и фильтрация
- **По пользователю** - сообщения конкретного участника
- **По ключевым словам** - поиск по содержимому


## 📄 Лицензия

ЕЁ НЕТ, ПХПХПХ

## 🌟 Поддержка проекта

Если проект вам помог:
- ⭐ Поставьте звезду на GitHub
- 🐛 Сообщайте о багах

---

я сделал этот проект по приколу. :3

*Для вопросов и предложений: создайте issue в репозитории проекта*
