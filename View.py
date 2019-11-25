import pygame


class Icon(pygame.sprite.Sprite):
    def __init__(self, icon_image):
        super().__init__()
        self.image = pygame.image.load("images/" + icon_image)
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image_file_name, pos):
        super().__init__()
        # Load the png image with transparency
        self.image = pygame.image.load("images/" + image_file_name)
        self.image = self.image.convert_alpha()
        # Move the rect to make sure it follows the image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos)
        self.pos = pos


class TextSprite(pygame.sprite.Sprite):
    def __init__(self, font, text, color, pos):
        super().__init__()
        self.text_surface = font.render(text, False, color)
        self.color = color
        self.text = text
        self.pos = pos

    def emphasize_and_change_color(self, color):
        font = pygame.font.SysFont('Comic Sans MS', 30, bold=True)
        font.set_underline(True)
        self.text_surface = font.render(self.text, False, color)

    def reset_and_change_color(self, color):
        font = pygame.font.SysFont('Comic Sans MS', 30, bold=False)
        font.set_underline(False)
        self.text_surface = font.render(self.text, False, color)


class FoodSprite(pygame.sprite.Sprite):
    def __init__(self, name, icon_image):
        super().__init__()

        self.width = 125
        self.height = 94

        self.name = name
        self.image = pygame.image.load("images/" + icon_image)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()

        self.pos = None
        self.starting_pos = None

    def set_starting_pos(self, x, y):
        self.pos = self.starting_pos = (x, y)
        self.rect = self.rect.move(self.pos)

    def reset_starting_pos(self):
        self.update_pos(self.starting_pos[0], self.starting_pos[1])

    def update_pos(self, x, y):
        self.pos = (x, y)
        self.rect.x = x
        self.rect.y = y

        self.update()


class BackgroundSprite(pygame.sprite.Sprite):
    def __init__(self, filename, screen_width, screen_height):
        super().__init__()
        self.image = pygame.image.load("images/" + filename)
        self.image = self.image.convert_alpha()

        self.pos = self.image.get_size()
        self.pos = (screen_width // 2 - self.pos[0] // 2, screen_height // 2 - self.pos[1] // 2)

        self.rect = self.image.get_rect()
        self.rect = self.rect.move(self.pos)


class ShelfGame:
    def __init__(self, shelf_order, stock_order, screen_width, screen_height):
        self.shelf_order_names = shelf_order
        self.stock_order = []
        for item_name in stock_order:
            filename = item_name + '.png'
            self.stock_order.append(FoodSprite(item_name, filename))

        self.shelf_sprite = BackgroundSprite('shelf.png', screen_width, screen_height)
        self.shelf_sprite_size = self.shelf_sprite.image.get_size()

        self.shelf_height_offset = 21
        self.shelf_width_offset = 20
        self.opening_width = self.shelf_sprite_size[0] - 2 * self.shelf_width_offset
        self.opening_height = self.stock_order[0].height

        self.opening_rects = self.set_opening_rects()

        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.shelf_order_text = self.set_shelf_order_text(shelf_order)
        self.shelf_order_sprite_pos = self.set_shelf_order_sprite_pos()

        instructions_x = screen_width // 2 - 250
        instructions_y = screen_height - 85
        self.instructions = TextSprite(self.font, 'Click and drag each item to its corresponding box.', (0, 0, 0),
                                       (instructions_x, instructions_y))

        self.progress = 0
        self.all_restocked = (1 << len(shelf_order)) - 1

    def set_opening_rects(self):
        opening_rects = []

        first_opening_top_left_px = self.shelf_sprite.pos[0] + self.shelf_width_offset
        first_opening_top_left_py = self.shelf_sprite.pos[1] + self.shelf_height_offset
        for i in range(5):
            opening_top_left_py = first_opening_top_left_py + (self.opening_height + self.shelf_height_offset) * i
            image = pygame.Surface([self.opening_width, self.opening_height])
            rect = image.get_rect().move((first_opening_top_left_px, opening_top_left_py))
            opening_rects.append(rect)

        return opening_rects

    def set_shelf_order_text(self, shelf_order):
        shelf_order_text = []
        for i in range(5):
            text_pos_x = self.opening_rects[i].x
            text_pos_y = self.opening_rects[i].y
            text_color = (0, 0, 0)
            shelf_order_text.append(TextSprite(self.font, shelf_order[i], text_color, (text_pos_x, text_pos_y)))

        return shelf_order_text

    def set_shelf_order_sprite_pos(self):
        shelf_order_sprite_pos = []
        for i in range(5):
            sprite_pos_x = self.opening_rects[i].x + self.opening_width // 2 - self.stock_order[0].width // 2
            sprite_pos_y = self.opening_rects[i].y
            shelf_order_sprite_pos.append((sprite_pos_x, sprite_pos_y))

        return shelf_order_sprite_pos

    def won(self):
        return self.progress == self.all_restocked

    def reset(self):
        self.progress = 0
        for food_sprite in self.stock_order:
            food_sprite.reset_starting_pos()


class Sound:
    def __init__(self, filename):
        self.sound = pygame.mixer.Sound(filename)
        self.is_playing = False


class ApplicationTypingGame:
    def __init__(self, screen_width, screen_height):
        self.background = BackgroundSprite('application_form.jpg', screen_width, screen_height)
        self.first_name = 'Elon'
        self.middle_name = 'The'
        self.last_name = 'Musk'
        self.address = '3500 Deer Creek Road'
        self.city_street_zip = 'Palo Alto, California, 94304'
        self.number = '650-681-5000'
        self.eligible = 'X'

        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.default_color = (128, 128, 128)
        self.typed_color = (0, 0, 0)
        self.emph_color = (255, 0, 0)

        self.first_name_text = None
        self.middle_name_text = None
        self.last_name_text = None
        self.address_text = None
        self.city_street_zip_text = None
        self.number_text = None
        self.eligible_text = None

        self.set_name_texts(self.default_color)

        self.text_surface_list = [self.first_name_text, self.middle_name_text, self.last_name_text, self.address_text,
                                  self.city_street_zip_text, self.number_text, self.eligible_text]

        self.current_word_idx = 0
        self.input_box = self.init_input_box(screen_width, screen_height)

        instructions_1_x = self.input_box.rect.x
        instructions_1_y = self.input_box.rect.y - 100
        self.instructions_1 = TextSprite(self.font, 'Type the word highlighted in RED', (0, 0, 0),
                                         (instructions_1_x, instructions_1_y))

        instructions_2_x = instructions_1_x
        instructions_2_y = instructions_1_y + 30
        self.instructions_2 = TextSprite(self.font, 'and press enter to move onto', (0, 0, 0),
                                         (instructions_2_x, instructions_2_y))

        instructions_3_x = instructions_2_x
        instructions_3_y = instructions_2_y + 30
        self.instructions_3 = TextSprite(self.font, 'the next word.', (0, 0, 0),
                                         (instructions_3_x, instructions_3_y))

        self.text_surface_list[0].emphasize_and_change_color(self.emph_color)

        next_button_w = 300
        next_button_h = 50
        next_button_x = screen_width - next_button_w - 25
        next_button_y = screen_height - next_button_h - 25
        skip_text = TextSprite(self.font, "Or use a family connection", (255, 255, 255),
                               (next_button_x + 17, next_button_y + 15))
        self.skip_button = Button(next_button_x, next_button_y, next_button_w, next_button_h, (0, 0, 255), (0, 0, 200),
                                  skip_text)

        self.won = False

    def init_input_box(self, screen_width, screen_height):
        right_of_form_px = self.background.rect.x + self.background.image.get_size()[0]
        center_screen_py = screen_height // 2 - 15

        # box_px = right_of_form_px + (screen_width - right_of_form_px) // 2
        box_px = right_of_form_px + 17
        box_py = center_screen_py

        return InputBox(box_px, box_py, 300, 30, self.font)

    def draw(self, screen, skippable):
        screen.blit(self.background.image, self.background.pos)
        for text in self.text_surface_list:
            screen.blit(text.text_surface, text.pos)
        self.input_box.draw(screen)
        screen.blit(self.instructions_1.text_surface, self.instructions_1.pos)
        screen.blit(self.instructions_2.text_surface, self.instructions_2.pos)
        screen.blit(self.instructions_3.text_surface, self.instructions_3.pos)

        if skippable:
            self.skip_button.draw(screen)

    def set_name_texts(self, text_color):
        name_offset = 45

        first_name_pos_x = self.background.pos[0] + 110
        first_name_pos_y = self.background.pos[1] + 225
        self.first_name_text = TextSprite(self.font, self.first_name, text_color, (first_name_pos_x, first_name_pos_y))

        middle_name_pos_x = first_name_pos_x + 10
        middle_name_pos_y = first_name_pos_y + name_offset
        self.middle_name_text = TextSprite(self.font, self.middle_name, text_color, (middle_name_pos_x,
                                                                                     middle_name_pos_y))

        last_name_pos_x = first_name_pos_x
        last_name_pos_y = middle_name_pos_y + name_offset
        self.last_name_text = TextSprite(self.font, self.last_name, text_color, (last_name_pos_x, last_name_pos_y))

        address_pos_x = first_name_pos_x - 60
        address_pos_y = last_name_pos_y + 90
        self.address_text = TextSprite(self.font, self.address, text_color, (address_pos_x, address_pos_y))

        city_state_zip_pos_x = first_name_pos_x - 60
        city_state_zip_pos_y = address_pos_y + 85
        self.city_street_zip_text = TextSprite(self.font, self.city_street_zip, text_color, (city_state_zip_pos_x,
                                                                                             city_state_zip_pos_y))

        number_pos_x = first_name_pos_x - 65
        number_pos_y = city_state_zip_pos_y + 90
        self.number_text = TextSprite(self.font, self.number, text_color, (number_pos_x, number_pos_y))

        eligible_pos_x = first_name_pos_x - 35
        eligible_pos_y = number_pos_y + 85
        self.eligible_text = TextSprite(self.font, self.eligible, text_color, (eligible_pos_x, eligible_pos_y))

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEMOTION:
                self.skip_button.selected = self.skip_button.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.skip_button.rect.collidepoint(event.pos):
                    self.won = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    current_surface = self.text_surface_list[self.current_word_idx]
                    if self.input_box.text == current_surface.text:
                        self.input_box.clear_text()
                        current_surface.reset_and_change_color(self.typed_color)

                        self.current_word_idx += 1

                        if self.current_word_idx < len(self.text_surface_list):
                            next_surface = self.text_surface_list[self.current_word_idx]
                            next_surface.emphasize_and_change_color(self.emph_color)
                elif event.key == pygame.K_BACKSPACE:
                    self.input_box.text = self.input_box.text[:-1]
                else:
                    self.input_box.text += event.unicode

        if self.current_word_idx == len(self.text_surface_list):
            self.won = True

        return True


class InputBox:

    def __init__(self, x, y, w, h, font, text=''):
        image = pygame.Surface([w, h])
        self.rect = image.get_rect().move((x, y))
        self.color = (0, 0, 0)
        self.text = text
        self.font = font
        self.txt_surface = font.render(text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def clear_text(self):
        self.text = ''

    def draw(self, screen):
        self.txt_surface = self.font.render(self.text, True, self.color)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


class TitleScreen:
    def __init__(self, screen_width, screen_height):
        title_font = pygame.font.Font('freesansbold.ttf', 115)
        title_x = screen_width // 2 - 350
        title_y = screen_height // 2 - 150
        self.title = TextSprite(title_font, 'Meritocracy?', (255, 0, 255), (title_x, title_y))

        button_font = pygame.font.Font('freesansbold.ttf', 30)
        b_w = 125
        b_h = 75
        self.start_default_color = (0, 0, 200)
        self.start_hover_color = (0, 0, 255)

        start_b_x = screen_width // 2 - b_w // 2
        start_b_y = title_y + 150
        start_txt_x = start_b_x + 15
        start_txt_y = start_b_y + 25
        self.start_text = TextSprite(button_font, 'START', (255, 255, 255), (start_txt_x, start_txt_y))
        self.start_button = Button(start_b_x, start_b_y, b_w, b_h,
                                   self.start_hover_color, self.start_default_color, self.start_text)

        self.quit_hover_color = (255, 0, 0)
        self.quit_default_color = (200, 0, 0)

        quit_b_x = start_b_x
        quit_b_y = start_b_y + 100
        quit_txt_x = quit_b_x + 25
        quit_txt_y = quit_b_y + 25
        self.quit_text = TextSprite(button_font, 'QUIT', (255, 255, 255), (quit_txt_x, quit_txt_y))
        self.quit_button = Button(quit_b_x, quit_b_y, b_w, b_h,
                                  self.quit_hover_color, self.quit_default_color, self.quit_text)

    def draw(self, screen):
        screen.blit(self.title.text_surface, self.title.pos)
        self.start_button.draw(screen)
        self.quit_button.draw(screen)


class WinScreen:
    def __init__(self, screen_width, screen_height):
        title_font = pygame.font.Font('freesansbold.ttf', 115)
        title_x = screen_width // 2 - 275
        title_y = screen_height // 2 - 150
        self.title = TextSprite(title_font, 'You did it!', (255, 255, 255), (title_x, title_y))

        button_font = pygame.font.Font('freesansbold.ttf', 30)
        b_w = 350
        b_h = 75
        self.start_default_color = (0, 0, 200)
        self.start_hover_color = (0, 0, 255)

        home_b_x = screen_width // 2 - b_w // 2
        home_b_y = title_y + 250
        home_txt_x = home_b_x + 20
        home_txt_y = home_b_y + 25
        self.home_text = TextSprite(button_font, 'Back to home screen', (255, 255, 255), (home_txt_x, home_txt_y))
        self.home_button = Button(home_b_x, home_b_y, b_w, b_h,
                                  self.start_hover_color, self.start_default_color, self.home_text)

        self.quit_hover_color = (255, 0, 0)
        self.quit_default_color = (200, 0, 0)

        quit_b_x = home_b_x
        quit_b_y = home_b_y + 100
        quit_txt_x = quit_b_x + 135
        quit_txt_y = quit_b_y + 25
        self.quit_text = TextSprite(button_font, 'QUIT', (255, 255, 255), (quit_txt_x, quit_txt_y))
        self.quit_button = Button(quit_b_x, quit_b_y, b_w, b_h,
                                  self.quit_hover_color, self.quit_default_color, self.quit_text)

    def draw(self, screen):
        screen.blit(self.title.text_surface, self.title.pos)
        self.home_button.draw(screen)
        self.quit_button.draw(screen)


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, b_w, b_h, hover_color, default_color, text_sprite):
        super().__init__()
        self.image = pygame.Surface([b_w, b_h])
        white = (255, 255, 255)
        self.image.fill(white)
        self.image.set_colorkey(white)

        self.hover_color = hover_color
        self.default_color = default_color
        self.dim = (x, y, b_w, b_h)

        self.rect = self.image.get_rect().move((x, y))

        self.selected = False

        self.text_sprite = text_sprite

    def draw(self, screen):
        if self.selected:
            pygame.draw.rect(screen, self.hover_color, self.dim)
        else:
            pygame.draw.rect(screen, self.default_color, self.dim)

        screen.blit(self.text_sprite.text_surface, self.text_sprite.pos)


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, color, maze_color, x, y, radius):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Create the rectangular image, fill and set background to transparent
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.image.fill(maze_color)
        self.image.set_colorkey(maze_color)

        # Draw our player onto the transparent rectangle
        pygame.draw.circle(self.image, color, (radius, radius), radius)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def set_coord(self, x, y):
        self.rect.x = x
        self.rect.y = y


class SlotMachineView:
    def __init__(self, screen_width, screen_height):
        font = pygame.font.SysFont('Comic Sans MS', 30)
        text_color_black = (0, 0, 0)
        instruction_pos = (455, 140)
        self.instructions = TextSprite(font, 'Click the spin button to spin your destiny!', text_color_black,
                                       instruction_pos)

        text_color_white = (255, 255, 255)
        button_default_color = (0, 0, 200)  # dark blue
        button_hover_color = (0, 0, 255)  # blue
        next_button_w = 125
        next_button_h = 75
        next_button_x = screen_width - next_button_w - 75
        next_button_y = screen_height - next_button_h - 25
        next_txt_x = next_button_x + 35
        next_txt_y = next_button_y + 30
        self.next_b_text = TextSprite(font, 'NEXT', text_color_white, (next_txt_x, next_txt_y))
        self.next_button = Button(next_button_x, next_button_y, next_button_w, next_button_h,
                                  button_default_color, button_hover_color, self.next_b_text)


class View:
    BACKGROUND_IMAGE_NAME = 'background.png'
    GAME_TITLE = 'Slot Machine'
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    REEL_POSITIONS = [(400, 258), (400 + 180, 258), (400 + 180 * 2, 258)]

    WALL_COLOR = (18, 94, 32)
    MAZE_COLOR = (255, 255, 255)
    BLOCK_SIZE = 10
    PATH_WIDTH = 3
    CELL_SIZE = BLOCK_SIZE * PATH_WIDTH + BLOCK_SIZE  # extra BLOCK_SIZE to include wall to east and south of cell

    PLAYER_COLOR = (0, 0, 255)  # Blue
    PLAYER_RADIUS = (BLOCK_SIZE * 3) // 2
    WIN_SPRITE_COLOR = (255, 0, 0)  # Red

    TOP_RIGHT_TIME_PX = SCREEN_WIDTH - 175
    TOP_RIGHT_TIME_PY = 50

    def __init__(self, maze):
        """ Constructs view, setting up values for coordinates and colors"""
        pygame.init()
        pygame.font.init()

        # Initialize sounds
        pygame.mixer.init()
        self.spin_snd = Sound('sounds/spin_snd.ogg')
        self.spinning_snd = Sound('sounds/itemreel.wav')
        self.spin_result = Sound('sounds/gotitem.wav')

        # Assign the Display Variables
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption(self.GAME_TITLE)

        self.slot_background = Sprite(self.BACKGROUND_IMAGE_NAME, (self.SCREEN_WIDTH / 4, 0))
        # 270, self.slot_background.get_height() - 165)
        self.spin_button = Sprite('spin_button.png', (self.SCREEN_WIDTH / 2 - 50, self.SCREEN_HEIGHT * 0.7))

        self.reel_icons = self.set_reel_icons()

        # Set maze drawing variables
        # extra BLOCK_SIZE to include top edge wall
        self.MAZE_WIDTH_PX = self.CELL_SIZE * maze.width + self.BLOCK_SIZE
        # extra BLOCK_SIZE to include left edge wall
        self.MAZE_HEIGHT_PX = self.CELL_SIZE * maze.height + self.BLOCK_SIZE
        self.MAZE_TOP_LEFT_CORNER = (self.SCREEN_WIDTH // 2 - self.MAZE_WIDTH_PX // 2,
                                     self.SCREEN_HEIGHT // 2 - self.MAZE_HEIGHT_PX // 2)
        self.OFFSET_X = self.MAZE_TOP_LEFT_CORNER[0] + self.BLOCK_SIZE
        self.OFFSET_Y = self.MAZE_TOP_LEFT_CORNER[1] + self.BLOCK_SIZE

        self.maze_image = None
        self.player_sprite = None
        self.player_sprite_image = None
        self.win_sprite = None
        self.win_sprite_image = None

        self.shelf_view = None
        self.food_sprite_rects = None
        self.food_sprite_group = None

        self.application_game = ApplicationTypingGame(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.title_screen = TitleScreen(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.slot_machine_view = SlotMachineView(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.win_screen = WinScreen(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.insults = []

    def spin_results_to_icon_images(self, spin_results):
        icon_images = [0] * 3
        for reel in range(3):
            result = spin_results[reel]
            icon_images[reel] = self.reel_icons[reel][result]

        return icon_images

    @staticmethod
    def set_reel_icons():
        return [[Icon('female_symbol.jpg'), Icon('male_symbol.jpg')],
                [Icon('black_hand.jpg'), Icon('white_hand.jpg')],
                [Icon('food_stamp.jpg'), Icon('money.jpg')]]

    def draw_maze_screen(self, time, draw_insult):
        self.screen.blit(self.maze_image, (0, 0))
        self.player_sprite_image.draw(self.screen)
        self.win_sprite_image.draw(self.screen)

        self.draw_time_text(self.TOP_RIGHT_TIME_PX, self.TOP_RIGHT_TIME_PY, time)

        if draw_insult:
            insult = self.insults[0]
            self.screen.blit(insult.text_surface, insult.pos)

    def draw_maze(self, maze):
        """ Draws a maze with a maze object"""
        self.screen.fill((0, 0, 0))
        self.draw_background()

        for y in range(maze.height):
            for x in range(maze.width):
                for px in range(self.PATH_WIDTH):
                    for py in range(self.PATH_WIDTH):
                        self.draw_block(x * (self.PATH_WIDTH + 1) + px, y * (self.PATH_WIDTH + 1) + py)

                for p in range(self.PATH_WIDTH):
                    # Bit values for down and right
                    down = 2
                    right = 8
                    cells = maze.Maze  # 2d array of maze
                    if cells[y][x].open_walls & down:
                        self.draw_block(x * (self.PATH_WIDTH + 1) + p,
                                        y * (self.PATH_WIDTH + 1) + self.PATH_WIDTH)
                    if cells[y][x].open_walls & right:
                        self.draw_block(x * (self.PATH_WIDTH + 1) + self.PATH_WIDTH,
                                        y * (self.PATH_WIDTH + 1) + p)

        self.maze_image = self.screen.copy()

        insult_x = self.SCREEN_WIDTH // 2
        insult_y = self.SCREEN_HEIGHT // 2
        font = pygame.font.SysFont('Comic Sans MS', 80)
        self.insults.append(TextSprite(font, "A WOMAN SHOULDN'T BE DOING THIS", (255, 0, 0), (insult_x - 525, insult_y)))

        pygame.mixer.music.unload()
        pygame.mixer.music.load('sounds/maze_music.ogg')
        pygame.mixer.music.play(loops=-1, start=30)

    def maze_coord_to_px(self, x, y):
        px = self.OFFSET_X + self.BLOCK_SIZE * (self.PATH_WIDTH + 1) * y
        py = self.OFFSET_Y + self.BLOCK_SIZE * (self.PATH_WIDTH + 1) * x

        return px, py

    def draw_block(self, x, y):
        x_offset = self.MAZE_TOP_LEFT_CORNER[0] + self.BLOCK_SIZE
        y_offset = self.MAZE_TOP_LEFT_CORNER[1] + self.BLOCK_SIZE
        x_coord = x * self.BLOCK_SIZE + x_offset
        y_coord = y * self.BLOCK_SIZE + y_offset
        pygame.draw.rect(self.screen, self.MAZE_COLOR, (x_coord, y_coord, self.BLOCK_SIZE, self.BLOCK_SIZE))

    def draw_background(self):
        x_coord = self.MAZE_TOP_LEFT_CORNER[0]
        y_coord = self.MAZE_TOP_LEFT_CORNER[1]
        pygame.draw.rect(self.screen, self.WALL_COLOR, (x_coord, y_coord, self.MAZE_WIDTH_PX, self.MAZE_HEIGHT_PX))

    def init_player(self, x, y):
        self.player_sprite = PlayerSprite(self.PLAYER_COLOR, self.MAZE_COLOR, x, y, self.PLAYER_RADIUS)
        self.player_sprite_image = pygame.sprite.RenderPlain(self.player_sprite)

    def init_win_sprite(self, x_coord, y_coord):
        px = self.maze_coord_to_px(x_coord, y_coord)
        self.win_sprite = PlayerSprite(self.WIN_SPRITE_COLOR, self.MAZE_COLOR, px[0], px[1], self.PLAYER_RADIUS)
        self.win_sprite_image = pygame.sprite.RenderPlain(self.win_sprite)

    def init_shelf_view(self, shelf_order, stock_order):
        self.shelf_view = ShelfGame(shelf_order, stock_order, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.set_food_starting_pos()

    # def init_application_view(self):
    #     self.application_game = ApplicationTypingGame(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
    def draw_application_game(self, time, skippable):
        self.screen.fill((255, 255, 255))
        self.application_game.draw(self.screen, skippable)
        self.draw_time_text(self.TOP_RIGHT_TIME_PX, self.TOP_RIGHT_TIME_PY, time)

    def draw_shelf(self, time):
        self.screen.fill((255, 255, 255))
        shelf_sprite = self.shelf_view.shelf_sprite
        self.screen.blit(shelf_sprite.image, shelf_sprite.rect)
        for food_sprite in self.shelf_view.stock_order:
            self.screen.blit(food_sprite.image, food_sprite.rect)

        for text_sprite in self.shelf_view.shelf_order_text:
            self.screen.blit(text_sprite.text_surface, text_sprite.pos)

        self.draw_time_text(self.TOP_RIGHT_TIME_PX, self.TOP_RIGHT_TIME_PY, time)
        self.screen.blit(self.shelf_view.instructions.text_surface, self.shelf_view.instructions.pos)
        pygame.display.update(shelf_sprite.rect)
        pygame.display.update(self.food_sprite_rects)
        pygame.sprite.RenderUpdates(self.food_sprite_group)

    def set_food_starting_pos(self):
        self.food_sprite_rects = []

        shelf_sprite = self.shelf_view.shelf_sprite
        shelf_sprite_dim = shelf_sprite.image.get_size()

        shelf_sprite_width = shelf_sprite_dim[0]
        shelf_sprite_height = shelf_sprite_dim[1]

        left_side_px = shelf_sprite.pos[0] / 2
        # Draw three food sprites on left side of shelf sprite
        for i in range(3):
            food_sprite = self.shelf_view.stock_order[i]
            left_side_py = shelf_sprite.pos[1] + (shelf_sprite_height - food_sprite.height) * i // 2
            food_sprite.set_starting_pos(left_side_px - food_sprite.width // 2, left_side_py)

        right_side_px = (self.SCREEN_WIDTH - shelf_sprite_width) * 2
        # Draw three food sprites on left side of shelf sprite
        for i in range(2):
            food_sprite = self.shelf_view.stock_order[3 + i]
            right_side_py = shelf_sprite.pos[1] + (shelf_sprite_height - food_sprite.height) * (i + 1) // 3
            food_sprite.set_starting_pos(right_side_px - food_sprite.width // 2, right_side_py)

        for food_sprite in self.shelf_view.stock_order:
            self.food_sprite_rects.append(food_sprite.rect)
            self.food_sprite_group = pygame.sprite.Group(self.shelf_view.stock_order)

    def can_place_item(self, food_sprite, mouse_pos):
        print(self.shelf_view.opening_rects[1][0], self.shelf_view.opening_rects[1][1])
        for i, opening_rect in enumerate(self.shelf_view.opening_rects):
            if opening_rect.collidepoint(mouse_pos):
                stock_order = self.shelf_view.stock_order
                if stock_order[food_sprite].name is self.shelf_view.shelf_order_names[i]:
                    food_sprite_new_x = self.shelf_view.shelf_order_sprite_pos[i][0]
                    food_sprite_new_y = self.shelf_view.shelf_order_sprite_pos[i][1]
                    print(food_sprite_new_x, food_sprite_new_y)
                    stock_order[food_sprite].update_pos(food_sprite_new_x, food_sprite_new_y)
                    return True

        self.shelf_view.stock_order[food_sprite].reset_starting_pos()
        return False

    def draw_title_screen(self):
        self.screen.fill((0, 0, 0))
        self.title_screen.draw(self.screen)

    def draw_win_screen(self, time):
        self.screen.fill((0, 0, 0))
        self.win_screen.draw(self.screen)

        title_pos = self.win_screen.title.pos
        self.draw_time_text(title_pos[0] + 155, title_pos[1] + 150, time, font_size=65, offset_x=125, offset_y=15)

    def draw_time_text(self, x, y, time, font_size=30, offset_x=65, offset_y=7):
        description_font = pygame.font.SysFont('Comic Sans MS', font_size)
        description = TextSprite(description_font, 'TIME:', (255, 0, 0), (x, y))

        time_font = pygame.font.Font("fonts/DS-DIGIT.TTF", font_size)
        time = str(round(time, 3))
        time_text = TextSprite(time_font, time, (255, 0, 0), (x + offset_x, y - offset_y))

        self.screen.blit(description.text_surface, description.pos)
        self.screen.blit(time_text.text_surface, time_text.pos)
