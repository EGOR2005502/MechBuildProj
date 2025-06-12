from pygame.display import set_mode, set_caption, flip
from pygame.time import Clock
from pygame.font import init, SysFont
from pygame.locals import *
from pygame.mouse import get_pos
from datetime import datetime
import pygame
import program
from models import Button, draw_text_centered
import sys


class Front:
    def __init__(self):
        self.run = True
        self.fps = 15
        self.backgrCol = (158, 165, 135)
        self.bazeButCol = (255, 165, 0)
        self.bazeButSize = (100, 40)
        self.fontSize = 15
        self.screen_width, self.screen_height = 1000, 600
        self.screen = set_mode((self.screen_width, self.screen_height))
        self.mouse_key = 0
        self.mouse_whiil = 0
        self.mouse_pos = (0, 0)
        self.ord_id = 0
        self.mouse_click_processed = False
        self.clock = Clock()
        init()
        self.font = SysFont('lucidaconsole', self.fontSize)

        # Основные кнопки
        self.but_pred = Button(self, (self.screen_width - 60, self.screen_height - 240), self.bazeButSize, 'Совет',
                               color=self.bazeButCol)
        self.but_inv = Button(self, (self.screen_width - 60, self.screen_height - 180), self.bazeButSize, 'Склад',
                              color=self.bazeButCol)
        self.but_ord = Button(self, (self.screen_width - 60, self.screen_height - 120), self.bazeButSize, 'Заказы',
                              color=self.bazeButCol)
        self.bakc_but = Button(self, (self.screen_width - 110, self.screen_height - 50), self.bazeButSize, 'назад',
                               color=self.bazeButCol)
        self.bakc_but1 = Button(self, (self.screen_width - 110, self.screen_height - 150), self.bazeButSize, 'назад',
                               color=self.bazeButCol)
        self.output1 = Button(self, (self.screen_width // 2 - 70, self.screen_height // 2), (800, 500), ' ',
                              color=(255, 255, 255))
        self.but_log = Button(self, (self.screen_width - 60, self.screen_height - 300), self.bazeButSize, 'Логистика',
                               color=self.bazeButCol)
        self.but_search = Button(self, (120, 100), (200, 30), 'Поиск...',
                               color=self.bazeButCol)
        self.butL_log = Button(self, (self.screen_width//2, self.screen_height//2 - 80), self.bazeButSize, ' ',
                               color=self.bazeButCol)
        self.butL_par = Button(self, (self.screen_width // 2, self.screen_height // 2), self.bazeButSize, ' ',
                               color=self.bazeButCol)
        self.butL_ent = Button(self, (self.screen_width // 2, self.screen_height // 2 + 90), self.bazeButSize, 'Вход',
                               color=self.bazeButCol)
        self.buttons = [self.but_pred, self.but_inv, self.but_ord, self.output1, self.but_log]
        self.log_buttons = [self.but_search]
        self.login_buttons = [self.butL_log, self.butL_par, self.butL_ent]

        # Параметры прокрутки
        self.scroll_offset = 0
        self.max_scroll = 0

        self.orders = []

        # Кнопки склада
        self.inventory_items = []
        self.inv_itm_names = []
        self.init_inventory_buttons()

        self.result = program.main()

        pygame.init()
        set_caption('Подручный')

    def is_date(self, inpt, form='%d.%m.%Y'):
        try:
            datetime.strptime(inpt, form)
            return True
        except ValueError:
            return False

    def is_range(self, s):
        parts = s.split('-')
        if len(parts) == 2:
            return parts[0].isdigit() and parts[1].isdigit()
        return False

    def extr_numb(self, s):
        if self.is_range(s):
            a, b = map(int, s.split('-'))
            return [a, b]
        return None


    def init_orders_buttons(self):
        self.orders = []
        ord = program.get_objectives()
        y = 20
        item_height = 50

        for order_data in ord:
            order = {
                'btn': Button(self, (self.screen_width // 2 - 300, y), (200, 30),
                              f"{order_data['customer']}", color=self.bazeButCol),
                'id': order_data['IDorder'],
                'customer': order_data['customer'],
                'product': order_data['product'],
                'volume': order_data['Volume'],
                'base_y': y
            }
            self.orders.append(order)
            y += item_height

        self.max_scroll = len(ord) * item_height - self.screen_height + 100

    def init_inventory_buttons(self):
        """Инициализация кнопок склада"""
        self.inventory_items = []
        inv = program.get_quantity()
        y = 20
        p = 150
        item_height = 40

        for item_data in inv:
            item = {
                'plus_btn': Button(self, (self.screen_width // 2 - 300 - p, y), (30, 30), '+', color=self.bazeButCol),
                'minus_btn': Button(self, (self.screen_width // 2 - 300 + p, y), (30, 30), '-', color=self.bazeButCol),
                'id': item_data['IDitem'],
                'name': item_data['item'],
                'count': item_data['volume'],
                'base_y': y
            }
            self.inventory_items.append(item)
            y += item_height
        for i in range(len(self.inventory_items)):
            self.inv_itm_names.append(self.inventory_items[i]['name'])

        self.max_scroll = len(inv) * item_height - self.screen_height + 100

    def save_inventory_changes(self):
        inventory_data = []
        for item in self.inventory_items:
            inventory_data.append({
                'IDitem': item['id'],
                'item': item['name'],
                'volume': item['count']
            })

        success = program.set_quantity(inventory_data)
        if not success:
            print("Ошибка при сохранении изменений в базу данных")

    def update_inventory_text(self, item):
        return f"{item['name']} {item['count']}"

    def predict(self):
        return 'Вставь функцию еблан'

    def update(self):
        result = None
        flag_pred = False
        current_screen = 'login'
        self.scroll_offset_main = 0
        self.max_scroll_main = 0
        search_text = "Поиск..."
        is_search_active = False
        input_string = ""

        while self.run:
            self.mouse_pos = get_pos()
            self.screen.fill(self.backgrCol)

            for ev in pygame.event.get():
                if ev.type == QUIT:
                    self.run = False
                    pygame.quit()
                    sys.exit()

                if ev.type == MOUSEBUTTONDOWN:
                    if ev.button == 1 and not self.mouse_click_processed:
                        self.mouse_key = ev.button
                        self.mouse_click_processed = True

                        if current_screen == 'logistics' and self.but_search.rect.collidepoint(self.mouse_pos):
                            if not is_search_active:
                                is_search_active = True
                                input_string = ""
                                self.but_search.text = "|"
                            else:
                                is_search_active = False
                                if not input_string:
                                    self.but_search.text = search_text
                                else:
                                    print(f"Поиск по: {input_string}")
                                    if not is_search_active and not input_string:
                                        self.but_search.text = search_text
                                    if ('принято' or 'Принято') in input_string:
                                        print('принято')
                                        result = program.filter_logistics({'condition': 'принято'})
                                    elif ('отправлено' or 'Отправлено') in input_string:
                                        print('отправлено')
                                        result = program.filter_logistics({'condition': 'отправлено'})
                                    elif input_string in self.inv_itm_names:
                                        print('имя')
                                        result = program.filter_logistics({'content': input_string})
                                    elif self.is_date(input_string):
                                        print('дата')
                                        result = program.filter_logistics({'date_range': [str(input_string), str(input_string)]})
                                    elif self.is_range(input_string):
                                        print('количество')
                                        a = self.extr_numb(input_string)
                                        result = program.filter_logistics({'quantity': (a[0], a[1])})
                                    else:
                                        result = None
                                        draw_text_centered(self.font, self.screen, 'Ничего не нашлось', 85, 150)
                                    self.but_search.text = input_string

                elif ev.type == MOUSEBUTTONUP:
                    self.mouse_click_processed = False

                if ev.type == KEYDOWN and is_search_active:
                    if ev.key == K_RETURN:
                        is_search_active = False
                        if not input_string:
                            self.but_search.text = search_text
                    elif ev.key == K_BACKSPACE:
                        input_string = input_string[:-1]
                    else:
                        if ev.unicode.isprintable():
                            input_string += ev.unicode

                    if is_search_active:
                        self.but_search.text = input_string + "|" if input_string else "|"

                # Прокрутка
                if ev.type == MOUSEWHEEL:
                    if current_screen == 'main' and flag_pred and self.output1.rect.collidepoint(self.mouse_pos):
                        self.scroll_offset_main -= ev.y * 20
                        self.scroll_offset_main = max(0, min(self.scroll_offset_main, self.max_scroll_main))
                    elif current_screen in ['orders', 'inventory']:
                        self.scroll_offset -= ev.y * 20
                        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

            if current_screen == 'main':
                for butt in self.buttons:
                    butt.draw()
                draw_text_centered(self.font, self.screen, 'Окно вывода', 85, 70)

                if self.but_pred.activate():
                    self.result = program.main()
                    flag_pred = True
                    text_height = 30*len(self.result)+sum(len(i) * 30 for i in self.result)
                    self.max_scroll_main = max(0, text_height - 400)

                if flag_pred:
                    visible_y = 100 - self.scroll_offset_main
                    for i in self.result:
                        if visible_y + 30 >= 100 and visible_y <= 500:
                            draw_text_centered(self.font, self.screen, '_' * 88,
                                               self.screen_width // 2 - 70, visible_y)
                        visible_y += 30
                        for j in i:
                            if visible_y >= 100 and visible_y <= 500:
                                draw_text_centered(self.font, self.screen, j,
                                                   self.screen_width // 2 - 70, visible_y)
                            visible_y += 30
                else:
                    self.output1.text = ' '

                if self.but_ord.activate():
                    current_screen = 'orders'
                    self.init_orders_buttons()
                    self.scroll_offset = 0

                if self.but_log.activate():
                    current_screen = 'logistics'
                    self.scroll_offset = 0

                if self.but_inv.activate():
                    current_screen = 'inventory'
                    flag_pred = False
                    self.scroll_offset = 0
                    self.init_inventory_buttons()
                    self.max_scroll = max(0, len(self.inventory_items) * 40 - (self.screen_height - 100))


            elif current_screen == 'inventory':
                self.bakc_but.draw()
                if self.bakc_but.activate():
                    self.save_inventory_changes()
                    program.set_quantity(self.inventory_items)
                    current_screen = 'main'
                    continue
                for item in self.inventory_items:
                    visible_y = item['base_y'] - self.scroll_offset
                    if -40 < visible_y < self.screen_height:
                        item['plus_btn'].y = visible_y
                        item['minus_btn'].y = visible_y
                        item['plus_btn'].rect = item['plus_btn'].create_rect_centered(
                            item['plus_btn'].width, item['plus_btn'].height)
                        item['plus_btn'].rect2 = item['plus_btn'].create_rect_centered(
                            item['plus_btn'].width + 6, item['plus_btn'].height + 6)
                        item['minus_btn'].rect = item['minus_btn'].create_rect_centered(
                            item['minus_btn'].width, item['minus_btn'].height)
                        item['minus_btn'].rect2 = item['minus_btn'].create_rect_centered(
                            item['minus_btn'].width + 6, item['minus_btn'].height + 6)
                        if item['plus_btn'].activate():
                            item['count'] += 1
                        elif item['minus_btn'].activate() and item['count'] > 0:
                            item['count'] -= 1
                        item['plus_btn'].draw()
                        item['minus_btn'].draw()
                        text = f"{item['name']}: {item['count']}"
                        draw_text_centered(self.font, self.screen, text,
                                           self.screen_width // 2 - 300,
                                           visible_y + 15)
            elif current_screen == 'orders':
                self.bakc_but.draw()
                if self.bakc_but.activate():
                    current_screen = 'main'
                    continue
                for order in self.orders:
                    visible_y = order['base_y'] - self.scroll_offset

                    if -40 < visible_y < self.screen_height:
                        order['btn'].y = visible_y
                        order['btn'].rect = order['btn'].create_rect_centered(
                            order['btn'].width, order['btn'].height)
                        order['btn'].rect2 = order['btn'].create_rect_centered(
                            order['btn'].width + 6, order['btn'].height + 6)

                        if order['btn'].activate():
                            self.ord_id = order['id'] - 1
                            current_screen = 'ord_info'
                            print(f"Выбран заказ: {order['customer']} - {order['product']}")

                        order['btn'].draw()
            elif current_screen == 'ord_info':
                self.bakc_but1.draw()
                if self.bakc_but1.activate():
                    current_screen = 'orders'
                    continue
                draw_text_centered(self.font, self.screen, f'Заказ от: {self.orders[self.ord_id]['customer']}',
                                   40, 40)
                draw_text_centered(self.font, self.screen, f'Заказывает: {self.orders[self.ord_id]['product']}',
                                   40, 80)
                draw_text_centered(self.font, self.screen, f'В количестве: {self.orders[self.ord_id]['volume']}',
                                   40, 120)
            elif current_screen == 'logistics':
                self.bakc_but.draw()
                for butt in self.log_buttons:
                    butt.draw()

                if self.bakc_but.activate():
                    current_screen = 'main'
                    continue

                draw_text_centered(self.font, self.screen, 'Поиск по поставкам', 85, 70)
                if result is not None:
                    y = 150
                    for res in result:
                        draw_text_centered(self.font, self.screen, 'Номер заказа: ' + str(res['IDorder']), 85, y)
                        draw_text_centered(self.font, self.screen, 'Состояние: ' + res['condition'], 85, y+30)
                        draw_text_centered(self.font, self.screen, 'Наименование: ' + res['content'], 85, y+60)
                        draw_text_centered(self.font, self.screen, 'Количество: ' + str(res['quantity']), 85, y+90)
                        draw_text_centered(self.font, self.screen, 'Дата: ' + res['date'], 85, y+120)
                        y += 150
            elif current_screen == 'login':
                draw_text_centered(self.font, self.screen, 'Имя пользователя', self.screen_width // 2,
                                   self.screen_height // 2 - 110)
                draw_text_centered(self.font, self.screen, 'Пароль', self.screen_width // 2,
                                   self.screen_height // 2 - 30)
                if self.butL_ent.activate():
                    current_screen = 'main'
                for but in self.login_buttons:
                    but.draw()
                pass

            self.mouse_key = 0
            flip()
            self.clock.tick(self.fps)
