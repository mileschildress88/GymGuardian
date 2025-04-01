import pygame
import sys
from src.game import Game

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Gym Guardian: Defend the Gains")
clock = pygame.time.Clock()

def main():
    game = Game(screen)
    running = True

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            result = game.handle_event(event)
            if result == "quit":
                running = False

        # Update game state
        game.update()

        # Draw everything
        screen.fill(BLACK)
        game.draw()
        pygame.display.flip()

        # Cap the framerate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 