#1. game foundation (requires "graphics" setup to run)
import pygame
import sys
import random

#2. Initalize Pygame
pygame.init()

#3. Screen dimensions (Canvas)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mobility Maneuvers: Wheelchair Wonderland!")

#4. Core Variables
clock = pygame.time.Clock()
FPS = 60

# Colors for placeholders
white = (255, 255, 255)
blue = (0, 0, 255)
dark_gray = (50, 50, 50)

class Player:
    def __init__(self):
        # <u>A movable player square that is 32 x 32 px</u>
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, 32, 32)
        self.color = blue
        self.speed = 5

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Obstacle:
    def __init__(self, x, y, wall_margin):
        # A 32 x 32 pixel hazard
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = (255, 0, 0) # Red for dangers
        self.base_speed = 1 # Speed at which the obstacle moves towards the player.

        self.dx = random.choice([-3, 3])
        self.wall_margin = wall_margin

    def update(self, scroll_amount, SCREEN_WIDTH):
        # Obstacle moves at a speed of it's own and the world's combined.
        self.rect.y += self.base_speed + scroll_amount

        # Horizontal movement
        self.rect.x += self.dx

        # Bounce off Walls
        if self.rect.left <= self.wall_margin:
            self.rect.left = self.wall_margin
            self.dx *= -1 # Reverses direction
        
        elif self.rect.right >= SCREEN_WIDTH - self.wall_margin:
            self.rect.right = SCREEN_WIDTH - self.wall_margin
            self.dx *= -1 # Reverses direction

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Environmental Variables
# <u>A background the scrolls down as the player moves, which gives the illusion of movement.
bg_scroll_y = 0
scroll_speed = 4

# <u>Walls on each side that are impassible within a distance. (tbd)
wall_margin = 150 # Change this value to adjust hallway width.

# Main game Loop
# Create entities before the loop begins
player = Player()
# Spawn an obstacle in the middle of the hall, just above the visible screen.
#removed# obstacle1 = Obstacle(SCREEN_WIDTH // 2, -50, wall_margin)

# Obstacle Management List:
active_obstacles = []

# Custom Pygame event for spawning:
SPAWN_OBSTACLE = pygame.USEREVENT + 1

# Set timer to trigger the SPAWN_OBSTACLE event every 1.5 seconds (1500ms)
pygame.time.set_timer(SPAWN_OBSTACLE, 1500)

running = True

while running:
    # 1. Event handling.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Spawn a new obstacle when the timer ticks.
        if event.type == SPAWN_OBSTACLE:
            # Pick a random starting X positions within the hallway.
            spawn_x = random.randint(wall_margin, SCREEN_WIDTH - wall_margin - 32)
            new_obstacle = Obstacle(spawn_x, -50, wall_margin)
            active_obstacles.append(new_obstacle)

# 2. Player Input/Movement.
keys = pygame.key.get_pressed()

if keys[pygame.K_LEFT]:
    player.rect.x -= player.speed
if keys[pygame.K_RIGHT]:
    player.rect.x += player.speed

scroll_amount = 0
if keys[pygame.K_UP]:
    scroll_amount = scroll_speed
    bg_scroll_y += scroll_amount

# 3. Collision Detectors (Player and Walls)
if player.rect.left < wall_margin:
    if player.rect.right > SCREEN_WIDTH - wall_margin:
        player.rect.right = SCREEN_WIDTH - wall_margin

# 4. Environmental/Entity updates
# We iterate over a copy of the list with [:] so we can safely remove the items.
for obs in active_obstacles[:]:
    obs.update(scroll_amount, SCREEN_WIDTH)

    # Player collides with Obstacle.
    if player.rect.colliderect(obs.rect):
        print("Sorry, I did not see you there!")
        
    # Memory Manager: delete obstacle if it goes off the screen.
    if obs.rect.top > SCREEN_HEIGHT:
        active_obstacles.remove(obs)

while running:
    #1. Game exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

#2. Player Input/movement
keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.rect.x -= player.speed
    if keys[pygame.K_RIGHT]:
        player.rect.x += player.speed

    # Moving "forward" scrolls instead of moving the player upwards.
    scroll_amount = 0
    if keys[pygame.K_UP]:
        bg_scroll_y += scroll_speed

    #3. Environmental/Entity updates
    # Pass the scroll_amount to the obstacle so it moves correctly.
    obstacle1.update(scroll_amount)

    #4. <u>Collision detector/Hitboxes</u> (Game boundaries)
    if player.rect.left < wall_margin:
        player.rect.left = wall_margin
    if player.rect.right > SCREEN_WIDTH - wall_margin:
        player.rect.right = SCREEN_WIDTH - wall_margin
    
    # Obstacle Collisions
    if player.rect.colliderect(obstacle1.rect):
        print("Sorry!")
    # Later, add logic to reduce speed, deduct points, or restart...

    #5. Drawing
    screen.fill(dark_gray) # Loads the background

    # Draw Walls
    pygame.draw.rect(screen, white, (0, 0, wall_margin, SCREEN_HEIGHT))
    pygame.draw.rect(screen, white, (SCREEN_WIDTH - wall_margin, 0, wall_margin, SCREEN_HEIGHT))

    # Draw all active obstacles.
    for obs in active_obstacles:
        obs.draw(screen)

    obstacle1.draw(screen)
    player.draw(screen)

    # Frame Rendering
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()