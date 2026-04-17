# Cannot download pygame unless file is set up in "graphics" mode.
import pygame   # game foundation
import sys

# 1. Setup
pygame.init()
canvas = pygame.display.set_mode((400, 400))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
running = true

while running:

# Variables to track our player
px = 200
py = 200

# 2. The Game Loop
def update():
    global px, py

    canvas.fill((0, 0, 0)) # Erase the previous frame

    # Input & Logic
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        px -= 5
    if keys[pygame.K_RIGHT]:
        px += 5
    if keys[pygame.K_UP]:
        py -= 5
    if keys[pygame.K_DOWN]:
        py += 5

    # Drawing
    pygame.draw.rect(canvas, (0, 255, 0), (px, py, 40, 40)) # Lime colour

    pygame.display.flip() # Push the new frame to the screen

# 3. Run
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    update()
    clock.tick(60) # Locks to 60 FPS
