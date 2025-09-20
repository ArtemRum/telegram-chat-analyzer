import re
import json
import subprocess
import platform
from bs4 import BeautifulSoup
import os
from jinja2 import Template

class TelegramChatParser:
    def __init__(self):
        self.messages = []
        self.file_sources = {}
        self.current_filters = {
            'target_user': None,
            'target_message_id': None,
            'keyword': None,
            'source_file': None
        }
        self.current_results = None
    
    def clear_data(self):
        """Очищает все данные"""
        self.messages = []
        self.file_sources = {}
        self.current_filters = {
            'target_user': None,
            'target_message_id': None,
            'keyword': None,
            'source_file': None
        }
        self.current_results = None
        
    def parse_html(self, html_content, filename):
        """Парсит HTML файл Telegram чата"""
        soup = BeautifulSoup(html_content, 'html.parser')
        messages = soup.find_all('div', class_='message')
        
        for message in messages:
            message_id = message.get('id')
            if message_id:
                message_id = int(message_id.replace('message', ''))
            
            from_name_elem = message.find('div', class_='from_name')
            from_name = from_name_elem.text.strip() if from_name_elem else 'Unknown'
            
            text_elem = message.find('div', class_='text')
            text = text_elem.text.strip() if text_elem else ''
            
            date_elem = message.find('div', class_='date')
            date = date_elem.get('title') if date_elem else ''
            
            reply_to = None
            reply_to_elem = message.find('div', class_='reply_to')
            if reply_to_elem and reply_to_elem.find('a'):
                reply_link = reply_to_elem.find('a')
                if 'onclick' in reply_link.attrs:
                    match = re.search(r'GoToMessage\((\d+)\)', reply_link['onclick'])
                    if match:
                        reply_to = int(match.group(1))
            
            msg_data = {
                'id': message_id,
                'from': from_name,
                'text': text,
                'date': date,
                'reply_to': reply_to,
                'source_file': filename
            }
            
            self.messages.append(msg_data)
            # Сохраняем информацию о файле
            if filename not in self.file_sources:
                self.file_sources[filename] = {
                    'message_count': 0,
                    'users': set(),
                    'message_ids': set()
                }
            
            self.file_sources[filename]['message_count'] += 1
            self.file_sources[filename]['users'].add(from_name)
            if message_id:
                self.file_sources[filename]['message_ids'].add(message_id)
    
    def parse_json(self, json_content, filename):
        """Парсит JSON файл Telegram чата"""
        data = json.loads(json_content)
        
        if 'messages' in data:
            for msg in data['messages']:
                msg_data = {
                    'id': msg.get('id'),
                    'from': msg.get('from', 'Unknown'),
                    'text': msg.get('text', ''),
                    'date': msg.get('date', ''),
                    'reply_to': msg.get('reply_to_message_id'),
                    'source_file': filename
                }
                
                self.messages.append(msg_data)
                # Сохраняем информацию о файле
                if filename not in self.file_sources:
                    self.file_sources[filename] = {
                        'message_count': 0,
                        'users': set(),
                        'message_ids': set()
                    }
                
                self.file_sources[filename]['message_count'] += 1
                self.file_sources[filename]['users'].add(msg_data['from'])
                if msg_data['id']:
                    self.file_sources[filename]['message_ids'].add(msg_data['id'])
    
    def load_files(self, filenames):
        """Загружает несколько файлов"""
        for filename in filenames:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if filename.endswith('.html'):
                    self.parse_html(content, filename)
                else:
                    self.parse_json(content, filename)
                
                print(f"✓ Файл {filename} загружен ({self.file_sources[filename]['message_count']} сообщений)")
                
            except Exception as e:
                print(f"✗ Ошибка при чтении файла {filename}: {e}")
    
    def clear_data(self):
        """Очищает все данные"""
        self.messages = []
        self.file_sources = {}
        self.current_file = None
    
    def filter_messages(self, target_user=None, target_message_id=None, keyword=None, source_file=None):
        """Фильтрует сообщения и сохраняет параметры"""
        # Сохраняем текущие фильтры
        self.current_filters = {
            'target_user': target_user,
            'target_message_id': target_message_id,
            'keyword': keyword,
            'source_file': source_file
        }
        
        results = {
            'user_messages': [],
            'message_comments': [],
            'keyword_matches': []
        }
        
        for msg in self.messages:
            # Фильтр по исходному файлу
            if source_file and msg['source_file'] != source_file:
                continue
            
            # Фильтр по пользователю
            if target_user and msg['from'] == target_user:
                results['user_messages'].append(msg)
            
            # Фильтр по комментариям
            if target_message_id and msg['reply_to'] == target_message_id:
                results['message_comments'].append(msg)
            
            # Поиск по ключевому слову
            if keyword and keyword.lower() in msg['text'].lower():
                results['keyword_matches'].append(msg)
        
        self.current_results = results
        return results


def clear_console():
    """
    Очищает консоль кроссплатформенным способом
    """
    try:
        if platform.system() == "Windows":
            # Для Windows
            subprocess.run("cls", shell=True, check=True)
        else:
            # Для Linux/MacOS
            subprocess.run("clear", shell=True, check=True)
    except:
        # Fallback: просто выводим много пустых строк
        print("\n" * 100)

def get_available_users(parser, source_file=None):
    """Получает список уникальных пользователей"""
    users = set()
    for msg in parser.messages:
        if (source_file is None or msg['source_file'] == source_file) and msg['from']:
            users.add(msg['from'])
    return sorted(users)

def get_available_message_ids(parser, source_file=None):
    """Получает список доступных ID сообщений"""
    message_ids = []
    for msg in parser.messages:
        if (source_file is None or msg['source_file'] == source_file) and msg['id'] is not None:
            message_ids.append(msg['id'])
    return sorted(message_ids)

def get_available_files(parser):
    """Получает список загруженных файлов"""
    return list(parser.file_sources.keys())

def display_menu():
    """Отображает главное меню"""
    print("\n" + "="*60)
    print("          TELEGRAM CHAT PARSER - МНОГОФАЙЛОВЫЙ")
    print("="*60)
    print("1. Выбрать файлы для анализа")
    print("2. Показать загруженные файлы")
    print("3. Настроить фильтры")
    print("4. Выполнить анализ")
    print("5. Экспорт результатов")
    print("6. Показать статистику")
    print("7. Очистить все данные")
    print("8. Выход")
    print("="*60)

def choose_files():
    """Выбор файлов для анализа"""
    files = [f for f in os.listdir('.') if f.endswith(('.html', '.json'))]
    
    if not files:
        print("Файлы .html или .json не найдены в текущей директории!")
        return None
    
    print("\nДоступные файлы:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    print(f"{len(files) + 1}. Выбрать все файлы")
    
    try:
        choice = input("\nВыберите файлы через запятую (например: 1,3,5) или 'all' для всех: ")
        
        if choice.lower() == 'all':
            return files
        
        selected_indices = [int(x.strip()) - 1 for x in choice.split(',')]
        selected_files = []
        
        for index in selected_indices:
            if 0 <= index < len(files):
                selected_files.append(files[index])
            else:
                print(f"Неверный индекс: {index + 1}")
        
        return selected_files if selected_files else None
    
    except ValueError:
        print("Введите числа через запятую!")
        return None

def configure_filters(parser):
    """Настройка фильтров с сохранением текущих значений"""
    # Используем текущие фильтры как начальные значения
    filters = parser.current_filters.copy()
    
    files = get_available_files(parser)
    
    # Выбор файла для фильтрации
    if len(files) > 1:
        clear_console()
        print("\n--- ВЫБОР ФАЙЛА ДЛЯ ФИЛЬТРАЦИИ ---")
        print("0. Все файлы")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file} ({parser.file_sources[file]['message_count']} сообщений)")
        
        try:
            file_choice = int(input(f"Выберите файл [текущий: {filters['source_file'] or 'Все файлы'}]: ") or "0")
            if 1 <= file_choice <= len(files):
                filters['source_file'] = files[file_choice - 1]
            elif file_choice == 0:
                filters['source_file'] = None
            else:
                print("Неверный выбор! Сохраняется текущее значение.")
        except ValueError:
            print("Введите число! Сохраняется текущее значение.")
    
    source_file = filters['source_file']
    users = get_available_users(parser, source_file)
    message_ids = get_available_message_ids(parser, source_file)
    
    while True:
        clear_console()
        print(f"\n--- НАСТРОЙКА ФИЛЬТРОВ ---")
        print(f"Файл: {filters['source_file'] or 'Все файлы'}")
        print("1. Пользователь: {}".format(filters['target_user'] or 'Не выбрано'))
        print("2. ID сообщения для комментариев: {}".format(filters['target_message_id'] or 'Не выбрано'))
        print("3. Ключевое слово: {}".format(filters['keyword'] or 'Не выбрано'))
        print("4. Файл для фильтрации: {}".format(filters['source_file'] or 'Все файлы'))
        print("5. Применить фильтры и выйти")
        print("6. Сбросить все фильтры")
        print("7. Выйти без сохранения")
        
        choice = input("\nВыберите опцию: ")
        
        if choice == '1':
            clear_console()
            print("\nДоступные пользователи:")
            for i, user in enumerate(users, 1):
                print(f"{i}. {user}")
            print(f"{len(users) + 1}. Ввести вручную")
            print(f"{len(users) + 2}. Очистить")
            print(f"Текущее значение: {filters['target_user'] or 'Не выбрано'}")
            
            try:
                user_choice = input("Выберите пользователя: ")
                if user_choice:
                    user_choice = int(user_choice)
                    if 1 <= user_choice <= len(users):
                        filters['target_user'] = users[user_choice - 1]
                    elif user_choice == len(users) + 1:
                        new_user = input("Введите имя пользователя: ")
                        filters['target_user'] = new_user if new_user else None
                    elif user_choice == len(users) + 2:
                        filters['target_user'] = None
                    else:
                        print("Неверный выбор! Сохраняется текущее значение.")
            except ValueError:
                print("Введите число! Сохраняется текущее значение.")
        
        elif choice == '2':
            clear_console()
            print("\nДоступные ID сообщений (первые 10):")
            for msg_id in message_ids[:10]:
                print(f"- {msg_id}")
            if len(message_ids) > 10:
                print("... и еще", len(message_ids) - 10)
            print(f"Текущее значение: {filters['target_message_id'] or 'Не выбрано'}")
            
            try:
                msg_id = input("Введите ID сообщения (или Enter для отмены): ")
                if msg_id:
                    filters['target_message_id'] = int(msg_id)
                else:
                    filters['target_message_id'] = None
            except ValueError:
                print("ID должно быть числом! Сохраняется текущее значение.")
        
        elif choice == '3':
            clear_console()
            print(f"Текущее ключевое слово: {filters['keyword'] or 'Не выбрано'}")
            keyword = input("Введите ключевое слово: ")
            filters['keyword'] = keyword if keyword else None
        
        elif choice == '4':
            clear_console()
            print("\nДоступные файлы:")
            print("0. Все файлы")
            for i, file in enumerate(files, 1):
                print(f"{i}. {file}")
            print(f"Текущее значение: {filters['source_file'] or 'Все файлы'}")
            
            try:
                file_choice = input("Выберите файл: ")
                if file_choice:
                    file_choice = int(file_choice)
                    if 1 <= file_choice <= len(files):
                        filters['source_file'] = files[file_choice - 1]
                    elif file_choice == 0:
                        filters['source_file'] = None
                    else:
                        print("Неверный выбор! Сохраняется текущее значение.")
            except ValueError:
                print("Введите число! Сохраняется текущее значение.")
        
        elif choice == '5':
            # Применяем фильтры и выходим
            parser.filter_messages(**filters)
            print("Фильтры применены!")
            break
        
        elif choice == '6':
            # Сброс фильтров
            filters = {'target_user': None, 'target_message_id': None, 'keyword': None, 'source_file': None}
            parser.filter_messages(**filters)
            print("Фильтры сброшены!")
            break
        
        elif choice == '7':
            # Выход без сохранения (восстанавливаем старые фильтры)
            print("Изменения отменены.")
            break
        
        else:
            print("Неверный выбор!")
    
    return filters

def export_results(results, format_type):
    """Экспорт результатов"""
    filename = input("Введите имя файла для экспорта (без расширения): ")
    
    if format_type == 'json':
        filename += '.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Результаты сохранены в {filename}")
    
    elif format_type == 'html':
        filename += '.html'
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Telegram Chat Analysis</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .section { margin-bottom: 40px; border-bottom: 2px solid #333; padding-bottom: 20px; }
                .message { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .user { font-weight: bold; color: #2c3e50; }
                .date { color: #7f8c8d; font-size: 0.9em; margin-bottom: 5px; }
                .text { margin-top: 5px; line-height: 1.4; }
                .count { background: #3498db; color: white; padding: 2px 6px; border-radius: 3px; }
                .source { color: #e74c3c; font-size: 0.8em; margin-top: 5px; }
            </style>
        </head>
        <body>
            <h1>Анализ Telegram Чата</h1>
            <p><strong>Общее количество сообщений:</strong> {{ total_messages }}</p>
            
            {% if user_messages %}
            <div class="section">
                <h2>Сообщения пользователя <span class="count">{{ user_messages|length }}</span></h2>
                {% for msg in user_messages %}
                <div class="message">
                    <div class="user">{{ msg.from }}</div>
                    <div class="date">{{ msg.date }}</div>
                    <div class="text">{{ msg.text }}</div>
                    <div class="source">Источник: {{ msg.source_file }}</div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if message_comments %}
            <div class="section">
                <h2>Комментарии к сообщению <span class="count">{{ message_comments|length }}</span></h2>
                {% for msg in message_comments %}
                <div class="message">
                    <div class="user">{{ msg.from }}</div>
                    <div class="date">{{ msg.date }}</div>
                    <div class="text">{{ msg.text }}</div>
                    <div class="source">Источник: {{ msg.source_file }}</div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if keyword_matches %}
            <div class="section">
                <h2>Сообщения с ключевым словом <span class="count">{{ keyword_matches|length }}</span></h2>
                {% for msg in keyword_matches %}
                <div class="message">
                    <div class="user">{{ msg.from }}</div>
                    <div class="date">{{ msg.date }}</div>
                    <div class="text">{{ msg.text }}</div>
                    <div class="source">Источник: {{ msg.source_file }}</div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </body>
        </html>
        """
        
        template = Template(html_template)
        total_messages = len(results.get('user_messages', [])) + len(results.get('message_comments', [])) + len(results.get('keyword_matches', []))
        rendered_html = template.render(total_messages=total_messages, **results)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print(f"Результаты сохранены в {filename}")

def show_statistics(parser, results, filters):
    """Показывает статистику анализа"""
    source_file = filters.get('source_file')
    
    print("\n--- СТАТИСТИКА ---")
    print(f"Всего загружено файлов: {len(parser.file_sources)}")
    print(f"Всего сообщений: {len(parser.messages)}")
    
    if source_file:
        print(f"Сообщений в выбранном файле: {parser.file_sources[source_file]['message_count']}")
    
    print(f"\nРезультаты анализа:")
    if results:
        print(f"Сообщений пользователя: {len(results['user_messages'])}")
        print(f"Комментариев: {len(results['message_comments'])}")
        print(f"Сообщений с ключевым словом: {len(results['keyword_matches'])}")
    else:
        print("Фильтры не применены")
    
    # Статистика по файлам
    if len(parser.file_sources) > 1:
        print(f"\nСтатистика по файлам:")
        for file, stats in parser.file_sources.items():
            print(f"  {file}: {stats['message_count']} сообщений, {len(stats['users'])} пользователей")

def show_loaded_files(parser):
    """Показывает загруженные файлы"""
    if not parser.file_sources:
        print("Файлы не загружены!")
        return
    
    print("\n--- ЗАГРУЖЕННЫЕ ФАЙЛЫ ---")
    total_messages = 0
    total_users = set()
    
    for file, stats in parser.file_sources.items():
        print(f"* {file}")
        print(f"   Сообщений: {stats['message_count']}")
        print(f"   Пользователей: {len(stats['users'])}")
        total_messages += stats['message_count']
        total_users.update(stats['users'])
    
    print(f"\nИтого: {len(parser.file_sources)} файлов, {total_messages} сообщений, {len(total_users)} уникальных пользователей")

def main():
    parser = TelegramChatParser()
    
    while True:
        clear_console()
        print("\n" + "="*60)
        print("          TELEGRAM CHAT PARSER - МНОГОФАЙЛОВЫЙ")
        print("="*60)
        print("1. Выбрать файлы для анализа")
        print("2. Показать загруженные файлы")
        print("3. Настроить фильтры")
        print("4. Экспорт результатов")
        print("5. Показать статистику")
        print("6. Очистить все данные")
        print("7. Выход")
        print("="*60)
        
        # Показываем статус загруженных файлов
        if parser.file_sources:
            print(f"* Загружено файлов: {len(parser.file_sources)}")
        else:
            print("* Файлы не загружены")
        
        # Показываем статус фильтров
        if any(parser.current_filters.values()):
            print("* Активные фильтры: Да")
        else:
            print("* Активные фильтры: Нет")
        
        print("="*60)
        
        choice = input("Выберите опцию: ")
        
        if choice == '1':
            clear_console()
            selected_files = choose_files()
            if selected_files:
                parser.load_files(selected_files)
                # Автоматически применяем текущие фильтры к новым данным
                if any(parser.current_filters.values()):
                    parser.filter_messages(**parser.current_filters)
                    print("Текущие фильтры применены к новым данным!")
        
        elif choice == '2':
            clear_console()
            show_loaded_files(parser)
        
        elif choice == '3':
            if not parser.messages:
                print("Сначала загрузите файлы!")
            else:
                configure_filters(parser)
        
        elif choice == '4':
            if not parser.current_results:
                print("Сначала выполните анализ!")
            else:
                clear_console()
                print("\nФормат экспорта:")
                print("1. JSON")
                print("2. HTML")
                format_choice = input("Выберите формат: ")
                
                if format_choice == '1':
                    export_results(parser.current_results, 'json')
                elif format_choice == '2':
                    export_results(parser.current_results, 'html')
                else:
                    print("Неверный выбор!")
        
        elif choice == '5':
            if not parser.messages:
                print("Сначала загрузите файлы!")
            else:
                clear_console()
                show_statistics(parser, parser.current_results, parser.current_filters)
        
        elif choice == '6':
            parser.clear_data()
            print("Все данные очищены!")
        
        elif choice == '7':
            print("Выход из программы...")
            break
        
        else:
            print("Неверный выбор!")
        input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    main()
