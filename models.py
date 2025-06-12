from pygame import font, Rect
from pygame.draw import rect


class Button:
    def __init__(self, position, scale, text, color=(0, 200, 0), text_color=(0, 0, 0),
                 visible=True):
        if visible:
            self.x = position[0]
            self.y = position[1]
        else:
            self.x = 10000
            self.y = 10000
        self.width = scale[0]
        self.height = scale[1]
        self.color = color
        c1 = 0 if color[0] - 20 < 0 else color[0] - 40
        c2 = 0 if color[1] - 20 < 0 else color[1] - 40
        c3 = 0 if color[2] - 20 < 0 else color[2] - 40
        self.color2 =(c1, c2, c3)
        self.text = text
        c1 = 255 if color[0] + 20 > 255 else color[0]+40
        c2 = 255 if color[1] + 20 > 255 else color[1]+40
        c3 = 255 if color[2] + 20 > 255 else color[2]+40
        self.target_color = (c1, c2, c3)
        self.active = False
        self.cf = color
        self.text_color = text_color
        self.rect = self.create_rect_centered(self.width, self.height)
        self.rect2 = self.create_rect_centered(self.width+6, self.height+6)
        self.color_changed = False
        self.visible = visible
        self.font = font.SysFont('lucidaconsole', 15)

    def draw(self, surface, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.color = self.target_color
        else:
            self.color = self.cf
        if self.visible:
            rect(surface, self.color2, self.rect2, 4, 10)
            rect(surface, self.color, self.rect, border_radius=10)
            draw_text_centered(self.font, surface, self.text, self.x, self.y)

    def create_rect_centered(self, w, h):
        top_left_x = self.x - w // 2
        top_left_y = self.y - h // 2
        return Rect(top_left_x, top_left_y, w, h)

    def activate(self, mouse_pos, mouse_key):
        return self.rect.collidepoint(mouse_pos) and mouse_key == 1


def draw_text_centered(font, screen, text, x, y, text_color=(0, 0, 0), padding=20):
    screen_width = screen.get_width()
    max_line_width = screen_width - 2 * padding  # Учитываем отступы слева и справа

    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        # Проверяем, помещается ли слово в текущую строку
        test_line = ' '.join(current_line + [word]) if current_line else word
        test_width = font.size(test_line)[0]

        if test_width <= max_line_width:
            current_line.append(word)
        else:
            # Если слово не помещается, начинаем новую строку
            if current_line:  # Добавляем текущую строку, если она не пустая
                lines.append(' '.join(current_line))
            # Если слово слишком длинное (длиннее max_line_width), разбиваем его
            if font.size(word)[0] > max_line_width:
                # Разбиваем слово на части, которые помещаются
                split_word = []
                current_part = ""
                for char in word:
                    test_part = current_part + char
                    if font.size(test_part)[0] <= max_line_width:
                        current_part = test_part
                    else:
                        split_word.append(current_part)
                        current_part = char
                if current_part:
                    split_word.append(current_part)
                # Первая часть добавляется к текущей строке (если она есть)
                if split_word:
                    lines.append(split_word[0])
                    current_line = split_word[1:] if len(split_word) > 1 else []
            else:
                current_line = [word]

    # Добавляем последнюю строку, если она не пустая
    if current_line:
        lines.append(' '.join(current_line))

    # Рассчитываем общую высоту текста для вертикального центрирования
    line_height = font.get_linesize()
    total_height = len(lines) * line_height
    start_y = y - total_height // 2  # Центрируем по вертикали

    # Отрисовываем каждую строку с учетом границ экрана
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, text_color)
        text_rect = text_surface.get_rect(center=(x, start_y + i * line_height))

        # Проверяем, не выходит ли текст за границы экрана
        if text_rect.left < padding:
            text_rect.left = padding  # Фиксируем левую границу
        elif text_rect.right > screen_width - padding:
            text_rect.right = screen_width - padding  # Фиксируем правую границу

        screen.blit(text_surface, text_rect)