# 1. Game Foundation
import pygame
import sys
import random

# 1.1. Initialize Pygame
pygame.display.init()

# 1.2. Screen dimensions (Canvas)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mobility Maneuvers: Hollering Halls!")

# 1.3. Core Variables
clock = pygame.time.Clock()
FPS = 60

# 1.4. Colors
white = (255, 255, 255)
blue = (0, 0, 255)
dark_gray = (50, 50, 50)
black = (0, 0, 0)

# 1.5. Fonts for UI and scoring
pygame.font.init() # this keeps the font module active
sys_font = pygame.font.SysFont(None, 36) # sets default font size to '36'

#1.6. Class List

class Player:
    def __init__(self):
        # A movable player square that is 32 x 32 px
        self.moving_left = False
        self.moving_right = False
        self.sprinting = False
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, 32, 32)
        self.color = blue
        
        # Base and boosted speeds
        self.base_speed = 2
        self.speed = self.base_speed
        
        # Boost end timer
        self.boost_end_time = 0
        self.sprint_multiplier = 1.0
        
        # Toggles hazard collisions 
        self.is_penalized = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Obstacle:
    def __init__(self, x, y, wall_margin):
        # A 32 x 32 pixel hazard
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = (255, 0, 0) # Red for obstacles
        
        self.base_speed = 0.5 # Speed at which the obstacle moves towards the player.
        self.dx = random.choice([-1.5, 1.5]) # Slower horizontal speed
        self.wall_margin = wall_margin

        # Track exact position with floats
        self.exact_x = float(x)
        self.exact_y = float(y)

    def update(self, scroll_amount, SCREEN_WIDTH):
        
        # Obstacle moves at a speed of its own and the world's combined.
        self.exact_y += self.base_speed + scroll_amount
        self.exact_x += self.dx

        # Horizontal movement
        self.rect.y = int(self.exact_y)
        self.rect.x = int(self.exact_x)

        # Bounce off Walls
        if self.rect.left <= self.wall_margin:
            self.rect.left = self.wall_margin
            self.exact_x = float(self.rect.x) # Resyncs float after bounce
            self.dx *= -1 # Reverses direction
        
        elif self.rect.right >= SCREEN_WIDTH - self.wall_margin:
            self.rect.right = SCREEN_WIDTH - self.wall_margin
            self.exact_x = float(self.rect.x) # Resyncs float after bounce
            self.dx *= -1 # Reverses direction

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        
class Boost:
    def __init__(self, x, y):
        # A 16 x 16 item
        self.rect = pygame.Rect(x, y, 16, 16)
        self.color = (0, 255, 0) # Green for boosts
        
        # Position tracking for smooth movement
        self.exact_y = float(y)
        # Boosts come in slightly faster than the hallway
        self.base_speed = 1.0
        
    def update(self, scroll_amount):
        # Boosts move straight down
        self.exact_y += self.base_speed + scroll_amount
        self.rect.y = int(self.exact_y)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        
class Door:
    def __init__(self, wall_margin, SCREEN_WIDTH):
        # Calculate the width of the playable hallway
        width = SCREEN_WIDTH - (wall_margin * 2)
        
        # Currently a 50 px rectangle, spanning the wall; spawns out of view
        self.rect = pygame.Rect(wall_margin, -100, width, 50)
        self.color = (255, 215, 0) # Gold finish line
        self.exact_y = float(-100)
        
    def update(self, scroll_amount):
        # The "door" comes down at the world scroll pace
        self.exact_y += scroll_amount
        self.rect.y = int(self.exact_y)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        
# --- Master Loop --- #
player_name = " " # Remember the player's name between plays.
play_again = True

while play_again:
    

# --- 2.0 Environmental Variables
# A background that scrolls down as the player moves, which gives the illusion of movement.
bg_scroll_y = 0
base_scroll_speed = 1
scroll_speed = base_scroll_speed

# Walls on each side that are impassible within a distance.
wall_margin = 150 # Change this value to adjust hallway width.

# Create entities before the loop begins
player = Player()

# Obstacle Manager:
active_obstacles = []

# Custom Pygame event for spawning:
SPAWN_OBSTACLE = pygame.USEREVENT + 1

# Set timer to trigger the SPAWN_OBSTACLE event every 1.5 seconds (1500ms)
pygame.time.set_timer(SPAWN_OBSTACLE, 1500)

# Boost Manager
active_boosts = []

# Boost spawner
SPAWN_BOOST = pygame.USEREVENT + 2

# Set timer to spawn boosts every 5 seconds (5000ms)
pygame.time.set_timer(SPAWN_BOOST, 5000)

door = None
door_spawned = False
level_complete = False
final_time = 0.0 # Variable can be determined here.

# --- Menu and leaderboard variables
player_name = ""
menu_running = True
input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 40)

# Add a start button
start_button = pygame.Rect
toggle_button = pygame.Rect(SCREEN_WIDTH //2 - 100, SCREEN_HEIGHT // 2 + 120, 200, 40)
auto_sprint = False # False means Manual Chair, True = Power Chair
(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 60, 100, 40)
color_active = pygame.Color('lightskyblue3')
color_passive = pygame.Color('chartreuse4')
input_color = color_passive
input_active = False

# The mobile keyboard module is awoken by pygame\
try:
    pygame.key.start_text_input()
except AttributeError:
    pass # older pygame versions will ignore this
    

# --- Menu Screen Loop ---
while menu_running:
    screen.fill(dark_gray)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        # Click the mouse on input box
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Accessibility Mode option toggle
            if toggle_button.collidepoint(event.pos):
                auto_sprint = not auto_sprint # toggles True or False
            # Tap the box
            if input_rect.collidepoint(event.pos):
                input_active = True
                input_color = color_active
            else:
                input_active = False
                input_color = color_passive
            
            # Tap the start button
            if start_button.collidepoint(event.pos):
                if len(player_name) > 0: # It only starts if a name is typed
                    try:
                        pygame.key.stop_text_input() # Hides the mobile keyboard
                    except AttributeError:
                        pass
                    menu_running = False
                    
        # Capture text for Mobile devices and keyboard typing
        if event.type == pygame.TEXTINPUT:
                if input_active:
                    # Only allow text that is a readable character
                    for char in event.text:
                        if char.isalnum() or char == " ":
                            player_name += char
                    
        if event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    # Exit the menu and start the game by pressing ENTER
                    if len(player_name) > 0:
                        player_name = player_name[:-1]
                        try:
                            pygame.key.stop_text_input()
                        except AttributeError:
                            pass
                        menu_running = False
                elif event.key == pygame.K_BACKSPACE:
                    # Only delete characters if there is one to delete
                    if len(player_name) > 0:
                    # Allows mistypes to be deleted
                        player_name = player_name[:-1]
                    # Allows typing of player names
                        # (removed due to conflict with text box typing on Chrome OS) player_name += event.unicode
 
                    
    # --- Draws the menu text
    title_text = sys_font.render("Mobility Maneuvers: Wheelchair Wonderland!!", True, white)
    prompt_text = sys_font.render("Please click on the box, type your name, and press ENTER: ", True, white)

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    
    # Draws the text box
    pygame.draw.rect(screen, input_color, input_rect, 2)
    
    # Draws name in box
    name_surface= sys_font.render(player_name, True, white)
    screen.blit(name_surface, (input_rect.x + 5, input_rect.y + 5))
    
    # Resize the box to fit the name
    input_rect.w = max(200, name_surface.get_width() + 10)
    
    # Draws a start button
    button_color = (255, 140, 0)
    start_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 60, 100, 40)
    pygame.draw.rect(screen, button_color, start_button)
    start_text = sys_font.render("START", True, white)
    screen.blit(start_text, (start_button.x + 10, start_button.y + 10))

    # Draws the Accessibility button
    
    # Toggles text on Accessibility button
    if auto_sprint:
        mode_text = sys_font.render("Mode: Power Wheelchair", True, white)
    else:
        mode_text = sys_font.render("Mode: Manual Wheelchair", True, white)

    # Dynamic resizing of the button width
    text_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))
    # toggle_button.x = (SCREEN_WIDTH // 2) - (toggle_button.width // 2)

    # Enlarge the box (30px/w, 20px/h)
    toggle_button = text_rect.inflate(30, 20)
    
    # Draws the Accessibility button
    pygame.draw.rect(screen, color_passive, toggle_button)

    # Set toggle button text to centered
    screen.blit(mode_text, text_rect)
    
    pygame.display.flip()
    clock.tick(FPS)
    
# --- End of menu loop ---

# After the player presses enter...

# Stamp the clock right before the game loop begins
start_time = pygame.time.get_ticks()

running = True

# --- THE SINGLE MAIN GAME LOOP ---
while running:
    # 1. Event handling.
    for event in pygame.event.get():
        
        # 1.1. Quit out
        if event.type == pygame.QUIT:
            running = False
            
            # Key compatibility for Chrome OS
            # Keys toggle 'on'
            # if event.type == pygame.KEYDOWN:
                # if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    # player.moving_left = True
                # if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    # player.moving_right = True
                # if event.key == pygame.K_UP or event.key == pygame.K_w:
                    # player.sprinting = True
                # print("Key registered: ", event.key)
                
            # Keys toggle 'off'
            # if event.type == pygame.KEYUP:
                # if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    # player.moving_left = False
                # if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    # player.moving_right = False
                # if event.key == pygame.K_UP or event.key -- pygame.K_w:
                    # player.sprinting = False

        # Spawn a new obstacle when the timer ticks.
        if event.type == SPAWN_OBSTACLE:
            # Pick a random starting X position within the hallway.
            spawn_x = random.randint(wall_margin, SCREEN_WIDTH - wall_margin - 32)
            new_obstacle = Obstacle(spawn_x, -50, wall_margin)
            active_obstacles.append(new_obstacle)
            
        # Spawn a new boost when the timer ticks.
        if event.type == SPAWN_BOOST:
            spawn_x = random.randint(wall_margin, SCREEN_WIDTH - wall_margin - 32)
            new_boost = Boost(spawn_x, -50)
            active_boosts.append(new_boost)

    # 2. Player Input/Movement.
    
    # Chrome OS compatible movement based on custom switches in # 1.
    # if player.moving_left:
        # player.rect.x -= player.speed
    # if player.moving_right:
        # player.rect.x += player.speed
            
    keys = pygame.key.get_pressed()
        
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.rect.x -= player.speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.rect.x += player.speed
            
    # Wheelchair auto-scroll
    scroll_amount = scroll_speed / 2

    if auto_sprint:
        # Accessibility Mode: Always move at max speed as if holding down the UP arrow or W key
        scroll_amount = scroll_speed * player.sprint_multiplier
    else:
        # Unassisted Mode: Hold the UP arrow, or W key (Win/Mac) to increase speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            scroll_amount = scroll_speed * player.sprint_multiplier
        
    # Chrome OS compatible sprint switch tracker
    # if player.sprinting:
        # scroll_amount = scroll_speed
        
    # if keys[pygame.K_UP] or keys[pygame.K_w]:
        # scroll_amount = scroll_speed
            
    # Adds scroll amount to background tracking
    bg_scroll_y += scroll_amount
        
    # --- Boost Cooldown Checker ---
    # If boosted, check the clock
    if player.speed > player.base_speed:
        current_time = pygame.time.get_ticks()
        
        # If time expires, revert the speed to normal
        if current_time >= player.boost_end_time:
            player.speed = player.base_speed
            # Optional: testing expiration!
            print("That was fun!")

    # 3. Collision Detectors (Player and Walls)
    if player.rect.left < wall_margin:
        player.rect.left = wall_margin
    if player.rect.right > SCREEN_WIDTH - wall_margin:
        player.rect.right = SCREEN_WIDTH - wall_margin

    # 4. Environmental/Entity updates
    
    # Assume player is safe in each frame unless toggled
    player.is_penalized = False
    
    # We iterate over a copy of the list with [:] so we can safely remove the items.
    for obs in active_obstacles[:]:
        obs.update(scroll_amount, SCREEN_WIDTH)

        # Player collides with Obstacle.
        if player.rect.colliderect(obs.rect):
            player.is_penalized = True # Add collision logic here later!
            # print("Sorry, I did not see you there!")
            
        # Memory Manager: delete obstacle if it goes off the screen.
        if obs.rect.top > SCREEN_HEIGHT:
            active_obstacles.remove(obs)
            
        # Applies slowdown mechanics
        if player.is_penalized:
            # Reduce player movement speed significantly
            player.speed = 0.5
            scroll_speed = 0.25
        else:
            # Restore player default speed IF there are no active boosts
            if player.speed < player.base_speed:
                player.speed = player.base_speed
            scroll_speed = base_scroll_speed
            
    # Iterate over a copied boosts list
    for boost in active_boosts[:]:
        boost.update(scroll_amount)
        
        # Detecting pickups
        if player.rect.colliderect(boost.rect):
            # Grant the boost
            # player.speed += 2 # increases player scroll speed
            
            # Expiration timer
            player.boost_end_time = pygame.time.get_ticks() + 2000
            
            # Boost removal
            active_boosts.remove(boost) # Removes the item on screen

        # Memory manager: delete offscreen
        elif boost.rect.top > SCREEN_HEIGHT:
            active_boosts.remove(boost)

        # New boost effect
        if pygame.time.get_ticks() < player.boost_end_time:
            player.sprint_multiplier = 2.0 # 2x faster scrolling
        else:
            player.sprint_multiplier = 1.0 # Normal speed
            
    # --- End door logic ---
    
    # 1. Spawn door at distance (14,400pxs/60s ideal scroll distance)
    if bg_scroll_y >= 3000 and not door_spawned:
        door = Door(wall_margin, SCREEN_WIDTH)
        door_spawned = True
        
    # 2. Update and draw the door
    if door_spawned:
        door.update(scroll_amount)
        
        # Detect the win condition
        if player.rect.colliderect(door.rect):
            # Determine the time (secs)
            final_time = (pygame.time.get_ticks() - start_time) / 1000.0

            level_complete = True
            running = False # ends the main game loop

    # 5. Drawing
    screen.fill(dark_gray) # Loads the background

    # Draw Walls
    pygame.draw.rect(screen, white, (0, 0, wall_margin, SCREEN_HEIGHT))
    pygame.draw.rect(screen, white, (SCREEN_WIDTH - wall_margin, 0, wall_margin, SCREEN_HEIGHT))

    # Draw all active obstacles.
    for obs in active_obstacles:
        obs.draw(screen)
        
    # Draw all active boosts
    for boost in active_boosts:
        boost.draw(screen)
        
    # Draw the door if it has spawned
    if door_spawned:
        door.draw(screen)

    player.draw(screen)
    
    # --> UI/Text Rendering <--
    
    # 5.1. Distance score calculation
    current_time = pygame.time.get_ticks()
    elapsed_seconds = (current_time - start_time) // 1000
    
    # - score = bg_scroll_y // 100
    
    # 5.2. Fully render the text in an image (text, anti-aliasing, colour)
    timer_text = sys_font.render(f"Time: {elapsed_seconds}s", True, black)
    
    # - score_text = sys_font.render(f"Distance: {score}m", True, black)
    
    # 5.3. Draw (blit) the text image on the screen at x = 10, y = 10 (top left screen corner)
    screen.blit(timer_text, (10, 10))
    
    # - screen.blit(score_text, (10, 10))

    # Frame Rendering
    pygame.display.flip()
    clock.tick(FPS)

# --- Endgame Loop --- #
end_running = True

# Replay button (ellipse/oval)
replay_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 50)
replay_button_color = (0, 255, 255) # Cyan

while end_running:
    screen.fill((30, 30, 50)) # Dark blue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end_running = False

        # Replay button click response
        if event.type == pygame.MOUSEBUTTONDOWN:
            if replay_button.collidepoint(event.pos):
                print("Reloading Game... (logic pending!)")
                end_running = False

    # --- Endgame Text --- #
    # 1. Completion Praise
    congrats_text = sys_font.render(f"Congratulations {player_name}, you made it!", True, (255, 255, 0))
    screen.blit(congrats_text, (SCREEN_WIDTH // 2 - congrats_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

    # 2. Show end time and round to two decimals (only renders if the level is completed)
    if level_complete:
        time_text = sys_font.render(f"Finish Time: {final_time:.2f} seconds", True, (255, 215, 0))
        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

    # 3. Draw the replay button
    play_text = sys_font.render("Play Again?", True, (255, 255, 255))
    text_x = replay_button.x + (replay_button.width - play_text.get_width()) // 2
    text_y = replay_button.y + (replay_button.height - play_text.get_height()) // 2
    screen.blit(play_text, (text_x, text_y))

    pygame.display.flip()
    clock.tick(FPS)

# --- Final Quit Game Logic --- #
pygame.quit()
sys.exit()