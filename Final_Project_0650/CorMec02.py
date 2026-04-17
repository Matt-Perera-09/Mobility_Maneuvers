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
sys_font = pygame.font.SysFont(None, 24) # sets default font size to '24'

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
    scroll_amount = 0
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
            
        # Applies slowdown mechanics
        if player.is_penalized:
            # Reduce player movement speed significantly
            player.speed = 0.5
            scroll_speed = 0.25
        else:
            # Restore player strafe speed IF there are no active boosts
            if player.speed < player.base_speed:
                player.speed = player.base_speed
            scroll_speed = base_scroll_speed
            
    # Iterate over a copied boosts list
    for boost in active_boosts[:]:
        boost.update(scroll_amount)
        
        # Detecting pickups
        if player.rect.colliderect(boost.rect):
            # Grant the boost
            player.speed += 2 # increases player strafe speed
            
            # Expiration timer
            player.boost_end_time = pygame.time.get_ticks() + 2000
            
            # Boost removal
            active_boosts.remove(boost) # Removes the item on screen
            
        # Memory manager: delete offscreen
        elif boost.rect.top > SCREEN_HEIGHT:
            active_boosts.remove(boost)

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

    player.draw(screen)
    
    # --> UI/Text Rendering <--
    
    # 5.1. Distance score calculation
    score = bg_scroll_y // 100
    
    # 5.2. Fully render the text in an image (text, anti-aliasing, colour)
    score_text = sys_font.render(f"Distance: {score}m", True, black)
    
    # 5.3. Draw (blit) the text image on the screen at x = 10, y = 10 (top left screen corner)
    screen.blit(score_text, (10, 10))

    # Frame Rendering
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()