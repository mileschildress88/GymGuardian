import pygame
import math
from .projectiles import Projectile

class Tower:
    def __init__(self, tower_type, x, y, grid_size=32):
        self.tower_type = tower_type
        self.x = x
        self.y = y
        self.grid_size = grid_size
        self.selected = False
        self.last_shot = 0
        self.can_shoot = True
        self.buffs = {}
        self.deactivated = False
        self.deactivation_timer = 0
        
        # Tower statistics tracking
        self.enemies_killed = 0
        self.damage_dealt = 0
        self.shots_fired = 0
        self.sell_button = None
        
        # Tower properties based on type
        if tower_type == 'treadmill':
            self.base_damage = 10
            self.base_range = 150
            self.base_fire_rate = 1000
            self.color = (100, 100, 255)
            self.projectile_type = 'sneaker'
        elif tower_type == 'protein':
            self.base_damage = 25
            self.base_range = 120
            self.base_fire_rate = 1500
            self.color = (255, 100, 100)
            self.projectile_type = 'shake'
        elif tower_type == 'yoga':
            self.base_damage = 40
            self.base_range = 250
            self.base_fire_rate = 2000
            self.color = (200, 200, 255)
            self.projectile_type = 'arrow'
        elif tower_type == 'kettlebell':
            self.base_damage = 35
            self.base_range = 100
            self.base_fire_rate = 2000
            self.color = (100, 100, 100)
            self.projectile_type = 'kettlebell'
        elif tower_type == 'hiit':
            self.base_damage = 15
            self.base_range = 80
            self.base_fire_rate = 500
            self.color = (255, 150, 0)
            self.projectile_type = 'trainer'
        elif tower_type == 'spin':
            self.base_damage = 8
            self.base_range = 200
            self.base_fire_rate = 300
            self.color = (255, 0, 255)
            self.projectile_type = 'laser'
        
        # Initialize current stats with base values
        self.damage = self.base_damage
        self.range = self.base_range
        self.fire_rate = self.base_fire_rate
        
        # Tower stats based on type
        self.stats = {
            'treadmill': {
                'cost': 100,
                'damage': 20,
                'range': 100,  # Adjusted ranges for new grid size
                'fire_rate': 1000,  # milliseconds
                'color': (255, 0, 0),
                'name': 'Treadmill Turret',
                'description': 'Shoots sneakers at enemies, slowing them down with cardio burn damage over time.',
                'special': 'Slows enemies by 50% for 3 seconds'
            },
            'protein': {
                'cost': 150,
                'damage': 40,
                'range': 75,  # Adjusted ranges for new grid size
                'fire_rate': 2000,
                'color': (0, 255, 0),
                'name': 'Protein Cannon',
                'description': 'Launches protein shakes that explode on impact, dealing splash damage.',
                'special': 'Splash damage and buffs nearby towers'
            },
            'yoga': {
                'cost': 200,
                'damage': 15,
                'range': 150,  # Adjusted ranges for new grid size
                'fire_rate': 1500,
                'color': (0, 0, 255),
                'name': 'Yoga Sniper',
                'description': 'Calming arrows reduce enemy speed and stress.',
                'special': 'High range, slows enemies by 30% for 2 seconds'
            },
            'kettlebell': {
                'cost': 175,
                'damage': 30,
                'range': 85,  # Adjusted ranges for new grid size
                'fire_rate': 1800,
                'color': (255, 165, 0),
                'name': 'Kettlebell Dropper',
                'description': 'Drops heavy kettlebells causing splash damage.',
                'special': 'Area damage and knockback effect'
            },
            'hiit': {
                'cost': 250,
                'damage': 25,
                'range': 60,  # Adjusted ranges for new grid size
                'fire_rate': 800,
                'color': (255, 0, 255),
                'name': 'HIIT Barracks',
                'description': 'Spawns trainers that chase and attack nearby enemies.',
                'special': 'Trainers can move and attack'
            },
            'spin': {
                'cost': 300,
                'damage': 35,
                'range': 120,  # Adjusted ranges for new grid size
                'fire_rate': 1200,
                'color': (0, 255, 255),
                'name': 'Spin Class Laser',
                'description': 'Fires energy beams that can hit multiple enemies.',
                'special': 'Beam pierces through enemies'
            }
        }
        
        # Special effects
        self.effects = {
            'treadmill': {'slow': 0.5, 'duration': 3000},
            'protein': {'splash': True, 'buff': True},
            'yoga': {'slow': 0.7, 'duration': 2000},
            'kettlebell': {'splash': True},
            'hiit': {'melee': True},
            'spin': {'beam': True}
        }

    def reset_stats(self):
        """Reset tower stats to base values"""
        self.damage = self.base_damage
        self.range = self.base_range
        self.fire_rate = self.base_fire_rate

    def update(self, enemies, current_time):
        if self.deactivated and current_time >= self.deactivation_timer:
            self.deactivated = False
            
        if self.deactivated:
            return
            
        closest_enemy = None
        min_distance = float('inf')
        center_x = self.x + self.grid_size // 2
        center_y = self.y + self.grid_size // 2
        
        for enemy in enemies:
            distance = math.sqrt((enemy.x - center_x)**2 + 
                               (enemy.y - center_y)**2)
            if distance < min_distance and distance <= self.range:
                min_distance = distance
                closest_enemy = enemy
        
        self.target = closest_enemy
        self.can_shoot = (current_time - self.last_shot >= self.fire_rate and 
                         self.target is not None)

    def shoot(self, game):
        if not self.can_shoot or not game.enemies:
            return None
            
        closest_enemy = None
        closest_distance = float('inf')
        center_x = self.x + self.grid_size // 2
        center_y = self.y + self.grid_size // 2
        
        for enemy in game.enemies:
            distance = math.sqrt((enemy.x - center_x)**2 + 
                               (enemy.y - center_y)**2)
            if distance < closest_distance and distance <= self.range:
                closest_distance = distance
                closest_enemy = enemy
        
        if closest_enemy:
            projectile = Projectile(
                center_x,
                center_y,
                closest_enemy,
                self.damage,
                self.tower_type,
                game,
                self  # Pass the tower reference to the projectile
            )
            self.last_shot = pygame.time.get_ticks()
            self.can_shoot = False
            self.shots_fired += 1
            return projectile
        
        return None

    def apply_buff(self, buff_type, multiplier, duration):
        current_time = pygame.time.get_ticks()
        self.buffs[buff_type] = {
            'multiplier': multiplier,
            'end_time': current_time + duration
        }
        self.update_stats()

    def update_buffs(self, current_time):
        # Remove expired buffs
        expired_buffs = []
        for buff_type, buff_data in self.buffs.items():
            if current_time >= buff_data['end_time']:
                expired_buffs.append(buff_type)
        
        for buff_type in expired_buffs:
            del self.buffs[buff_type]
        
        if expired_buffs:
            self.update_stats()

    def update_stats(self):
        # Reset to base stats
        self.damage = self.base_damage
        
        # Apply all active buffs
        for buff_data in self.buffs.values():
            self.damage *= buff_data['multiplier']

    def deactivate(self, duration=5000):  # 5 seconds deactivation by default
        self.deactivated = True
        self.deactivation_timer = pygame.time.get_ticks() + duration

    def draw(self, screen, images=None):
        # Draw the tower image if images dict is provided
        if images is not None and self.tower_type in images:
            screen.blit(images[self.tower_type], (self.x, self.y))
        else:
            # Fallback: draw a colored rectangle
            tower_rect = pygame.Rect(self.x, self.y, self.grid_size, self.grid_size)
            pygame.draw.rect(screen, self.color, tower_rect)
        
        # Draw selection highlight and range indicator
        if self.selected:
            highlight_rect = pygame.Rect(self.x, self.y, self.grid_size, self.grid_size)
            pygame.draw.rect(screen, (255, 255, 255), highlight_rect, 2)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (self.x + self.grid_size//2, self.y + self.grid_size//2), 
                             self.range, 1)

    def upgrade(self):
        self.damage *= 1.5
        self.range *= 1.1
        self.fire_rate = max(100, self.fire_rate * 0.9)

    def is_hovered(self, mouse_pos):
        distance = ((mouse_pos[0] - self.x)**2 + 
                   (mouse_pos[1] - self.y)**2)**0.5
        return distance <= 20

    def draw_tooltip(self, screen, mouse_pos):
        if not self.is_hovered(mouse_pos):
            return
            
        # Create tooltip surface
        font = pygame.font.Font(None, 24)
        name_text = font.render(self.name, True, (255, 255, 255))
        desc_text = font.render(self.description, True, (200, 200, 200))
        stats_text = font.render(f"Damage: {self.damage} | Range: {self.range}", True, (200, 200, 200))
        special_text = font.render(self.special, True, (255, 215, 0))
        
        # Calculate tooltip size
        padding = 10
        width = max(name_text.get_width(), desc_text.get_width(), 
                   stats_text.get_width(), special_text.get_width()) + padding * 2
        height = name_text.get_height() + desc_text.get_height() + \
                 stats_text.get_height() + special_text.get_height() + padding * 5
        
        # Position tooltip
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
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
        tooltip_surface.blit(stats_text, (padding, y_offset))
        y_offset += stats_text.get_height() + padding
        tooltip_surface.blit(special_text, (padding, y_offset))
        
        # Draw tooltip
        screen.blit(tooltip_surface, (tooltip_x, tooltip_y)) 