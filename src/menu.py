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
        
        self.restart_button = pygame.Rect(
            self.width//2 - self.button_width//2,
            self.height//2,
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

    def draw_game_over_screen(self, wave, gold):
        # Draw semi-transparent background
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over = self.font_big.render("Game Over", True, self.RED)
        game_over_rect = game_over.get_rect(center=(self.width//2, self.height//3))
        self.screen.blit(game_over, game_over_rect)
        
        # Draw stats
        stats = [
            f"Wave Reached: {wave}",
            f"Gold Earned: {gold}"
        ]
        
        for i, text in enumerate(stats):
            stat_text = self.font_medium.render(text, True, self.WHITE)
            stat_rect = stat_text.get_rect(center=(self.width//2, self.height//2 + i * 40))
            self.screen.blit(stat_text, stat_rect)
        
        # Draw restart button
        pygame.draw.rect(self.screen, self.GREEN, self.restart_button)
        restart_text = self.font_small.render("Play Again", True, self.BLACK)
        restart_text_rect = restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(restart_text, restart_text_rect)

    def handle_click(self, pos, screen_type):
        if screen_type == "home":
            if self.start_button.collidepoint(pos):
                return "start"
            elif self.quit_button.collidepoint(pos):
                return "quit"
        elif screen_type == "game_over":
            if self.restart_button.collidepoint(pos):
                return "restart"
            elif self.quit_button.collidepoint(pos):
                return "quit"
        return None 