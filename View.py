import pygame


class Icon(pygame.sprite.Sprite):
    def __init__(self, icon_image):
        self.image = pygame.image.load("images/" + icon_image)
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image_file_name, pos):
        pygame.sprite.Sprite.__init__(self)
        # Load the png image with transparency
        self.image = pygame.image.load("images/" + image_file_name)
        self.image = self.image.convert_alpha()
        # Move the rect to make sure it follows the image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos)
        self.pos = pos


class Sound:
    def __init__(self, filename):
        self.sound = pygame.mixer.Sound(filename)
        self.is_playing = False


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

    def __init__(self, maze):
        """ Constructs view, setting up values for coordinates and colors"""
        pygame.init()

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
