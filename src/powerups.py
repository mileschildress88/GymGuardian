import pygame
import math

class PowerUp:
    def __init__(self, name, key, cost):
        self.name = name
        self.key = key
        self.cost = cost
        self.active = False
        self.duration = 0
        self.cooldown = 0
        
        # Set color and description based on power-up type
        if 'Pre-Workout' in name:
            self.color = (255, 165, 0)  # Orange
            self.description = "All towers fire 2x faster for 10 seconds"
            self.cooldown_time = 30000  # 30 seconds
        elif 'Cheat Meal' in name:
            self.color = (255, 0, 0)    # Red
            self.description = "Massive explosion that clears a large area but reduces gold reward"
            self.cooldown_time = 45000  # 45 seconds
        elif 'Pep Talk' in name:
            self.color = (0, 255, 0)    # Green
            self.description = "Re-activates any towers disabled by Excuse Monsters"
            self.cooldown_time = 15000  # 15 seconds
        elif 'Water Break' in name:
            self.color = (0, 0, 255)    # Blue
            self.description = "Heals friendly units and clears debuffs"
            self.cooldown_time = 25000  # 25 seconds

    def activate(self, game):
        if self.active or game.gold < self.cost or self.cooldown > 0:
            return False
            
        self.active = True
        self.duration = 10000  # 10 seconds
        self.cooldown = self.cooldown_time
        game.gold -= self.cost
        
        # Apply power-up effects
        if 'Pre-Workout' in self.name:
            self._apply_pre_workout(game)
        elif 'Cheat Meal' in self.name:
            self._apply_cheat_meal(game)
        elif 'Pep Talk' in self.name:
            self._apply_pep_talk(game)
        elif 'Water Break' in self.name:
            self._apply_water_break(game)
            
        return True

    def update(self, game):
        if self.active:
            self.duration -= 16  # Assuming 60 FPS
            if self.duration <= 0:
                self.active = False
                self._remove_effects(game)
        
        if self.cooldown > 0:
            self.cooldown -= 16

    def _apply_pre_workout(self, game):
        for tower in game.towers:
            tower.fire_rate /= 2  # Double fire rate

    def _apply_cheat_meal(self, game):
        # Find center of screen
        center_x = game.game_width // 2
        center_y = game.height // 2
        
        # Damage all enemies in range
        for enemy in game.enemies[:]:
            distance = math.sqrt(
                (enemy.x - center_x)**2 + 
                (enemy.y - center_y)**2
            )
            if distance < 300:  # Explosion radius
                enemy.take_damage(200)
                enemy.reward = int(enemy.reward * 0.5)  # Reduce gold reward

    def _apply_pep_talk(self, game):
        # Re-enable all disabled towers
        for tower in game.towers:
            tower.disabled = False

    def _apply_water_break(self, game):
        # Heal all towers and clear debuffs
        for tower in game.towers:
            if hasattr(tower, 'health'):
                tower.health = tower.max_health

    def _remove_effects(self, game):
        if 'Pre-Workout' in self.name:
            for tower in game.towers:
                tower.fire_rate *= 2  # Restore normal fire rate

    def draw(self, screen, x, y):
        # Draw power-up button
        button_rect = pygame.Rect(x, y, 200, 50)  # Increased height
        color = self.color if self.cooldown == 0 else (100, 100, 100)
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 1)
        
        # Draw text
        font = pygame.font.Font(None, 24)
        key_text = font.render(f"[{self.key}]", True, (255, 255, 255))
        name_text = font.render(self.name, True, (255, 255, 255))
        cost_text = font.render(f"{self.cost} gold", True, (255, 215, 0))
        
        # Center text vertically
        total_height = key_text.get_height() + name_text.get_height() + cost_text.get_height()
        start_y = y + (50 - total_height) // 2
        
        screen.blit(key_text, (x + 5, start_y))
        screen.blit(name_text, (x + 5, start_y + key_text.get_height()))
        screen.blit(cost_text, (x + 5, start_y + key_text.get_height() + name_text.get_height()))
        
        # Draw cooldown bar if on cooldown
        if self.cooldown > 0:
            cooldown_width = 200 * (1 - self.cooldown / self.cooldown_time)
            pygame.draw.rect(screen, (100, 100, 100),
                           (x, y + 55, cooldown_width, 5))
            
            # Draw tooltip on hover
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):
                self.draw_tooltip(screen, mouse_pos)

    def draw_tooltip(self, screen, mouse_pos):
        # Create tooltip surface
        font = pygame.font.Font(None, 24)
        name_text = font.render(self.name, True, (255, 255, 255))
        desc_text = font.render(self.description, True, (200, 200, 200))
        cooldown_text = font.render(f"Cooldown: {self.cooldown_time/1000}s", True, (200, 200, 200))
        
        # Calculate tooltip size
        padding = 10
        width = max(name_text.get_width(), desc_text.get_width(), 
                   cooldown_text.get_width()) + padding * 2
        height = name_text.get_height() + desc_text.get_height() + \
                 cooldown_text.get_height() + padding * 4
        
        # Position tooltip
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        # Get screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Adjust position if tooltip would go off screen
        if tooltip_x + width > screen_width:
            tooltip_x = mouse_pos[0] - width - 20  # Show to the left of cursor
        if tooltip_y + height > screen_height:
            tooltip_y = screen_height - height - 10  # Show above cursor
        
        # Draw tooltip background
        tooltip_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surface, (0, 0, 0, 180), 
                        (0, 0, width, height))
        pygame.draw.rect(tooltip_surface, (255, 255, 255), 
                        (0, 0, width, height), 1)
        
        # Draw text
        y_offset = padding
        tooltip_surface.blit(name_text, (padding, y_offset))
        y_offset += name_text.get_height() + padding
        tooltip_surface.blit(desc_text, (padding, y_offset))
        y_offset += desc_text.get_height() + padding
        tooltip_surface.blit(cooldown_text, (padding, y_offset))
        
        # Draw tooltip
        screen.blit(tooltip_surface, (tooltip_x, tooltip_y)) 