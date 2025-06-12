from pygame.display import set_mode, set_caption, flip
from pygame.time import Clock
from pygame.font import init, SysFont
from pygame.locals import *
from pygame.mouse import get_pos
import pygame
import program
from models import Button, draw_text_centered
import sys


class Front:
    def __init__(self):
        self.run = True
        self.fps = 60
        self.backgrCol = (158, 165, 135)
        self.bazeButCol = (255, 165, 0)
        self.bazeButSize = (100, 40)
        self.fontSize = 15
        self.screen_width, self.screen_height = 1000, 600
        self.screen = set_mode((self.screen_width, self.screen_height))
        self.mouse_key = 0
        self.mouse_whiil = 0
        self.mouse_pos = (0, 0)
        self.clock = Clock()
        init()
        self.font = SysFont('lucidaconsole', self.fontSize)

        # Основные кнопки
        self.but_pred = Button((self.screen_width - 60, self.screen_height - 240), self.bazeButSize, 'Совет',
                               color=self.bazeButCol)
        self.but_inv = Button((self.screen_width - 60, self.screen_height - 180), self.bazeButSize, 'Склад',
                              color=self.bazeButCol)
        self.but_ord = Button((self.screen_width - 60, self.screen_height - 120), self.bazeButSize, 'Заказы',
                              color=self.bazeButCol)
        self.bakc_but = Button((self.screen_width - 110, self.screen_height - 50), self.bazeButSize, 'назад',
                               color=self.bazeButCol)
        self.output1 = Button((self.screen_width // 2 - 70, self.screen_height // 2), (800, 500), ' ',
                              color=(255, 255, 255))
        self.buttons = [self.but_pred, self.but_inv, self.but_ord, self.output1]

        # Параметры прокрутки
        self.scroll_offset = 0
        self.max_scroll = 0

        # Кнопки склада
        self.inventory_items = []
        self.init_inventory_buttons()

        # Кнопки заказов
        self.ord_but1, self.ord_but2 = [], []
        y = 20
        p = 150
        for i in range(3):
            self.ord_but1.append(Button((self.screen_width // 2 - 300 - p, y), (30, 30), '+',
                                        color=self.bazeButCol))
            y += 40
        y = 20
        for i in range(3):
            self.ord_but2.append(Button((self.screen_width // 2 - 300 + p, y), (30, 30), '-',
                                        color=self.bazeButCol))
            y += 40

        pygame.init()
        set_caption('Подручный')

    def init_inventory_buttons(self):
        """Инициализация кнопок склада"""
        self.inventory_items = []
        inv = program.get_quantity()
        y = 20
        p = 150
        item_height = 40

        for item_data in inv:
            item = {
                'plus_btn': Button((self.screen_width // 2 - 300 - p, y), (30, 30), '+', color=self.bazeButCol),
                'minus_btn': Button((self.screen_width // 2 - 300 + p, y), (30, 30), '-', color=self.bazeButCol),
                'id': item_data['IDitem'],  # Используем ID для обновления
                'name': item_data['item'],
                'count': item_data['volume'],
                'base_y': y
            }
            self.inventory_items.append(item)
            y += item_height

        self.max_scroll = len(inv) * item_height - self.screen_height + 100

    def save_inventory_changes(self):
        """Сохраняет изменения в базу данных"""
        inventory_data = []
        for item in self.inventory_items:
            inventory_data.append({
                'IDitem': item['id'],  # Используем ID для обновления
                'item': item['name'],
                'volume': item['count']
            })

        # Сохраняем изменения в базу
        success = program.set_quantity(inventory_data)
        if not success:
            print("Ошибка при сохранении изменений в базу данных")

    def update_inventory_text(self, item):
        """Обновляет текст для элемента инвентаря"""
        return f"{item['name']} {item['count']}"

    def predict(self):
        return 'Вставь функцию еблан'

    def update(self):
        flag_pred = False
        current_screen = 'main'
        while self.run:
            self.mouse_pos = get_pos()
            self.screen.fill(self.backgrCol)

            for ev in pygame.event.get():
                if ev.type == QUIT:
                    self.run = False
                    pygame.quit()
                    sys.exit()
                if ev.type == MOUSEBUTTONDOWN:
                    self.mouse_key = ev.button
                if ev.type == MOUSEWHEEL and current_screen == 'inventory':
                    # Обработка прокрутки колесика мыши
                    self.scroll_offset -= ev.y * 20
                    # Ограничение прокрутки
                    self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

            if current_screen == 'main':
                draw_text_centered(self.font, self.screen,
                                   'Анализируя данные о заказах и материалах на складе, нейросеть определяет какой'
                                   ' товар лучше производить',
                                   self.screen_width // 2 - 350, self.screen_height // 2 - 270)
                if self.but_pred.activate(self.mouse_pos, self.mouse_key):
                    sf = self.predict()
                    flag_pred = True
                if flag_pred:
                    self.output1.text = f'Рекомендовано производить:' + sf
                else:
                    self.output1.text = ' '
                if self.but_ord.activate(self.mouse_pos, self.mouse_key):
                    current_screen = 'orders'
                if self.but_inv.activate(self.mouse_pos, self.mouse_key):
                    current_screen = 'inventory'
                    flag_pred = False
                    self.scroll_offset = 0
                    # Обновляем данные при входе на экран склада
                    self.init_inventory_buttons()
                for butt in self.buttons:
                    butt.draw(self.screen, self.mouse_pos)


            elif current_screen == 'inventory':

                self.bakc_but.draw(self.screen, self.mouse_pos)

                if self.bakc_but.activate(self.mouse_pos, self.mouse_key):
                    self.save_inventory_changes()  # Сохраняем при выходе

                    current_screen = 'main'

                    continue

                for item in self.inventory_items:

                    visible_y = item['base_y'] - self.scroll_offset

                    if -40 < visible_y < self.screen_height:

                        # Обновляем позиции и прямоугольники кнопок

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

                        # Обработка нажатий

                        if item['plus_btn'].activate(self.mouse_pos, self.mouse_key):

                            item['count'] += 1

                        elif item['minus_btn'].activate(self.mouse_pos, self.mouse_key) and item['count'] > 0:

                            item['count'] -= 1

                        # Отрисовка

                        item['plus_btn'].draw(self.screen, self.mouse_pos)

                        item['minus_btn'].draw(self.screen, self.mouse_pos)

                        # Отображаем название и количество

                        text = f"{item['name']}: {item['count']}"

                        draw_text_centered(self.font, self.screen, text,

                                           self.screen_width // 2 - 300,

                                           visible_y + 15)
            elif current_screen == 'orders':
                self.bakc_but.draw(self.screen, self.mouse_pos)
                if self.bakc_but.activate(self.mouse_pos, self.mouse_key):
                    current_screen = 'main'

            self.mouse_key = 0
            flip()
            self.clock.tick(self.fps)