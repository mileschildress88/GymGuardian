import pygame
import math
import random

class Projectile:
    def __init__(self, x, y, target, damage, tower_type, game, tower=None):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.target = target
        self.damage = damage
        self.tower_type = tower_type
        self.game = game
        self.tower = tower  # Reference to the tower that fired this projectile
        self.hit_target = False
        self.missed = False
        self.speed = 5
        self.radius = 5
        self.splash_radius = 50
        self.effects = {}
        
        # Set default color
        self.color = (255, 255, 255)  # White default
        
        # Special projectile behaviors based on tower descriptions
        if tower_type == 'treadmill':
            # "Slows enemies by 50% for 3 seconds"
            self.effects['slow'] = {'duration': 3000, 'amount': 0.5}
            self.color = (255, 0, 0)  # Red
        elif tower_type == 'protein':
            # "Splash damage and buffs nearby towers"
            self.splash_radius = 80
            self.color = (0, 255, 0)  # Green
        elif tower_type == 'yoga':
            # "High range, slows enemies by 30% for 2 seconds"
            self.effects['slow'] = {'duration': 2000, 'amount': 0.3}
            self.speed = 8
            self.color = (0, 0, 255)  # Blue
        elif tower_type == 'kettlebell':
            # "Area damage and knockback effect"
            self.splash_radius = 100
            self.color = (255, 165, 0)  # Orange
            self.knockback = 20  # Pixels to knock back enemies
        elif tower_type == 'hiit':
            # "Trainers can move and attack"
            self.speed = 6
            self.radius = 8  # Slightly larger to represent the trainer
            self.color = (255, 0, 255)  # Magenta
            self.punch_range = 20  # Close range for melee attacks
        elif tower_type == 'spin':
            # "Beam pierces through enemies"
            self.color = (0, 255, 255)  # Cyan
            self.laser_width = 4  # Increased from 2
            self.pierce = True  # Can hit multiple enemies
            self.laser_glow = True

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
        hit_enemies = []
        total_damage_dealt = 0
        enemies_killed = 0
        
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
                        applied_damage = self.damage * damage_multiplier
                        
                        # Record health before damage to check if enemy is killed
                        health_before = enemy.health
                        
                        enemy.take_damage(applied_damage)
                        
                        # Update statistics
                        total_damage_dealt += min(health_before, applied_damage)
                        if enemy.health <= 0 and health_before > 0:
                            enemies_killed += 1
                            
                        if self.effects:
                            enemy.apply_effects(self.effects)
                            
                        # Apply knockback for kettlebell
                        if self.tower_type == 'kettlebell':
                            # Calculate knockback direction (away from impact)
                            if distance > 0:  # Prevent division by zero
                                # Calculate unit vector away from impact
                                knock_dx = dx / distance
                                knock_dy = dy / distance
                                
                                # Move enemy away from impact point
                                knock_amount = self.knockback * (1 - distance / self.splash_radius)
                                enemy.x += knock_dx * knock_amount
                                enemy.y += knock_dy * knock_amount
                                
                        hit_enemies.append(enemy)
        elif self.tower_type == 'spin':
            # Laser pierces through enemies in a line
            # We'll hit all enemies in the same direction as the target
            direction_x = self.target.x - self.x
            direction_y = self.target.y - self.y
            direction_length = (direction_x ** 2 + direction_y ** 2) ** 0.5
            
            if direction_length > 0:  # Prevent division by zero
                # Normalize direction vector
                direction_x /= direction_length
                direction_y /= direction_length
                
                for enemy in self.game.enemies:
                    if enemy.is_alive():
                        # Check if enemy is roughly along the same line
                        enemy_dx = enemy.x - self.x
                        enemy_dy = enemy.y - self.y
                        enemy_dist = (enemy_dx ** 2 + enemy_dy ** 2) ** 0.5
                        
                        if enemy_dist <= 200:  # Within laser range
                            # Project enemy position onto laser line
                            dot_product = enemy_dx * direction_x + enemy_dy * direction_y
                            
                            # Calculate perpendicular distance to laser line
                            proj_x = dot_product * direction_x
                            proj_y = dot_product * direction_y
                            perp_dx = enemy_dx - proj_x
                            perp_dy = enemy_dy - proj_y
                            perp_dist = (perp_dx ** 2 + perp_dy ** 2) ** 0.5
                            
                            # If enemy is close to laser line and in front of tower
                            if perp_dist <= 10 and dot_product > 0:
                                # Record health before damage to check if enemy is killed
                                health_before = enemy.health
                                
                                enemy.take_damage(self.damage)
                                
                                # Update statistics
                                total_damage_dealt += min(health_before, self.damage)
                                if enemy.health <= 0 and health_before > 0:
                                    enemies_killed += 1
                                    
                                if self.effects:
                                    enemy.apply_effects(self.effects)
                                hit_enemies.append(enemy)
        else:
            # Single target damage
            # Record health before damage to check if enemy is killed
            health_before = self.target.health
            
            self.target.take_damage(self.damage)
            
            # Update statistics
            total_damage_dealt += min(health_before, self.damage)
            if self.target.health <= 0 and health_before > 0:
                enemies_killed += 1
                
            if self.effects:
                self.target.apply_effects(self.effects)
            hit_enemies.append(self.target)
        
        # Update tower statistics if tower reference exists
        if self.tower:
            self.tower.damage_dealt += total_damage_dealt
            self.tower.enemies_killed += enemies_killed
        
        self.hit_target = True
        return hit_enemies

    def handle_laser(self):
        if not self.target or not self.target.is_alive():
            self.missed = True
            return

        # For lasers, we'll handle the hit directly
        hit_enemies = self.handle_hit()
        if not hit_enemies:
            self.missed = True

    def draw(self, screen):
        if self.hit_target or self.missed:
            return

        if self.tower_type == 'spin':
            if self.target and self.target.is_alive():
                # Draw the main laser beam
                pygame.draw.line(screen, self.color, 
                               (self.x, self.y), 
                               (self.target.x, self.target.y), 
                               self.laser_width)
                
                # Add a glow effect by drawing additional thinner lines
                if hasattr(self, 'laser_glow') and self.laser_glow:
                    # Draw a wider, semi-transparent outer glow
                    pygame.draw.line(screen, (self.color[0], self.color[1], self.color[2], 128), 
                                   (self.x, self.y), 
                                   (self.target.x, self.target.y), 
                                   self.laser_width + 4)
                    
                    # Draw a brighter inner core
                    pygame.draw.line(screen, (255, 255, 255), 
                                   (self.x, self.y), 
                                   (self.target.x, self.target.y), 
                                   max(1, self.laser_width // 2))
                    
                    # Add impact point at the target
                    impact_radius = 6
                    pygame.draw.circle(screen, self.color, 
                                     (int(self.target.x), int(self.target.y)), 
                                     impact_radius)
                    pygame.draw.circle(screen, (255, 255, 255), 
                                     (int(self.target.x), int(self.target.y)), 
                                     max(1, impact_radius // 2))
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