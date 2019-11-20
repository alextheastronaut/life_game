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
        self.text = text
        self.pos = pos


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


class Sound:
    def __init__(self, filename):
        self.sound = pygame.mixer.Sound(filename)
        self.is_playing = False


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

        self.shelf_view = None
        self.food_sprite_rects = None
        self.food_sprite_group = None

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

    def draw_maze_screen(self):
        self.screen.blit(self.maze_image, (0, 0))
        self.player_sprite_image.draw(self.screen)

    def draw_maze(self, maze):
        """ Draws a maze with a maze object"""
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

        pygame.display.update()
        self.maze_image = self.screen.copy()

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

    def init_shelf_view(self, shelf_order, stock_order):
        self.shelf_view = ShelfGame(shelf_order, stock_order, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.set_food_starting_pos()

    def draw_shelf(self):
        self.screen.fill((255, 255, 255))
        shelf_sprite = self.shelf_view.shelf_sprite
        self.screen.blit(shelf_sprite.image, shelf_sprite.rect)
        for food_sprite in self.shelf_view.stock_order:
            self.screen.blit(food_sprite.image, food_sprite.rect)

        for text_sprite in self.shelf_view.shelf_order_text:
            self.screen.blit(text_sprite.text_surface, text_sprite.pos)

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

