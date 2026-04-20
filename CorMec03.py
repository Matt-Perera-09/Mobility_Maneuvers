# 1. Game Foundation
import pygame
import sys
import random

# 2. Initialize Pygame
pygame.display.init()

# 3. Screen dimensions (Canvas)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mobility Maneuvers: Hollering Halls!")

# 4. Core Variables
clock = pygame.time.Clock()
FPS = 60

# Colors
white = (255, 255, 255)
blue = (0, 0, 255)
dark_gray = (50, 50, 50)
black = (0, 0, 0)

# Fonts for UI and scoring
pygame.font.init() # this keeps the font module active
sys_font = pygame.font.SysFont(None, 36) # sets default font size to '36'

class Player:
    def __init__(self):
        # A movable player square that is 32 x 32 px
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, 32, 32)
        self.color = blue
        
        # Base and boosted speeds
        self.base_speed = 2
        self.speed = self.base_speed
        
        # Boost end timer
        self.boost_end_time = 0
        
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

# Environmental Variables
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

# --- Menu and leaderboard variables
player_name = ""
menu_running = True
input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 40)

# Add a start button
start_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 60, 100, 40)
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
                        if ord(char) < 128 and char.isprintable():
                            player_name += char
                    
        if event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    # Exit the menu and start the game by pressing ENTER
                    if len(player_name) > 0:
                        try:
                            pygame.key.stop_text_input()
                        except AttributeError:
                            pass
                        menu_running = False
                elif event.key == pygame.K_BACKSPACE:
                    # Allows mistypes to be deleted
                    player_name = player_name[:-1]
                    # Allows typing of player names
                    player_name += event.unicode
 
                    
    # --- Draws the menu text
    title_text = sys_font.render("Wheelchair Wonderland!!", True, white)
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
    pygame.draw.rect(screen, button_color, start_button)
    start_text = sys_font.render("START", True, white)
    screen.blit(start_text, (start_button.x + 10, start_button.y + 10))
    
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
        if event.type == pygame.QUIT:
            running = False
            
            # Diagnostics check: print the key ID when pressed
            if event.type == pygame.KEYDOWN:
                print("Key registered: ", event.key)

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
    # NOTICE: This is indented 4 spaces so it remains INSIDE the while loop!
    keys = pygame.key.get_pressed()

    # Check the left arrow OR the 'a' key 
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.rect.x -= player.speed
    # Check the right arrow OR the 'd' key
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.rect.x += player.speed

    # Moving "forward" scrolls instead of moving the player upwards.
    scroll_amount = scroll_speed / 2
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        scroll_amount = scroll_speed
    
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
            
  