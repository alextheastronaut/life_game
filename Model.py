import pygame
import random
from enum import Enum


class SlotMachine:
    def __init__(self):
        self.results = 3 * [0]
        self.prev_results = 3 * [0]
        self.display_spinning = self.prev_results.copy()
        self.spinning = False
        self.can_spin = True

    def spin(self):
        random.seed()
        # Chance to be woman, black, and in poverty, respectively.
        chance = [50, 25, 15]
        # chance = [100, 0, 100]

        # For each reel, choose between two outcomes based on the chance.
        for reel in range(3):
            rand_chance = random.randint(0, 100)
            self.results[reel] = 0 if rand_chance < chance[reel] else 1

    def switch_spin_icons(self):
        for reel in range(3):
            self.display_spinning[reel] = 0 if self.display_spinning[reel] is 1 else 1

    def set_prev_results_to_results(self):
        self.prev_results = self.results.copy()


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 4
    RIGHT = 8


class Maze:
    # Down, Left, Up, Right
    NEIGHBORS = {Direction.UP: [-1, 0],
                 Direction.DOWN: [1, 0],
                 Direction.LEFT: [0, -1],
                 Direction.RIGHT: [0, 1]
                 }

    DIRECTIONS = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

    OPPOSITE_DIRECTION = {Direction.UP: Direction.DOWN,
                          Direction.DOWN: Direction.UP,
                          Direction.LEFT: Direction.RIGHT,
                          Direction.RIGHT: Direction.LEFT
                          }

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.max_distance = 0

        random.seed()
        self.Maze = self.generate_maze()
        # self.win_sprite_coord = (0, 1)
        self.win_sprite_coord = self.find_farthest_cell_from_start()

    def generate_maze(self):
        maze = [[Cell() for j in range(self.width)] for i in range(self.height)]
        self.generate_rand_maze(0, 0, maze)

        return maze

    def find_farthest_cell_from_start(self):
        for x in range(self.height):
            for y in range(self.width):
                self.Maze[x][y].visited = False

        queue = list()
        queue.append((0, 0))
        curr_coord = None

        while len(queue) > 0:
            curr_coord = queue.pop(0)
            x = curr_coord[0]
            y = curr_coord[1]
            curr = self.Maze[x][y]
            curr.visited = True
            for direction in self.DIRECTIONS:
                if curr.open_walls & direction.value is not 0:
                    n_x = x + self.NEIGHBORS[direction][0]
                    n_y = y + self.NEIGHBORS[direction][1]

                    if self.__within_bounds(n_x, n_y) and not self.Maze[n_x][n_y].visited:
                        queue.append((n_x, n_y))

        return curr_coord

    def generate_rand_maze(self, i, j, maze):
        if self.__within_bounds(i, j) and not maze[i][j].visited:
            maze[i][j].visited = True
            unvisited_dir = self.get_unvisited_neighbors(i, j, maze)

            while len(unvisited_dir) > 0:
                # Choose a random unvisited direction to break down wall
                rand_dir = unvisited_dir[random.randint(0, len(unvisited_dir) - 1)]
                maze[i][j].open_walls |= rand_dir.value

                next_cell_x = i + self.NEIGHBORS[rand_dir][0]
                next_cell_y = j + self.NEIGHBORS[rand_dir][1]

                opposite = self.OPPOSITE_DIRECTION[rand_dir]
                maze[next_cell_x][next_cell_y].open_walls |= opposite.value

                self.generate_rand_maze(next_cell_x, next_cell_y, maze)

                unvisited_dir = self.get_unvisited_neighbors(i, j, maze)

    def get_unvisited_neighbors(self, i, j, maze):
        """ Returns unvisited neighbors """
        unvisited = []
        for direction in self.DIRECTIONS:
            neighbor = self.NEIGHBORS[direction]
            n_x = i + neighbor[0]
            n_y = j + neighbor[1]
            if self.__within_bounds(n_x, n_y) and not maze[n_x][n_y].visited:
                unvisited.append(direction)

        return unvisited

    def __within_bounds(self, i, j):
        return 0 <= i < self.height and 0 <= j < self.width

    @staticmethod
    def __mirror_direction(direction):
        # if Right or Down return Left and Up, otherwise do the opposite.
        return direction + 2 if direction <= 1 else direction - 2

    def print_maze(self):
        for y in range(self.height):
            for x in range(self.width):
                print(self.Maze[y][x].open_walls, '\t'),
            print()


class Cell:
    def __init__(self):
        self.visited = False
        self.open_walls = 0  # bitmap representing whether the cell's wall is open or closed.


class RestockShelfGame:
    ITEMS = ['condiments', 'steak', 'sushi', 'taco', 'watermelon']

    def __init__(self):
        self.shelf_order = None
        self.stock_order = None
        self.reshuffle_items()

    def reshuffle_items(self):
        random.shuffle(self.ITEMS)
        self.shelf_order = self.ITEMS.copy()
        random.shuffle(self.ITEMS)
        self.stock_order = self.ITEMS.copy()


class Player:
    def __init__(self, px, py, offset_x, offset_y):
        # Save the start position
        # x and y pixel coordinates
        self.start_px = self.px = px
        self.start_py = self.py = py
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.old_px = self.old_py = None
        self.x = 0
        self.y = 0

        self.tiles_moved_since_reset = 0

    def reset(self):
        self.px = self.start_px
        self.py = self.start_py

    def get_offset_px(self):
        return self.px + self.offset_x, self.py + self.offset_y

    def store_curr_pos_as_old_pos(self):
        self.old_px = self.px
        self.old_py = self.py

    def set_curr_pos_to_old_pos(self):
        self.px = self.old_px
        self.py = self.old_py
        self.tiles_moved_since_reset = 0

    def update_coord(self, x, y):
        self.x = x
        self.y = y
        self.tiles_moved_since_reset += 1

class Model:
    TILES_MOVED_TO_RESET = 65
    TILES_TO_MOVE_BACK = 10

    def __init__(self):
        self.slot_machine = SlotMachine()
        self.maze = Maze(14, 30)
        self.player = None
        self.shelf_game = RestockShelfGame()
        self.player_won = False
        self.prepped = False

    def init_player(self, x, y, offset_x, offset_y):
        self.player = Player(x, y, offset_x, offset_y)

    def move_player(self, direction, block_size, player_radius):
        if self.__can_move(direction, block_size, player_radius):
            if direction is Direction.UP:
                self.player.py -= 1
            elif direction is Direction.DOWN:
                self.player.py += 1
            elif direction is Direction.LEFT:
                self.player.px -= 1
            elif direction is Direction.RIGHT:
                self.player.px += 1

    def __can_move(self, direction, block_size, player_radius):
        # Calculate which cells the player occupies
        square = block_size * 4
        p1 = (self.player.px, self.player.py)  # Top left corner of player
        p2 = (p1[0] + square - 1, p1[1] + square - 1)  # Bottom right corner of player

        # Convert to maze index
        x_p1 = p1[1] // square
        y_p1 = p1[0] // square
        x_p2 = p2[1] // square
        y_p2 = p2[0] // square

        self.__update_player_coord(x_p1, x_p2, y_p1, y_p2)
        if self.should_prep_for_reset() and not self.prepped:
            self.player.store_curr_pos_as_old_pos()
            self.prepped = True

        # 2d array of cells
        maze = self.maze.Maze

        if self.__player_won(x_p1, x_p2, y_p1, y_p2):
            self.player_won = True
        # if direction is Direction.UP:
        # If the sprite is in the cell
        if x_p1 == x_p2 and y_p1 == y_p2:
            return maze[x_p1][y_p1].open_walls & direction.value
        else:
            dir_coord = self.maze.NEIGHBORS[direction]
            if direction is Direction.DOWN or direction is Direction.RIGHT:
                return x_p1 + dir_coord[0] == x_p2 and y_p1 + dir_coord[1] == y_p2
            else:
                return x_p2 + dir_coord[0] == x_p1 and y_p2 + dir_coord[1] == y_p1

    def __player_won(self, x_1, x_2, y_1, y_2):
        win_x = self.maze.win_sprite_coord[0]
        win_y = self.maze.win_sprite_coord[1]
        if x_1 == win_x and y_1 == win_y and x_2 == win_x and y_2 == win_y:
            return True

    def __update_player_coord(self, x_1, x_2, y_1, y_2):
        if self.player.x != x_1 or self.player.y != y_1:
            self.player.update_coord(x_1, y_1)
        # elif self.player.x != x_2 or self.player.y != y_2:
        #     self.player.update_coord(x_2, y_2)

    def should_prep_for_reset(self):
        return self.TILES_MOVED_TO_RESET <= self.player.tiles_moved_since_reset

    def should_reset(self):
        return self.TILES_MOVED_TO_RESET + self.TILES_TO_MOVE_BACK <= self.player.tiles_moved_since_reset

    def reset_player(self):
        self.player.set_curr_pos_to_old_pos()
        self.prepped = False


