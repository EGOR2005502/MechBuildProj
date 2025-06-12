import sqlite3, os
from collections import defaultdict
from datetime import datetime

conn = sqlite3.connect('project.db')
conn.row_factory = sqlite3.Row
row = conn.cursor().execute("SELECT * FROM sklad")
row_mass = []
out = []


def main():
    # Установка соединения с базой данных SQLite
    conn = sqlite3.connect('project.db')
    cursor = conn.cursor()

    # Получение данных о наличии товаров на складе
    cursor.execute("SELECT item, volume FROM sklad")
    # Преобразование результатов в словарь {товар: количество}
    stock = {item: volume for item, volume in cursor.fetchall()}

    # Получение рецептов производства продуктов
    cursor.execute("SELECT product, components, speed_minut FROM kraft")
    # Преобразование результатов в словарь {продукт: {компоненты, скорость}}
    recipes = {row[0]: {'components': row[1], 'speed': row[2]} for row in cursor.fetchall()}

    # Получение списка продуктов с ненулевым объемом заказа
    cursor.execute("SELECT product, Volume FROM objective WHERE Volume > 0")
    ordered_products = {row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT Volume FROM objective WHERE Volume > 0")
    ordered_products_quantity = [row[0] for row in cursor.fetchall()]

    # Основные продукты для анализа (отсортированные по алфавиту)
    target_products = sorted(['электрочайник', 'пылесос', 'вентилятор'])
    num_prods = []

    # Функция для разбора строки компонентов в словарь {компонент: количество}
    def parse_components(comp_str):
        components = defaultdict(int)
        for part in comp_str.split(','):
            qty, item = part.strip().split('-', 1)
            components[item.strip()] += int(qty.strip())
        return dict(components)

    # Результаты будут храниться в двух списках: для продуктов с заказом и без
    results_with_order = []
    results_without_order = []

    # Анализ каждого целевого продукта
    for product in target_products:
        # Анализ продукта с текущим состоянием склада
        analysis = analyze_product(product, stock.copy(), recipes, parse_components)

        # Разделение результатов в зависимости от наличия заказа
        if product in ordered_products:
            results_with_order.append((product, analysis))
            num_prods.append(product)


    # Вывод результатов анализа
    #print("\n=== ПРОДУКЦИЯ С ЗАКАЗОМ ===")
    for product, analysis in results_with_order:
        print_product_analysis(product, analysis, recipes, stock, ordered_products_quantity[num_prods.index(product)])
        out.append([product, analysis, recipes, stock, ordered_products_quantity[num_prods.index(product)]])




    '''print("\n=== ПРОДУКЦИЯ БЕЗ ЗАКАЗА ===")
    for product, analysis in results_without_order:
        print_product_analysis(product, analysis, recipes, stock)'''

    # Закрытие соединения с базой данных
    penis = get_quantity()
    conn.close()

def destroy_bd():
    os.remove('project.db')

def get_quantity():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT IDitem, item, volume FROM sklad")  # Добавляем id в выборку
        rows = cursor.fetchall()
        # Преобразуем в список словарей
        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        return result
    finally:
        cursor.close()

def set_quantity(data):
    cursor = conn.cursor()
    try:
        for item in data:
            # Предполагаем, что в словаре есть ключ 'volume' и какой-то идентификатор строки (например, 'id')
            cursor.execute("UPDATE sklad SET volume = ? WHERE IDitem = ?",
                          (item['volume'], item['IDitem']))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при обновлении данных: {e}")
        return False

def get_prints():
    return(out)



def get_workers():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID, fio, age, telephone, post FROM worker")
        rows = cursor.fetchall()
        # Преобразуем в список словарей
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result
    except Exception as e:
        print(f"Ошибка при получении данных работников: {e}")
        return []
    finally:
        cursor.close()

def set_workers(data):
    cursor = conn.cursor()
    try:
        for worker in data:
            cursor.execute("""
                UPDATE worker 
                SET fio = ?,
                    age = ?,
                    telephone = ?,
                    post = ?
                WHERE ID = ?
            """, (
                worker['fio'],
                worker['age'],
                worker['telephone'],
                worker['post'],
                worker['ID']
            ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при обновлении данных работников: {e}")
        return False
    finally:
        cursor.close()


def get_objectives():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT IDorder, product, Volume, customer FROM objective")
        rows = cursor.fetchall()
        # Преобразуем в список словарей
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result
    except Exception as e:
        print(f"Ошибка при получении данных заказов: {e}")
        return []
    finally:
        cursor.close()


def update_objectives(data):
    cursor = conn.cursor()
    try:
        for objective in data:
            cursor.execute("""
                UPDATE objective 
                SET product = ?,
                    Volume = ?,
                    customer = ?
                WHERE IDorder = ?
            """, (
                objective['product'],
                objective['Volume'],
                objective['customer'],
                objective['IDorder']
            ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при обновлении данных заказов: {e}")
        return False
    finally:
        cursor.close()

def add_objective(objective_data):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO objective (product, Volume, customer)
            VALUES (?, ?, ?)
        """, (
            objective_data['product'],
            objective_data['Volume'],
            objective_data['customer']
        ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении заказа: {e}")
        return False
    finally:
        cursor.close()



def get_credentials():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT IDuser, login, password, date FROM credentials")
        rows = cursor.fetchall()
        # Преобразуем в список словарей
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result
    except Exception as e:
        print(f"Ошибка при получении данных учетных записей: {e}")
        return []
    finally:
        cursor.close()


def set_credentials(data):
    cursor = conn.cursor()
    try:
        for credential in data:
            cursor.execute("""
                UPDATE credentials 
                SET login = ?,
                    password = ?,
                    date = ?
                WHERE IDuser = ?
            """, (
                credential['login'],
                credential['password'],
                credential['date'],
                credential['IDuser']
            ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при обновлении учетных данных: {e}")
        return False
    finally:
        cursor.close()


def add_credential(credential_data):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO credentials (login, password, date)
            VALUES (?, ?, ?)
        """, (
            credential_data['login'],
            credential_data['password'],
            credential_data['date']
        ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении учетной записи: {e}")
        return False
    finally:
        cursor.close()


def delete_credential(user_id):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM credentials WHERE IDuser = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при удалении учетной записи: {e}")
        return False
    finally:
        cursor.close()


def get_logistics():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT IDorder, condition, content, quantity, date FROM logistics")
        rows = cursor.fetchall()
        # Преобразуем в список словарей
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result
    except Exception as e:
        print(f"Ошибка при получении данных логистики: {e}")
        return []
    finally:
        cursor.close()


def set_logistics(data):
    cursor = conn.cursor()
    try:
        for item in data:
            cursor.execute("""
                UPDATE logistics 
                SET condition = ?,
                    content = ?,
                    quantity = ?,
                    date = ?
                WHERE IDorder = ?
            """, (
                item['condition'],
                item['content'],
                item['quantity'],
                item['date'],
                item['IDorder']
            ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при обновлении данных логистики: {e}")
        return False
    finally:
        cursor.close()


def add_logistics_item(item_data):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO logistics (condition, content, quantity, date)
            VALUES (?, ?, ?, ?)
        """, (
            item_data['condition'],
            item_data['content'],
            item_data['quantity'],
            item_data['date']
        ))
        conn.commit()
        return cursor.lastrowid  # Возвращаем ID новой записи
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении записи логистики: {e}")
        return None
    finally:
        cursor.close()


def delete_logistics_item(order_id):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM logistics WHERE IDorder = ?", (order_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при удалении записи логистики: {e}")
        return False
    finally:
        cursor.close()


def get_logistics_by_order(order_id):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT IDorder, condition, content, quantity, date 
            FROM logistics 
            WHERE IDorder = ?
        """, (order_id,))
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
        return None
    except Exception as e:
        print(f"Ошибка при поиске записи логистики: {e}")
        return None
    finally:
        cursor.close()


def filter_logistics(filters=None):
    """
    Фильтрует записи логистики по заданным параметрам
    :param filters: словарь с параметрами фильтрации (все поля опциональны)
        Пример: {
            'date_range': ['01.05.2025', '05.05.2025'],  # обратите внимание на точки в дате
            'IDorder': 5,
            'content': 'Мониторы',
            'quantity': (10, 20),
            'condition': 'В пути'
        }
    :return: список отфильтрованных записей
    """
    cursor = conn.cursor()
    try:
        # Базовый запрос
        query = "SELECT IDorder, condition, content, quantity, date FROM logistics WHERE 1=1"
        params = []
        
        if filters:
            # Обработка диапазона дат (исправленный формат)
            if 'date_range' in filters:
                try:
                    date_from = datetime.strptime(filters['date_range'][0], '%d.%m.%Y').strftime('%d.%m.%Y')
                    date_to = datetime.strptime(filters['date_range'][1], '%d.%m.%Y').strftime('%d.%m.%Y')
                    query += " AND date BETWEEN ? AND ?"
                    params.extend([date_from, date_to])
                except ValueError as e:
                    print(f"Ошибка формата даты: {e}. Ожидается формат 'дд.мм.гггг'")
                    return []
            
            # Остальные фильтры без изменений
            if 'IDorder' in filters:
                query += " AND IDorder = ?"
                params.append(filters['IDorder'])
            
            if 'content' in filters:
                query += " AND content LIKE ?"
                params.append(f'%{filters["content"]}%')
            
            if 'quantity' in filters:
                if isinstance(filters['quantity'], tuple) and len(filters['quantity']) == 2:
                    query += " AND quantity BETWEEN ? AND ?"
                    params.extend(filters['quantity'])
                else:
                    query += " AND quantity = ?"
                    params.append(filters['quantity'])
            
            if 'condition' in filters:
                query += " AND condition = ?"
                params.append(filters['condition'])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    except Exception as e:
        print(f"Ошибка при фильтрации записей: {e}")
        return []
    finally:
        cursor.close()



def analyze_product(product, virtual_stock, recipes, parse_components):
    # Проверка наличия рецепта для продукта
    if product not in recipes:
        return {
            'can_produce': False,
            'limiting_factor': 0,
            'missing': {product: 1},
            'missing_basic': {product: 1},
            'crafted_analysis': None,
            'base_time': 0,
            'total_time': 0
        }

    # Разбор рецепта продукта
    main_recipe = parse_components(recipes[product]['components'])
    speed = recipes[product]['speed']
    # Расчет базового времени производства одной единицы
    base_time_per_unit = 1 / speed if speed > 0 else float('inf')

    # Инициализация переменных для хранения результатов анализа
    missing = defaultdict(int)
    missing_basic = defaultdict(int)
    can_produce = True
    limiting_factor = 0
    total_time = 0

    # Проверка наличия компонентов первого уровня
    for component, needed in main_recipe.items():
        available = virtual_stock.get(component, 0)
        if available < needed:
            # Если компонент можно произвести (есть его рецепт)
            if component in recipes:
                sub_recipe = parse_components(recipes[component]['components'])
                sub_speed = recipes[component]['speed']
                can_create_sub = True

                # Проверка наличия компонентов для производства недостающего компонента
                for sub_comp, sub_needed in sub_recipe.items():
                    if virtual_stock.get(sub_comp, 0) < sub_needed * (needed - available):
                        missing[sub_comp] += sub_needed * (needed - available) - virtual_stock.get(sub_comp, 0)
                        can_create_sub = False

                if can_create_sub:
                    # Расчет времени производства недостающих компонентов
                    units_to_create = needed - available
                    creation_time = units_to_create / sub_speed if sub_speed > 0 else float('inf')
                    total_time += creation_time

                    # Обновление виртуального склада после производства компонентов
                    for sub_comp, sub_needed in sub_recipe.items():
                        virtual_stock[sub_comp] -= sub_needed * (needed - available)
                    virtual_stock[component] = virtual_stock.get(component, 0) + (needed - available)
            else:
                # Если компонент базовый и его нельзя произвести
                missing[component] += needed - available
                missing_basic[component] += needed - available
                can_produce = False

    # Расчет максимального количества продукта, которое можно произвести
    if not missing:
        limiting_factor = min(
            virtual_stock.get(comp, 0) // needed
            for comp, needed in main_recipe.items()
        )
        total_time += limiting_factor * base_time_per_unit

    # Анализ возможности производства с дополнительным созданием компонентов
    crafted_analysis = None
    if missing and any(comp in recipes for comp in missing):
        crafted_analysis = analyze_with_crafting(product, virtual_stock.copy(), recipes, parse_components)

    # Возврат результатов анализа
    return {
        'can_produce': can_produce,
        'limiting_factor': limiting_factor,
        'missing': dict(missing),
        'missing_basic': dict(missing_basic),
        'crafted_analysis': crafted_analysis,
        'base_time': base_time_per_unit,
        'total_time': total_time if limiting_factor > 0 else 0
    }

def analyze_with_crafting(target_product, virtual_stock, recipes, parse_components):
    # Проверка наличия рецепта для целевого продукта
    if target_product not in recipes:
        return None

    # Разбор рецепта целевого продукта
    main_recipe = parse_components(recipes[target_product]['components'])
    speed = recipes[target_product]['speed']
    base_time_per_unit = 1 / speed if speed > 0 else float('inf')

    # Рекурсивная функция для создания компонентов
    def craft_component(component, needed_qty, time_tracker, missing_basic_tracker):
        # Если компонент базовый и его нельзя произвести
        if component not in recipes:
            missing_basic_tracker[component] = missing_basic_tracker.get(component, 0) + needed_qty
            return False

        # Разбор рецепта компонента
        recipe = parse_components(recipes[component]['components'])
        component_speed = recipes[component]['speed']
        can_craft = True

        # Проверка и создание подкомпонентов
        for sub_comp, sub_needed in recipe.items():
            available = virtual_stock.get(sub_comp, 0)
            required = sub_needed * needed_qty

            if available < required:
                if not craft_component(sub_comp, required - available, time_tracker, missing_basic_tracker):
                    can_craft = False
                    break

        if can_craft:
            # Расчет времени создания компонента
            creation_time = needed_qty / component_speed if component_speed > 0 else float('inf')
            time_tracker['time'] += creation_time

            # Обновление виртуального склада
            for sub_comp, sub_needed in recipe.items():
                virtual_stock[sub_comp] -= sub_needed * needed_qty
            virtual_stock[component] = virtual_stock.get(component, 0) + needed_qty
            return True
        return False

    # Основная логика анализа с созданием компонентов
    time_tracker = {'time': 0}
    missing_basic = defaultdict(int)
    possible = True

    # Проверка и создание необходимых компонентов
    for component, needed in main_recipe.items():
        available = virtual_stock.get(component, 0)
        if available < needed:
            if not craft_component(component, needed - available, time_tracker, missing_basic):
                possible = False
                break

    if not possible:
        return {
            'possible': False,
            'missing_basic': dict(missing_basic)
        }

    # Расчет максимального количества продукта
    limiting_factor = min(
        virtual_stock.get(comp, 0) // needed
        for comp, needed in main_recipe.items()
    )

    # Расчет общего времени производства
    total_time = time_tracker['time'] + limiting_factor * base_time_per_unit

    # Определение компонентов, которые нужно создать
    created_components = defaultdict(int)

    # Рекурсивная функция для подсчета создаваемых компонентов
    def track_creation(component, qty):
        if component in recipes:
            created_components[component] += qty
            recipe = parse_components(recipes[component]['components'])
            for sub_comp, sub_needed in recipe.items():
                track_creation(sub_comp, sub_needed * qty)

    # Подсчет всех компонентов, которые нужно создать
    for component, needed in main_recipe.items():
        available = virtual_stock.get(component, 0)
        if available < needed * limiting_factor:
            track_creation(component, needed * limiting_factor - available)

    # Возврат результатов анализа с созданием компонентов
    return {
        'possible': possible,
        'limiting_factor': limiting_factor,
        'created_components': dict(created_components),
        'total_time': total_time,
        'missing_basic': dict(missing_basic)
    }


def print_product_analysis(product, analysis, recipes, initial_stock, orders):

    print(f"\n Заказано {product} в кол-ве {orders}")

    # Вывод недостающих базовых компонентов
    if analysis['missing_basic']:
        print("\nНедостающие базовые компоненты:")
        for comp, qty in analysis['missing_basic'].items():
            available = initial_stock.get(comp, 0)
            print(f"- {comp}: нужно {qty} (доступно {available})")

    # Вывод информации о производстве без дополнительного создания компонентов
    if analysis['can_produce'] and analysis['limiting_factor'] > 0:
        print(f"\nМожно произвести сразу (без создания новых компонентов): {analysis['limiting_factor']} шт.")
        if analysis['total_time'] > analysis['base_time'] * analysis['limiting_factor']:
            print(f"Общее время производства: {analysis['total_time']:.2f} минут (включая создание компонентов)")
            print(f"Из них:")
            print(f"- Время сборки: {analysis['base_time'] * analysis['limiting_factor']:.2f} минут")
            print(f"- Время создания компонентов: {analysis['total_time'] - analysis['base_time'] * analysis['limiting_factor']:.2f} минут")
        else:
            print(f"Время производства: {analysis['total_time']:.2f} минут")
        print(f"Среднее время на единицу: {analysis['total_time'] / analysis['limiting_factor']:.2f} минут")
    elif analysis['missing']:
        if not analysis['missing_basic'] or set(analysis['missing'].keys()) != set(analysis['missing_basic'].keys()):
            print("\nНельзя произвести сразу. Недостающие компоненты:")
            for comp, qty in analysis['missing'].items():
                print(f"- {comp}: не хватает {qty} шт.")

    # Вывод информации о производстве с созданием компонентов
    if analysis['crafted_analysis']:
        crafted = analysis['crafted_analysis']
        if crafted['possible'] and crafted['limiting_factor'] > 0:
            print(f"\nПри дособирании компонентов можно произвести: {crafted['limiting_factor']} шт.")
            print(f"Общее время производства: {crafted['total_time']:.2f} минут")
            if crafted['limiting_factor'] > 0:
                print(f"Время на единицу: {crafted['total_time'] / crafted['limiting_factor']:.2f} минут")
            print("\nДля этого нужно создать:")
            for comp, qty in crafted['created_components'].items():
                print(f"- {comp}: {qty} шт.")

            if crafted['missing_basic'] and not all(comp in analysis['missing_basic'] for comp in crafted['missing_basic']):
                print("\nНедостающие базовые компоненты (невозможно произвести):")
                for comp, qty in crafted['missing_basic'].items():
                    available = initial_stock.get(comp, 0)
                    print(f"- {comp}: нужно {qty} (доступно {available})")
        else:
            if not analysis['missing_basic']:
                print("\nДаже с дособиранием невозможно произвести.")
                if crafted['missing_basic']:
                    print("Недостающие базовые компоненты:")
                    for comp, qty in crafted['missing_basic'].items():
                        available = initial_stock.get(comp, 0)
                        print(f"- {comp}: нужно {qty} (доступно {available})")
    elif analysis['missing'] and not any(comp in recipes for comp in analysis['missing']):
        print("\nНевозможно произвести - отсутствуют базовые компоненты.")

if __name__ == "__main__":
    main()