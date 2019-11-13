import pygame
import random


class SlotMachine:
    def __init__(self):
        # Initialize sounds
        pygame.mixer.init()
        self.spin_snd = pygame.mixer.Sound('sounds/spin_snd.ogg')
        self.spinning_snd = pygame.mixer.Sound('sounds/itemreel.wav')
        self.spin_result = pygame.mixer.Sound('sounds/gotitem.wav')

        self.results = 3 * [0]

        self.icons = {}
        self.__create_icons()

    def __create_icons(self):
        self.icons['arnis'] = Icon('arnis', 'images/arnis.png')
        self.icons['bandana'] = Icon('bandana', 'images/bandana.png')
        self.icons['banyal'] = Icon('banyal', 'images/banyal.png')
        self.icons['camesa_de_chino'] = Icon('camesa_de_chino', 'images/camesa_de_chino.png')
        self.icons['katipunero_hat'] = Icon('katipunero_hat', 'images/katipunero_hat.png')
        self.icons['sadface'] = Icon('sadface', 'images/sadface.png')
        self.icons['siete'] = Icon('siete', 'images/siete.png')
        self.icons['tsinelas'] = Icon('tsinelas', 'images/tsinelas.png')

    def spin(self):
        # For each reel
        for spin in range(3):
            # Save the wildcard number as spinned_result
            spinned_result = random.randint(0, 100)

            if spinned_result in range(0, 40):  # 40% Chance
                self.results[spin] = self.icons[0].name
            elif spinned_result in range(40, 56):  # 16% Chance
                self.results[spin] = self.icons[1].name
            elif spinned_result in range(56, 70):  # 14% Chance
                self.results[spin] = self.icons[2].name
            elif spinned_result in range(70, 82):  # 12% Chance
                self.results[spin] = self.icons[3].name
            elif spinned_result in range(82, 89):  # 7% Chance
                self.results[spin] = self.icons[4].name
            elif spinned_result in range(89, 95):  # 6% Chance
                self.results[spin] = self.icons[5].name
            elif spinned_result in range(95, 99):  # 4% Chance
                self.results[spin] = self.icons[6].name
            elif spinned_result in range(99, 100):  # 1% Chance
                self.results[spin] = self.icons[7].name


class Icon(pygame.sprite.Sprite):
    def __init__(self, name, icon_image):
        self.name = name
        self.image = pygame.image.load("images/" + icon_image)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()


BACKGROUND_IMAGE_NAME = 'images/background.png'
GAME_TITLE = 'Slot Machine'


def start_game():
    # Assign the Display Variables
    background = pygame.image.load(BACKGROUND_IMAGE_NAME)
    screen = pygame.display.set_mode(background.get_size())
    pygame.display.set_caption(GAME_TITLE)

    # Create the slot machine object and hashes to be used by the game
    slot_machine = SlotMachine()
    spin_results = slot_machine.results
    icon_images = []  # The current icon images or spin result icons

    # Create all the symbols/icons to be shown in the reels
    all_symbols = pygame.sprite.Group()
    icons = slot_machine.icons
    for icon in icons:
        all_symbols.add(icon)

    # Set the game clock
    clock = pygame.time.Clock()

    # The reel positions is saved as an array with tuples
    reel_positions = [(75, 258), (265, 258), (445, 258)]

    # Add the spin result symbols to icon images
    for symbol in all_symbols:
        for symbol_name in spin_results:
            if (symbol.name == symbol_name):
                icon_images.append(symbol)

    # Set the variables to be used by the game loop
    start_time = 0
    spinning = False

    # Set the previous spin results
    prev_results = slot_machine.results

    # Play the bg music
    pygame.mixer.music.load("sounds/background_msc.wav")
    pygame.mixer.music.play(-1)

    # Set the current slot machine values as previous values
    prev_bet, prev_jackpot, prev_current_msg, prev_cash = slot_machine.bet, slot_machine.current_jackpot, slot_machine.current_message, slot_machine.current_cash

    # Create functions used to get the previous slot machine values
    def prev_get_bet():
        return prev_bet

    def prev_get_current_cash():
        return prev_cash

    def prev_get_current_jackpot():
        return prev_jackpot

    def prev_get_current_msg():
        return prev_current_msg

    # Set the text values as the previous values
    # The reason this is done is to not let the user see how much he won until the spin animation is done
    prev_bet_digifont = DigitalFont(prev_get_bet, (245, 424))
    prev_cash_digifont = DigitalFont(prev_get_current_cash, (80, 424))
    prev_jackpot_digifont = DigitalFont(prev_get_current_jackpot, (445, 424))
    prev_message_digifont = DigitalFont(prev_get_current_msg, (100, 140), (0, 0, 0))

    # Create the sprite group digifonts
    # The prev digifonts are the ones to be shown to the user while the spin animation is still running.
    prev_digifonts = pygame.sprite.Group(prev_bet_digifont, prev_jackpot_digifont, prev_cash_digifont,
                                         prev_message_digifont)

    # Continue looping while the player hasn't ended the game
    continue_playing = True
    while (continue_playing):
        # Tick
        clock.tick(FRAME_RATE)

        # Check for events
        for event in pygame.event.get():
            # Stop the loop when the user chooses to quit the game
            if event.type == pygame.QUIT:
                continue_playing = False
            # When the user pushes the mouse button down, Check which sprites are involved
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if a bet button is clicked then set the bet value to the value of that button
                for bet_button in bet_buttons:
                    if bet_button.rect.collidepoint(event.pos):
                        slot_machine.set_bet(bet_button.bet_value)
                # Check if spin button is clicked
                if spin_button.rect.collidepoint(event.pos):
                    # Make sure you cant click the spin button while the reels are spinning
                    if not spinning:
                        # Execute the function inside the spin button. It would be slot_machine.spin()
                        spin_button.execute_func()
                        # If the message in the slot machine says the user cannot spin the reels, nothing happens.
                        # But if it is not then do the spin and set the spin results in the icon images
                        if slot_machine.current_message != SlotMachine.CANNOT_SPIN:
                            spin_results = slot_machine.results

                            # Set the result's icon into icon_images
                            icon_images = []
                            for symbol in all_symbols:
                                for symbol_name in spin_results:
                                    if symbol.name == symbol_name:
                                        icon_images.append(symbol)

                            # Set the start time to current time. Making the spin animation run
                            start_time = time.time()

                            # Set spinning to true to make sure the user can't click spin again while spinning
                            spinning = True
                        else:
                            slot_machine.bet_no_cash_snd.play()
                # If it is the reset button, call the function associated with the button and play the reset sound
                elif reset_button.rect.collidepoint(event.pos):
                    slot_machine.reset_snd.play()
                    reset_button.execute_func()
                # If the quit button is clicked, stop the loop
                elif quit_button.rect.collidepoint(event.pos):
                    continue_playing = False

        # Display the sprites

        # Display the background image
        screen.blit(background, background.get_rect())

        # Update the action buttons and position them on the screen
        action_buttons.update()
        for action_button in action_buttons:
            screen.blit(action_button.image, action_button.pos)

        # Update the texts
        digital_fonts.update()

        # Update the bet buttons and position them on the screen
        bet_buttons.update()
        for bet_button in bet_buttons:
            screen.blit(bet_button.image, bet_button.pos)

        # This section is the one responsible for the reel animation
        # While the current time - the time the spin button is clicked is less than one
        # Change the images in the reel and show the previous/current texts
        if time.time() - start_time < 1 and spinning:
            # Display the current icons in the reel so it does not change until the pulling the lever sound is finished
            for i in range(3):
                screen.blit(prev_results[i].image, reel_positions[i])
            # Display the current texts
            for digital_font in prev_digifonts:
                screen.blit(digital_font.get_rendered_surface(), digital_font.pos)
        if 1 < time.time() - start_time < 2 and spinning:
            # Display a random icon in each reel and play the spinning sound
            for i in range(3):
                screen.blit(icons[random.randint(0, len(icons) - 1)].image, reel_positions[i])
            slot_machine.spinning_snd.play()
            # Display the current texts
            for digital_font in prev_digifonts:
                screen.blit(digital_font.get_rendered_surface(), digital_font.pos)
        elif time.time() - start_time > 2:
            # The animation is done and display the resulted values
            for i in range(3):
                screen.blit(icon_images[i].image, reel_positions[i])
            screen.blit(current_message_digifont.get_rendered_surface(), current_message_digifont.pos)
            # Spinning is now false. The user can hit spin again
            spinning = False
            # Set the prev results to the current images to be used again on animation
            prev_results = icon_images
            # Stop the spinning sound if playing
            slot_machine.spinning_snd.stop()
            # Render the current texts in the screen
            for digital_font in digital_fonts:
                screen.blit(digital_font.get_rendered_surface(), digital_font.pos)

            # Reset the prev values
            prev_bet, prev_jackpot, prev_current_msg, prev_cash = slot_machine.bet, slot_machine.current_jackpot, slot_machine.current_message, slot_machine.current_cash

        # Refresh the display
        pygame.display.flip()


# Calls the main function
if __name__ == "__main__":
    start_game()





