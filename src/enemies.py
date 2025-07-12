import pygame
import math
import random

class Enemy:
    def __init__(self, x, y, path_points, enemy_type='normal', game=None):
        self.x = float(x)
        self.y = float(y)
        self.path_points = path_points
        self.current_point = 0
        self.enemy_type = enemy_type
        self.effects = {}
        self.reached_end = False
        self.game = game
        
        # Set properties based on enemy type
        if enemy_type == 'normal':
            self.speed = 2.0
            self.base_speed = 2.0
            self.health = 100
            self.max_health = 100
            self.radius = 12
            self.color = (200, 50, 50)
            self.reward = 20
        elif enemy_type == 'fast':
            self.speed = 3.5
            self.base_speed = 3.5
            self.health = 60
            self.max_health = 60
            self.radius = 10
            self.color = (255, 150, 0)
            self.reward = 25
        elif enemy_type == 'tank':
            self.speed = 1.0
            self.base_speed = 1.0
            self.health = 200
            self.max_health = 200
            self.radius = 15
            self.color = (100, 100, 200)
            self.reward = 35
        elif enemy_type == 'boss':
            self.speed = 0.8
            self.base_speed = 0.8
            self.health = 500
            self.max_health = 500
            self.radius = 20
            self.color = (150, 0, 150)
            self.reward = 100
    
    def is_alive(self):
        return self.health > 0 and not self.reached_end
        
    def update(self):
        # Update effects
        current_time = pygame.time.get_ticks()
        
        # Check for expired effects
        expired_effects = []
        for effect_type, effect_data in self.effects.items():
            if current_time >= effect_data.get('end_time', 0):
                expired_effects.append(effect_type)
                
        # Remove expired effects
        for effect_type in expired_effects:
            if effect_type == 'slow':
                self.speed = self.base_speed  # Reset speed
            del self.effects[effect_type]
            
        if not self.path_points or self.current_point >= len(self.path_points) - 1:
            self.reached_end = True
            return
            
        # Get target point
        target_x, target_y = self.path_points[self.current_point + 1]
        
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < self.speed:
            # Reached current target point, move to next one
            self.x = float(target_x)
            self.y = float(target_y)
            self.current_point += 1
        else:
            # Move towards target point
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def draw(self, screen, images=None):
        # Draw enemy image if images dict is provided
        if images is not None and f"{self.enemy_type}_enemy" in images:
            enemy_img = images[f"{self.enemy_type}_enemy"]
            img_rect = enemy_img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(enemy_img, img_rect)
        else:
            # Fallback: draw a colored circle
            pygame.draw.circle(screen, (200, 0, 0), (int(self.x), int(self.y)), self.radius)
        
        # Draw health bar
        health_bar_length = 30
        health_ratio = self.health / self.max_health
        
        pygame.draw.rect(screen, (200, 0, 0),
                        (self.x - health_bar_length/2,
                         self.y - self.radius - 10,
                         health_bar_length, 5))
        
        pygame.draw.rect(screen, (0, 200, 0),
                        (self.x - health_bar_length/2,
                         self.y - self.radius - 10,
                         health_bar_length * health_ratio, 5))
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return True
        return False
        
    def apply_effects(self, effects):
        current_time = pygame.time.get_ticks()
        
        # Apply slow effect
        if 'slow' in effects:
            slow_data = effects['slow']
            self.effects['slow'] = {
                'amount': slow_data['amount'],
                'end_time': current_time + slow_data['duration']
            }
            # Apply the slow effect immediately
            self.speed = self.base_speed * (1 - slow_data['amount']) 