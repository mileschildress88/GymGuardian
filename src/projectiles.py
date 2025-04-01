import pygame
import math
import random

class Projectile:
    def __init__(self, x, y, target, damage, tower_type, game):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.target = target
        self.damage = damage
        self.tower_type = tower_type
        self.game = game
        self.hit_target = False
        self.missed = False
        self.speed = 5
        self.radius = 5
        self.splash_radius = 50
        self.effects = {}
        
        # Set default color
        self.color = (255, 255, 255)  # White default
        
        # Special projectile behaviors
        if tower_type == 'treadmill':
            self.effects['slow'] = {'duration': 3000, 'amount': 0.3}
            self.color = (255, 0, 0)  # Red
        elif tower_type == 'protein':
            self.splash_radius = 80
            self.color = (0, 255, 0)  # Green
        elif tower_type == 'yoga':
            self.effects['slow'] = {'duration': 2000, 'amount': 0.3}
            self.speed = 8
            self.color = (0, 0, 255)  # Blue
        elif tower_type == 'kettlebell':
            self.splash_radius = 100
            self.color = (255, 165, 0)  # Orange
        elif tower_type == 'hiit':
            self.speed = 6
            self.radius = 8  # Slightly larger to represent the trainer
            self.color = (255, 0, 255)  # Magenta
            self.punch_range = 20  # Close range for melee attacks
        elif tower_type == 'spin':
            self.color = (0, 255, 255)  # Cyan
            self.laser_width = 2

    def update(self):
        if self.hit_target or self.missed:
            return

        if self.tower_type == 'spin':
            self.handle_laser()
            return

        if not self.target or not self.target.is_alive():
            self.missed = True
            return

        # Calculate direction to target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if self.tower_type == 'hiit':
            # HIIT trainers use melee range
            if distance <= self.punch_range:
                # Deal damage without knockback
                self.target.take_damage(self.damage)
                self.hit_target = True
            else:
                # Move towards target
                if distance > 0:
                    self.x += (dx / distance) * self.speed
                    self.y += (dy / distance) * self.speed
                    
                # Check if trainer has gone too far from start position
                distance_from_start = ((self.x - self.start_x) ** 2 + (self.y - self.start_y) ** 2) ** 0.5
                if distance_from_start > 200:  # Maximum chase range
                    self.missed = True
            return

        # For other projectiles
        if distance <= self.radius + self.target.radius:
            self.handle_hit()
        else:
            # Move projectile towards target
            if distance > 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed

    def handle_hit(self):
        if self.tower_type == 'protein' or self.tower_type == 'kettlebell':
            # Handle splash damage
            for enemy in self.game.enemies:
                if enemy.is_alive():
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    if distance <= self.splash_radius:
                        # Calculate damage falloff based on distance
                        damage_multiplier = 1 - (distance / self.splash_radius)
                        enemy.take_damage(self.damage * damage_multiplier)
                        if self.effects:
                            enemy.apply_effects(self.effects)
        else:
            # Single target damage
            self.target.take_damage(self.damage)
            if self.effects:
                self.target.apply_effects(self.effects)
        
        self.hit_target = True

    def handle_laser(self):
        if not self.target or not self.target.is_alive():
            self.missed = True
            return

        # Calculate direction to target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance <= self.game.towers[0].stats['spin']['range']:
            self.target.take_damage(self.damage)
            if self.effects:
                self.target.apply_effects(self.effects)
        else:
            self.missed = True

    def draw(self, screen):
        if self.hit_target or self.missed:
            return

        if self.tower_type == 'spin':
            if self.target and self.target.is_alive():
                pygame.draw.line(screen, self.color, 
                               (self.x, self.y), 
                               (self.target.x, self.target.y), 
                               self.laser_width)
        elif self.tower_type == 'hiit':
            # Draw HIIT trainer as a small person (magenta body, pink head)
            pygame.draw.rect(screen, self.color, 
                           (self.x - 4, self.y - 6, 8, 12))  # Body
            pygame.draw.circle(screen, (255, 192, 203), 
                             (int(self.x), int(self.y - 8)), 4)  # Head
        else:
            pygame.draw.circle(screen, self.color, 
                             (int(self.x), int(self.y)), 
                             self.radius) 