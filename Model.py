import pygame
import random
from enum import Enum


class SlotMachine:
    def __init__(self):
        self.results = 3 * [0]
        self.prev_results = 3 * [0]
        self.display_spinning = self.prev_results.copy()
        self.spinning = False
        random.seed()

    def spin(self):
        # Chance to be woman, black, and in poverty, respectively.
        chance = [50, 17, 20]

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

        random.seed()
        self.Maze = self.generate_maze()

    def generate_maze(self):
        maze = [[Cell() for j in range(self.width)] for i in range(self.height)]
        self.generate_rand_maze(0, 0, maze)

        return maze

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


class Model:
    def __init__(self):
        self.slot_machine = SlotMachine()
        self.maze = Maze(10, 15)
