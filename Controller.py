import pygame
import time
import random
from Model import Model
from Model import Direction
from View import View


class Controller:
    FRAME_RATE = 30

    def __init__(self):
        self.model = Model()
        self.view = View(self.model.maze)
        self.clock = pygame.time.Clock()
        self.clock.tick(self.FRAME_RATE)
        self.start_time = 0

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

        # Display the background image
        self.view.screen.blit(self.view.slot_background.image, self.view.slot_background.pos)

        # Update the action buttons and position them on the screen
        self.view.spin_button.update()
        self.view.screen.blit(self.view.spin_button.image, self.view.spin_button.pos)

        # This section is the one responsible for the reel animation
        # While the current time - the time the spin button is clicked is less than one
        # Change the images in the reel and show the previous/current texts
        if self.model.slot_machine.spinning:
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

                # Spinning is now false. The user can hit spin again
                self.model.slot_machine.spinning = False

                # Set the prev results to the current images to be used again on animation
                self.model.slot_machine.set_prev_results_to_results()

                # Stop the spinning sound if playing
                self.view.spinning_snd.sound.stop()
                self.view.spinning_snd.is_playing = False

                self.view.spin_result.sound.play()
        else:
            # Display previous results if slot machine isn't spinning
            prev_results = self.model.slot_machine.prev_results
            self.display_slot_machine_icons(prev_results)

        return True

    def init_maze_game(self):
        self.view.draw_maze(self.model.maze)
        self.model.init_player(0, 0, self.view.OFFSET_X, self.view.OFFSET_Y)
        offset_coord = self.model.player.get_offset_px()
        self.view.init_player(offset_coord[0], offset_coord[1])

    def play_maze_game(self):
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

    def start_game(self):
        # self.init_slot_machine()
        # Continue looping while the player hasn't ended the game
        continue_playing = True
        self.init_maze_game()
        while continue_playing:
            # continue_playing = self.play_slot_machine()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    continue_playing = False

            self.play_maze_game()

            # Refresh the display
            pygame.display.flip()

        pygame.quit()


# Calls the main function
if __name__ == "__main__":
    c = Controller()
    c.start_game()
