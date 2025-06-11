import sqlite3
from collections import defaultdict


def main():
    conn = sqlite3.connect('project.db')
    cursor = conn.cursor()

    # Получаем данные из базы
    cursor.execute("SELECT item, volume FROM sklad")
    stock = {item: volume for item, volume in cursor.fetchall()}

    cursor.execute("SELECT product, components, speed_minut FROM kraft")
    recipes = {row[0]: {'components': row[1], 'speed': row[2]} for row in cursor.fetchall()}

    # Получаем продукты с ненулевым объемом заказа
    cursor.execute("SELECT product, Volume FROM objective WHERE Volume > 0")
    ordered_products = {row[0] for row in cursor.fetchall()}

    # Основные продукты для анализа
    target_products = sorted(['электрочайник', 'пылесос', 'вентилятор'])

    # Разбираем все компоненты на составляющие
    def parse_components(comp_str):
        components = defaultdict(int)
        for part in comp_str.split(','):
            qty, item = part.strip().split('-', 1)
            components[item.strip()] += int(qty.strip())
        return dict(components)

    # Результаты будем хранить раздельно
    results_with_order = []
    results_without_order = []

    for product in target_products:
        # Анализируем каждый основной продукт
        analysis = analyze_product(product, stock.copy(), recipes, parse_components)

        if product in ordered_products:
            results_with_order.append((product, analysis))
        else:
            results_without_order.append((product, analysis))

    # Выводим результаты
    print("\n=== ПРОДУКЦИЯ С ЗАКАЗОМ ===")
    for product, analysis in results_with_order:
        print_product_analysis(product, analysis, recipes, stock)

    print("\n=== ПРОДУКЦИЯ БЕЗ ЗАКАЗА ===")
    for product, analysis in results_without_order:
        print_product_analysis(product, analysis, recipes, stock)

    conn.close()


def analyze_product(product, virtual_stock, recipes, parse_components):
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

    # Получаем рецепт продукта
    main_recipe = parse_components(recipes[product]['components'])
    speed = recipes[product]['speed']
    base_time_per_unit = 1 / speed if speed > 0 else float('inf')

    missing = defaultdict(int)
    missing_basic = defaultdict(int)
    can_produce = True
    limiting_factor = 0
    total_time = 0

    # Проверяем компоненты первого уровня
    for component, needed in main_recipe.items():
        available = virtual_stock.get(component, 0)
        if available < needed:
            # Проверяем, можно ли создать недостающий компонент
            if component in recipes:
                sub_recipe = parse_components(recipes[component]['components'])
                sub_speed = recipes[component]['speed']
                can_create_sub = True

                for sub_comp, sub_needed in sub_recipe.items():
                    if virtual_stock.get(sub_comp, 0) < sub_needed * (needed - available):
                        missing[sub_comp] += sub_needed * (needed - available) - virtual_stock.get(sub_comp, 0)
                        can_create_sub = False

                if can_create_sub:
                    # Рассчитываем время на создание недостающих компонентов
                    units_to_create = needed - available
                    creation_time = units_to_create / sub_speed if sub_speed > 0 else float('inf')
                    total_time += creation_time

                    # Создаём недостающий компонент
                    for sub_comp, sub_needed in sub_recipe.items():
                        virtual_stock[sub_comp] -= sub_needed * (needed - available)
                    virtual_stock[component] = virtual_stock.get(component, 0) + (needed - available)
            else:
                missing[component] += needed - available
                missing_basic[component] += needed - available  # Добавляем в недостающие базовые
                can_produce = False

    if not missing:
        # Рассчитываем сколько можно произвести
        limiting_factor = min(
            virtual_stock.get(comp, 0) // needed
            for comp, needed in main_recipe.items()
        )
        total_time += limiting_factor * base_time_per_unit

    # Анализ с дособиранием компонентов
    crafted_analysis = None
    if missing and any(comp in recipes for comp in missing):
        crafted_analysis = analyze_with_crafting(product, virtual_stock.copy(), recipes, parse_components)

    return {
        'can_produce': can_produce,
        'limiting_factor': limiting_factor,
        'missing': dict(missing),
        'missing_basic': dict(missing_basic),  # Недостающие базовые компоненты
        'crafted_analysis': crafted_analysis,
        'base_time': base_time_per_unit,
        'total_time': total_time if limiting_factor > 0 else 0
    }


def analyze_with_crafting(target_product, virtual_stock, recipes, parse_components):
    if target_product not in recipes:
        return None

    main_recipe = parse_components(recipes[target_product]['components'])
    speed = recipes[target_product]['speed']
    base_time_per_unit = 1 / speed if speed > 0 else float('inf')

    # Рекурсивная функция для создания компонентов с расчетом времени
    def craft_component(component, needed_qty, time_tracker, missing_basic_tracker):
        if component not in recipes:
            missing_basic_tracker[component] = missing_basic_tracker.get(component, 0) + needed_qty
            return False

        recipe = parse_components(recipes[component]['components'])
        component_speed = recipes[component]['speed']
        can_craft = True

        for sub_comp, sub_needed in recipe.items():
            available = virtual_stock.get(sub_comp, 0)
            required = sub_needed * needed_qty

            if available < required:
                if not craft_component(sub_comp, required - available, time_tracker, missing_basic_tracker):
                    can_craft = False
                    break

        if can_craft:
            # Добавляем время создания этого компонента
            creation_time = needed_qty / component_speed if component_speed > 0 else float('inf')
            time_tracker['time'] += creation_time

            for sub_comp, sub_needed in recipe.items():
                virtual_stock[sub_comp] -= sub_needed * needed_qty
            virtual_stock[component] = virtual_stock.get(component, 0) + needed_qty
            return True
        return False

    # Основная логика
    time_tracker = {'time': 0}
    missing_basic = defaultdict(int)
    possible = True

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

    limiting_factor = min(
        virtual_stock.get(comp, 0) // needed
        for comp, needed in main_recipe.items()
    )

    # Добавляем время создания основного продукта
    total_time = time_tracker['time'] + limiting_factor * base_time_per_unit

    # Определяем что нужно создать
    created_components = defaultdict(int)

    def track_creation(component, qty):
        if component in recipes:
            created_components[component] += qty
            recipe = parse_components(recipes[component]['components'])
            for sub_comp, sub_needed in recipe.items():
                track_creation(sub_comp, sub_needed * qty)

    for component, needed in main_recipe.items():
        available = virtual_stock.get(component, 0)
        if available < needed * limiting_factor:
            track_creation(component, needed * limiting_factor - available)

    return {
        'possible': possible,
        'limiting_factor': limiting_factor,
        'created_components': dict(created_components),
        'total_time': total_time,
        'missing_basic': dict(missing_basic)
    }


def print_product_analysis(product, analysis, recipes, initial_stock):
    print(f"\n{product}:")

    # Убираем дублирование вывода недостающих компонентов
    if analysis['missing_basic']:
        print("\nНедостающие базовые компоненты:")
        for comp, qty in analysis['missing_basic'].items():
            available = initial_stock.get(comp, 0)
            print(f"- {comp}: нужно {qty} (доступно {available})")

    # Вывод информации о производстве без дособирания
    if analysis['can_produce'] and analysis['limiting_factor'] > 0:
        print(f"\nМожно произвести сразу (без создания новых компонентов): {analysis['limiting_factor']} шт.")
        if analysis['total_time'] > analysis['base_time'] * analysis['limiting_factor']:
            print(f"Общее время производства: {analysis['total_time']:.2f} минут (включая создание компонентов)")
            print(f"Из них:")
            print(f"- Время сборки: {analysis['base_time'] * analysis['limiting_factor']:.2f} минут")
            print(
                f"- Время создания компонентов: {analysis['total_time'] - analysis['base_time'] * analysis['limiting_factor']:.2f} минут")
        else:
            print(f"Время производства: {analysis['total_time']:.2f} минут")
        print(f"Среднее время на единицу: {analysis['total_time'] / analysis['limiting_factor']:.2f} минут")
    elif analysis['missing']:
        # Убираем дублирующий вывод, если уже показали недостающие базовые компоненты
        if not analysis['missing_basic'] or set(analysis['missing'].keys()) != set(analysis['missing_basic'].keys()):
            print("\nНельзя произвести сразу. Недостающие компоненты:")
            for comp, qty in analysis['missing'].items():
                print(f"- {comp}: не хватает {qty} шт.")

    # Вывод информации о производстве с дособиранием компонентов
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

            # Показываем только те недостающие компоненты, которые невозможно произвести
            if crafted['missing_basic'] and not all(
                    comp in analysis['missing_basic'] for comp in crafted['missing_basic']):
                print("\nНедостающие базовые компоненты (невозможно произвести):")
                for comp, qty in crafted['missing_basic'].items():
                    available = initial_stock.get(comp, 0)
                    print(f"- {comp}: нужно {qty} (доступно {available})")
        else:
            if not analysis['missing_basic']:  # Если уже показали выше, не повторяем
                print("\nДаже с дособиранием невозможно произвести.")
                if crafted['missing_basic']:
                    print("Недостающие базовые компоненты:")
                    for comp, qty in crafted['missing_basic'].items():
                        available = initial_stock.get(comp, 0)
                        print(f"- {comp}: нужно {qty} (доступно {available})")
    elif analysis['missing'] and not any(comp in recipes for comp in analysis['missing']):
        print("\nНевозможно произвести - отсутствуют базовые компоненты.")


def parse_components(comp_str):
    components = defaultdict(int)
    for part in comp_str.split(','):
        qty, item = part.strip().split('-', 1)
        components[item.strip()] += int(qty.strip())
    return dict(components)


if __name__ == "__main__":
    main()