import pygame
import math

class Enemy:
    def __init__(self, x, y, path_points):
        self.x = x
        self.y = y
        self.path_points = path_points
        self.current_point = 0
        self.speed = 2
        self.health = 100
        self.max_health = 100
        self.radius = 15
        self.color = (200, 50, 50)
        self.reached_end = False
        
    def move(self):
        if self.current_point >= len(self.path_points) - 1:
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
            self.x = target_x
            self.y = target_y
            self.current_point += 1
        else:
            # Move towards target point
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def draw(self, screen):
        # Draw enemy body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw health bar
        health_bar_length = 30
        health_bar_height = 5
        health_ratio = self.health / self.max_health
        
        # Background (red)
        pygame.draw.rect(screen, (200, 0, 0),
                        (self.x - health_bar_length/2,
                         self.y - self.radius - 10,
                         health_bar_length,
                         health_bar_height))
        
        # Foreground (green)
        pygame.draw.rect(screen, (0, 200, 0),
                        (self.x - health_bar_length/2,
                         self.y - self.radius - 10,
                         health_bar_length * health_ratio,
                         health_bar_height))
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return True
        return False 