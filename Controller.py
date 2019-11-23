import pygame
import time
import random
from Model import Model
from Model import Direction
from View import View
from enum import Enum


class Screen(Enum):
    Title = 1
    Slot = 2
    Maze = 3
    Restock = 4
    Application = 5


class Controller:
    FRAME_RATE = 30

    def __init__(self):
        self.model = Model()
        self.view = View(self.model.maze)
        self.clock = pygame.time.Clock()
        self.clock.tick(self.FRAME_RATE)
        self.start_time = 0

        self.selected_food_sprite = None
        self.selected_offset_x = None
        self.selected_offset_y = None

        self.current_screen = Screen.Title

    def display_slot_machine_icons(self, results_to_display):
        """Displays previously rolled icons in slot machine"""
        display_results = self.view.spin_results_to_icon_images(results_to_display)
        for reel in range(3):
            self.view.screen.blit(display_results[reel].image, self.view.REEL_POSITIONS[reel])

    def init_slot_machine(self):
        # Set the variables to be used by the game loop
        self.model.slot_machine.spinning = False

        # Play the bg music
        pygame.mixer.music.load("sounds/mario_kart_wii_coconut_mall.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.6)

    def play_slot_machine(self):
        # Check for events
        for event in pygame.event.get():
            # Stop the loop when the user chooses to quit the game
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEMOTION:
                next_button = self.view.slot_machine_view.next_button
                next_button.selected = True if next_button.rect.collidepoint(event.pos) else False
            # When the user pushes the mouse button down, Check which sprites are involved
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if spin button is clicked
                if self.view.spin_button.rect.collidepoint(event.pos):
                    # Make sure you cant click the spin button while the reels are spinning
                    if not self.model.slot_machine.spinning:
                        self.model.slot_machine.spin()

                        # Set the start time to current time. Making the spin animation run
                        self.start_time = time.time()

                        # Set spinning to true to make sure the user can't click spin again while spinning
                        self.model.slot_machine.spinning = True
                        self.view.spin_snd.sound.play()
                elif self.view.slot_machine_view.next_button.rect.collidepoint(event.pos):
                    pygame.mixer.music.fadeout(1000)
                    self.current_screen = Screen.Maze

        # Fill the background black
        self.view.screen.fill((0, 0, 0))

        # Display the background image
        self.view.screen.blit(self.view.slot_background.image, self.view.slot_background.pos)

        # Display instructions on screen
        self.view.screen.blit(self.view.slot_machine_view.instructions.text_surface,
                              self.view.slot_machine_view.instructions.pos)

        # Update the action buttons and position them on the screen
        self.view.spin_button.update()
        self.view.screen.blit(self.view.spin_button.image, self.view.spin_button.pos)

        # This section is the one responsible for the reel animation
        # While the current time - the time the spin button is clicked is less than one
        # Change the images in the reel and show the previous/current texts
        if self.model.slot_machine.spinning and self.model.slot_machine.can_spin:
            if time.time() - self.start_time < 1:
                # Display the current icons in the reel so it does not change until the pulling the lever
                # sound is finished
                prev_results = self.model.slot_machine.prev_results
                self.display_slot_machine_icons(prev_results)
            elif time.time() - self.start_time < 3.6:
                # Alternate Icons in each reel and play the spinning sound
                self.model.slot_machine.switch_spin_icons()
                rand_icons = self.model.slot_machine.display_spinning
                self.display_slot_machine_icons(rand_icons)

                if not self.view.spinning_snd.is_playing:
                    self.view.spinning_snd.sound.play()
                    self.view.spinning_snd.is_playing = True
            else:
                # The animation is done and display the resulted values
                spin_results = self.model.slot_machine.results
                self.display_slot_machine_icons(spin_results)

                # # Spinning is now false. The user can hit spin again
                # self.model.slot_machine.spinning = False

                # Set the prev results to the current images to be used again on animation
                self.model.slot_machine.set_prev_results_to_results()

                # Stop the spinning sound if playing
                self.view.spinning_snd.sound.stop()
                self.view.spinning_snd.is_playing = False

                self.view.spin_result.sound.play()

                self.model.slot_machine.can_spin = False
        else:
            # Display previous results if slot machine isn't spinning
            prev_results = self.model.slot_machine.prev_results
            self.display_slot_machine_icons(prev_results)
            if not self.model.slot_machine.can_spin:
                self.view.slot_machine_view.next_button.draw(self.view.screen)

        return True

    def init_maze_game(self):
        self.view.draw_maze(self.model.maze)
        self.model.init_player(0, 0, self.view.OFFSET_X, self.view.OFFSET_Y)
        offset_coord = self.model.player.get_offset_px()
        self.view.init_player(offset_coord[0], offset_coord[1])
        self.view.init_win_sprite(self.model.maze.win_sprite_coord[0], self.model.maze.win_sprite_coord[1])

    def play_maze_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        # Handle key input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.model.move_player(Direction.UP, self.view.BLOCK_SIZE,
                                   self.view.PLAYER_RADIUS)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.model.move_player(Direction.DOWN, self.view.BLOCK_SIZE,
                                   self.view.PLAYER_RADIUS)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.model.move_player(Direction.LEFT, self.view.BLOCK_SIZE,
                                   self.view.PLAYER_RADIUS)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.model.move_player(Direction.RIGHT, self.view.BLOCK_SIZE,
                                   self.view.PLAYER_RADIUS)

        offset_coord = self.model.player.get_offset_px()
        self.view.player_sprite.set_coord(offset_coord[0], offset_coord[1])

        self.view.draw_maze_screen()

        return True

    def init_shelf_game(self):
        shelf_game = self.model.shelf_game
        self.view.init_shelf_view(shelf_game.shelf_order, shelf_game.stock_order)

    def play_shelf_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                stock_sprites = self.view.shelf_view.stock_order
                # Check if a bet button is clicked then set the bet value to the value of that button
                for i, food_sprite in enumerate(stock_sprites):
                    if food_sprite.rect.collidepoint(event.pos):
                        self.selected_food_sprite = i
                        self.selected_offset_x = food_sprite.rect.x - event.pos[0]
                        self.selected_offset_y = food_sprite.rect.y - event.pos[1]
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.selected_food_sprite is not None:
                    self.view.can_place_item(self.selected_food_sprite, event.pos)
                    self.selected_food_sprite = None
            elif event.type == pygame.MOUSEMOTION:
                if self.selected_food_sprite is not None:
                    stock_sprites = self.view.shelf_view.stock_order

                    new_px = event.pos[0] + self.selected_offset_x
                    new_py = event.pos[1] + self.selected_offset_y

                    stock_sprites[self.selected_food_sprite].update_pos(new_px, new_py)

        self.view.draw_shelf()

        return True

    def play_application_game(self):
        self.view.draw_application_game()
        return self.view.application_game.handle_event()

    def display_title_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEMOTION:
                start_button = self.view.title_screen.start_button
                quit_button = self.view.title_screen.quit_button
                start_button.selected = start_button.rect.collidepoint(event.pos)
                quit_button.selected = quit_button.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                start_button = self.view.title_screen.start_button
                quit_button = self.view.title_screen.quit_button
                if start_button.rect.collidepoint(event.pos):
                    self.current_screen = Screen.Slot
                elif quit_button.rect.collidepoint(event.pos):
                    return False

        self.view.draw_title_screen()

        return True

    def start_game(self):
        # self.init_slot_machine()
        # self.init_maze_game()
        # self.init_shelf_game()
        slot_machine_init = False
        maze_init = False

        continue_playing = True
        while continue_playing:
            if self.current_screen is Screen.Title:
                continue_playing = self.display_title_screen()
            elif self.current_screen is Screen.Slot:
                if not slot_machine_init:
                    self.init_slot_machine()
                    slot_machine_init = True
                continue_playing = self.play_slot_machine()
            elif self.current_screen is Screen.Maze:
                if not maze_init:
                    self.init_maze_game()
                    maze_init = True
                continue_playing = self.play_maze_game()
        # continue_playing = self.play_slot_machine()
        # continue_playing = self.play_maze_game()
        # continue_playing = self.play_shelf_game()
        # continue_playing = self.play_application_game()

            # Refresh the display
            pygame.display.flip()

# Calls the main function
if __name__ == "__main__":
    c = Controller()
    c.start_game()
