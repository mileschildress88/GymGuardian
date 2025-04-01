import pygame

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font_big = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 100, 255)
        
        # Button dimensions
        self.button_width = 200
        self.button_height = 50
        
        # Create buttons
        self.start_button = pygame.Rect(
            self.width//2 - self.button_width//2,
            self.height//2,
            self.button_width,
            self.button_height
        )
        
        self.quit_button = pygame.Rect(
            self.width//2 - self.button_width//2,
            self.height//2 + 70,
            self.button_width,
            self.button_height
        )
        
        # Game over screen buttons
        self.retry_button = pygame.Rect(
            self.width//2 - self.button_width//2,
            self.height//2 + 50,
            self.button_width,
            self.button_height
        )
        
        self.change_map_button = pygame.Rect(
            self.width//2 - self.button_width//2,
            self.height//2 + 120,
            self.button_width,
            self.button_height
        )
        
        self.exit_button = pygame.Rect(
            self.width//2 - self.button_width//2,
            self.height//2 + 190,
            self.button_width,
            self.button_height
        )

    def draw(self, screen, screen_type):
        if screen_type == "home":
            self.draw_home_screen()
        elif screen_type == "game_over":
            self.draw_game_over_screen()

    def draw_home_screen(self):
        # Draw background
        self.screen.fill(self.BLACK)
        
        # Draw title
        title = self.font_big.render("Gym Guardian", True, self.WHITE)
        title_rect = title.get_rect(center=(self.width//2, self.height//3))
        self.screen.blit(title, title_rect)
        
        # Draw subtitle
        subtitle = self.font_medium.render("Defend the Gains!", True, self.GREEN)
        subtitle_rect = subtitle.get_rect(center=(self.width//2, self.height//3 + 60))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Draw buttons
        pygame.draw.rect(self.screen, self.GREEN, self.start_button)
        pygame.draw.rect(self.screen, self.RED, self.quit_button)
        
        # Draw button text
        start_text = self.font_small.render("Start Game", True, self.BLACK)
        quit_text = self.font_small.render("Quit", True, self.BLACK)
        
        start_text_rect = start_text.get_rect(center=self.start_button.center)
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        
        self.screen.blit(start_text, start_text_rect)
        self.screen.blit(quit_text, quit_text_rect)
        
        # Draw instructions
        instructions = [
            "Controls:",
            "Left Click: Place/Select towers",
            "Right Click: Cancel tower placement",
            "Space: Start/Pause wave",
            "1-6: Select tower types",
            "Q,W,E,R: Activate power-ups"
        ]
        
        for i, text in enumerate(instructions):
            instruction_text = self.font_small.render(text, True, self.WHITE)
            self.screen.blit(instruction_text, (50, self.height - 200 + i * 30))

    def draw_game_over_screen(self):
        # Draw semi-transparent background
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill(self.BLACK)
        overlay.set_alpha(200)  # More opaque
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over = self.font_big.render("Game Over", True, self.RED)
        game_over_rect = game_over.get_rect(center=(self.width//2, self.height//3))
        self.screen.blit(game_over, game_over_rect)
        
        # Draw buttons
        pygame.draw.rect(self.screen, self.GREEN, self.retry_button)
        pygame.draw.rect(self.screen, self.BLUE, self.change_map_button)
        pygame.draw.rect(self.screen, self.RED, self.exit_button)
        
        # Draw button text
        retry_text = self.font_small.render("Retry", True, self.BLACK)
        change_map_text = self.font_small.render("Change Map", True, self.BLACK)
        exit_text = self.font_small.render("Exit to Menu", True, self.BLACK)
        
        retry_text_rect = retry_text.get_rect(center=self.retry_button.center)
        change_map_text_rect = change_map_text.get_rect(center=self.change_map_button.center)
        exit_text_rect = exit_text.get_rect(center=self.exit_button.center)
        
        self.screen.blit(retry_text, retry_text_rect)
        self.screen.blit(change_map_text, change_map_text_rect)
        self.screen.blit(exit_text, exit_text_rect)

    def handle_click(self, pos, screen_type):
        if screen_type == "home":
            if self.start_button.collidepoint(pos):
                return "start"
            elif self.quit_button.collidepoint(pos):
                return "quit"
        elif screen_type == "game_over":
            if self.retry_button.collidepoint(pos):
                return "retry"
            elif self.change_map_button.collidepoint(pos):
                return "change_map"
            elif self.exit_button.collidepoint(pos):
                return "exit"
        return None 