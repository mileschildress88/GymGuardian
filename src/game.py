import pygame
import math
import random
from .towers import Tower
from .enemies import Enemy
from .powerups import PowerUp
from .menu import Menu
from .map_selector import MapSelector

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Game state
        self.game_state = "home"  # home, map_select, playing, game_over
        self.menu = Menu(screen)
        self.map_selector = MapSelector(screen)
        
        # Game objects
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.powerups = []
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.tower_buttons = []  # Initialize tower buttons list
        
        # Tooltip variables
        self.show_tooltip = False
        self.tooltip_text = ""
        self.tooltip_position = (0, 0)
        
        # Define game area and UI area
        self.ui_width = 250  # Width of the UI sidebar
        self.game_width = self.width - self.ui_width  # Width of the actual game area
        
        # Grid will be initialized when map is selected
        self.grid_size = None
        self.grid_width = None
        self.grid_height = None
        self.grid = None
        
        # Map path (will be set when map is selected)
        self.path = None
        self.path_points = []
        self.path_segments = []
        
        # Selected tower type
        self.selected_tower = None
        self.selected_placed_tower = None
        
        # Wave management
        self.wave_in_progress = False
        self.spawn_timer = 0
        self.spawn_delay = 2000
        self.enemies_spawned = 0
        self.enemies_per_wave = 5  # Base number of enemies per wave
        self.current_wave_enemies = 0  # Track enemies for current wave
        self.total_enemies_this_wave = 0  # Total enemies for current wave
        
        # Game stats
        self.gold = 650  # Increased starting gold
        self.lives = 10
        self.wave = 1
        self.game_over = False
        self.paused = False
        self.last_spawn = 0
        self.spawning = True

        # Initialize tower types with descriptions
        self.tower_types = {
            'treadmill': {
                'name': 'Treadmill', 
                'cost': 150, 
                'color': (100, 100, 100),
                'description': 'Shoots projectiles that slow enemies down\nDamage: 10\nRange: 150\nFire Rate: 1.0s'
            },
            'protein': {
                'name': 'Protein Shaker', 
                'cost': 250, 
                'color': (200, 100, 100),
                'description': 'Launches protein shakes with splash damage\nDamage: 25\nRange: 120\nFire Rate: 1.5s'
            },
            'yoga': {
                'name': 'Yoga Mat', 
                'cost': 300, 
                'color': (100, 200, 100),
                'description': 'Long-range tower that slows enemies\nDamage: 40\nRange: 250\nFire Rate: 2.0s'
            },
            'kettlebell': {
                'name': 'Kettlebell', 
                'cost': 350, 
                'color': (150, 150, 150),
                'description': 'Drops heavy weights with splash damage\nDamage: 35\nRange: 100\nFire Rate: 2.0s'
            },
            'hiit': {
                'name': 'HIIT Station', 
                'cost': 450, 
                'color': (200, 50, 50),
                'description': 'Spawns trainers that chase enemies\nDamage: 15\nRange: 80\nFire Rate: 0.5s'
            },
            'spin': {
                'name': 'Spin Bike', 
                'cost': 800, 
                'color': (100, 100, 200),
                'description': 'Fires laser beams that pierce enemies\nDamage: 8\nRange: 200\nFire Rate: 0.3s'
            }
        }
        
        # Create tower buttons
        self.create_tower_buttons()

    def create_tower_buttons(self):
        # Calculate button dimensions
        button_width = self.ui_width - 20  # 10px padding on each side
        button_height = 50  # Taller buttons to fit icon and text
        button_spacing = 5  # Space between buttons
        
        # Track vertical position for button placement
        tower_y = 160  # Start below wave control button
        
        # Create buttons for each tower type
        for tower_type, tower_info in self.tower_types.items():
            button = pygame.Rect(
                self.game_width + 10,  # 10px padding from left
                tower_y,
                button_width,
                button_height
            )
            
            self.tower_buttons.append({
                'rect': button,
                'type': tower_type,
                'name': tower_info['name'],
                'cost': tower_info['cost']
            })
            
            # Move down for next button
            tower_y += button_height + button_spacing

    def initialize_game(self, selected_path):
        print(f"Initializing game with path of length {len(selected_path)}")
        
        # Store the grid-based path
        self.path = selected_path
        
        # Calculate map dimensions
        max_x = max(x for x, y in selected_path) + 1
        max_y = max(y for x, y in selected_path) + 1
        min_x = min(x for x, y in selected_path)
        min_y = min(y for x, y in selected_path)
        
        # Calculate grid size to fit the map
        width_grid_size = self.game_width // max_x
        height_grid_size = self.height // max_y
        self.grid_size = min(width_grid_size, height_grid_size)  # Use smaller size to ensure fit
        
        # Update grid dimensions
        self.grid_width = self.game_width // self.grid_size
        self.grid_height = self.height // self.grid_size
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Convert grid coordinates to pixel coordinates for path points
        self.path_points = []
        for x, y in selected_path:
            # Convert grid coordinates to pixel coordinates
            pixel_x = int(x * self.grid_size + self.grid_size // 2)
            pixel_y = int(y * self.grid_size + self.grid_size // 2)
            self.path_points.append((pixel_x, pixel_y))
            print(f"Added path point: ({pixel_x}, {pixel_y})")
        
        # Create path segments for drawing
        self.path_segments = list(zip(self.path_points[:-1], self.path_points[1:]))
        print(f"Created {len(self.path_segments)} path segments")
        
        # Reset game state
        self.reset_game()

    def draw_path(self):
        # Draw the path with a gradient effect
        for i in range(len(self.path) - 1):
            start_x, start_y = self.path[i]
            end_x, end_y = self.path[i + 1]
            
            # Calculate progress through the path for gradient
            progress = i / (len(self.path) - 1)
            # Gradient from dark to light gray
            color = (
                int(60 + progress * 40),
                int(60 + progress * 40),
                int(80 + progress * 40)
            )
            
            # Draw path segment
            pygame.draw.rect(self.screen, color,
                           (start_x * self.grid_size,
                            start_y * self.grid_size,
                            self.grid_size,
                            self.grid_size))
            
        # Draw end marker (black tile)
        end_x, end_y = self.path[-1]
        pygame.draw.rect(self.screen, (0, 0, 0),
                           (end_x * self.grid_size,
                            end_y * self.grid_size,
                            self.grid_size,
                            self.grid_size))

    def draw_ui(self):
        # Draw sidebar background
        pygame.draw.rect(self.screen, (40, 40, 40), 
                        (self.game_width, 0, self.ui_width, self.height))
        
        # Draw stats panel
        stats_y = 10
        pygame.draw.rect(self.screen, (60, 60, 60),
                        (self.game_width + 10, stats_y, 260, 100))
        
        # Draw gold and lives
        gold_text = self.font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        lives_text = self.font.render(f"Lives: {self.lives}", True, (255, 0, 0))
        wave_text = self.font.render(f"Wave: {self.wave}", True, (255, 255, 255))
        
        self.screen.blit(gold_text, (self.game_width + 20, stats_y + 10))
        self.screen.blit(lives_text, (self.game_width + 20, stats_y + 40))
        self.screen.blit(wave_text, (self.game_width + 20, stats_y + 70))
        
        # Draw wave control button
        wave_button = pygame.Rect(self.game_width + 10, 110, self.ui_width - 20, 40)
        button_color = (100, 100, 100) if self.wave_in_progress else (70, 70, 70)
        pygame.draw.rect(self.screen, button_color, wave_button)
        pygame.draw.rect(self.screen, (255, 255, 255), wave_button, 1)
        
        if self.wave_in_progress:
            # Show wave progress
            wave_text = self.font_small.render(
                f"Wave {self.wave} in Progress",
                True, (200, 200, 200)
            )
            progress = f"Spawned: {self.enemies_spawned}/{self.total_enemies_this_wave} Alive: {len(self.enemies)}"
            progress_text = self.font_small.render(progress, True, (200, 200, 200))
            self.screen.blit(wave_text, (wave_button.x + 5, wave_button.y + 5))
            self.screen.blit(progress_text, (wave_button.x + 5, wave_button.y + 20))
        else:
            # Show next wave button
            wave_text = self.font_small.render(
                f"Start Wave {self.wave} (SPACE)",
                True, (255, 255, 255)
            )
            self.screen.blit(wave_text, (wave_button.x + 5, wave_button.y + 10))
        
        # If a tower is selected, show tower details panel instead of tower buttons
        if self.selected_placed_tower:
            self.draw_tower_details()
        else:
            # Draw tower buttons
            for button in self.tower_buttons:
                # Draw button background
                color = (60, 60, 60)
                if button['type'] == self.selected_tower:
                    color = (80, 80, 80)
                elif self.gold < button['cost']:
                    color = (40, 40, 40)
                pygame.draw.rect(self.screen, color, button['rect'])
                pygame.draw.rect(self.screen, (255, 255, 255), button['rect'], 1)
                
                # Draw tower name and cost (align left)
                name_text = self.font_small.render(button['name'], True, (255, 255, 255))
                cost_text = self.font_small.render(f"{button['cost']} gold", True, (255, 215, 0))
                
                self.screen.blit(name_text, (button['rect'].x + 10, button['rect'].y + 5))
                self.screen.blit(cost_text, (button['rect'].x + 10, button['rect'].y + 25))
                
                # Draw tower icon on the right side of the button (using Tower class drawing)
                icon_size = 32  # Size of the icon
                icon_x = button['rect'].right - icon_size - 5  # 5px padding from right
                icon_y = button['rect'].y + (button['rect'].height - icon_size) // 2  # Center vertically
                
                # Create temporary Tower object to draw the icon
                temp_tower = Tower(button['type'], icon_x, icon_y, icon_size)
                temp_tower.draw(self.screen)
        
        # Draw tooltip if needed
        self.draw_tooltip()

    def draw_tower_details(self):
        # Get the selected tower
        tower = self.selected_placed_tower
        
        # Start position for tower details panel
        panel_y = 160
        panel_height = 300
        
        # Draw panel background
        pygame.draw.rect(self.screen, (50, 50, 50),
                      (self.game_width + 10, panel_y, self.ui_width - 20, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 100),
                      (self.game_width + 10, panel_y, self.ui_width - 20, panel_height), 1)
        
        # Draw tower name header
        tower_name = self.tower_types[tower.tower_type]['name']
        name_text = self.font.render(tower_name, True, (255, 255, 255))
        self.screen.blit(name_text, (self.game_width + 20, panel_y + 10))
        
        # Draw tower icon
        icon_size = 64  # Larger icon for details view
        icon_x = self.game_width + (self.ui_width - icon_size) // 2
        icon_y = panel_y + 50
        
        # Use a temporary tower object for drawing
        temp_tower = Tower(tower.tower_type, icon_x, icon_y, icon_size)
        temp_tower.draw(self.screen)
        
        # Draw tower stats
        stats_y = panel_y + 130
        line_height = 25
        
        # Tower level/tier
        level_text = self.font_small.render(f"Level: 1", True, (255, 255, 255))
        self.screen.blit(level_text, (self.game_width + 20, stats_y))
        
        # Enemies killed
        killed_text = self.font_small.render(f"Enemies killed: {tower.enemies_killed}", True, (255, 255, 255))
        self.screen.blit(killed_text, (self.game_width + 20, stats_y + line_height))
        
        # Damage dealt
        damage_text = self.font_small.render(f"Damage dealt: {tower.damage_dealt}", True, (255, 255, 255))
        self.screen.blit(damage_text, (self.game_width + 20, stats_y + line_height * 2))
        
        # Tower damage stats
        damage_stat = self.font_small.render(f"Damage: {tower.damage}", True, (255, 200, 200))
        self.screen.blit(damage_stat, (self.game_width + 20, stats_y + line_height * 3))
        
        # Tower range
        range_stat = self.font_small.render(f"Range: {tower.range}", True, (200, 200, 255))
        self.screen.blit(range_stat, (self.game_width + 20, stats_y + line_height * 4))
        
        # Tower fire rate
        fire_rate = 1000 / tower.fire_rate if tower.fire_rate > 0 else 0
        fire_stat = self.font_small.render(f"Fire rate: {fire_rate:.1f}/s", True, (200, 255, 200))
        self.screen.blit(fire_stat, (self.game_width + 20, stats_y + line_height * 5))
        
        # Draw sell button
        sell_button_y = panel_y + panel_height - 40
        sell_button = pygame.Rect(
            self.game_width + 20,
            sell_button_y,
            self.ui_width - 40,
            30
        )
        pygame.draw.rect(self.screen, (150, 50, 50), sell_button)
        pygame.draw.rect(self.screen, (255, 255, 255), sell_button, 1)
        
        # Calculate sell value (50% of original cost)
        tower_cost = self.tower_types[tower.tower_type]['cost']
        sell_value = int(tower_cost * 0.5)
        
        sell_text = self.font_small.render(f"Sell for {sell_value} gold", True, (255, 255, 255))
        sell_text_rect = sell_text.get_rect(center=sell_button.center)
        self.screen.blit(sell_text, sell_text_rect)
        
        # Store the sell button in the tower for click detection
        tower.sell_button = sell_button

    def draw(self):
        # Fill background with dark color
        self.screen.fill((20, 20, 20))
        
        if self.game_state == "home":
            self.menu.draw(self.screen, "home")
        elif self.game_state == "map_select":
            self.map_selector.draw(self.screen)
        elif self.game_state == "playing":
            # Draw game area background
            pygame.draw.rect(self.screen, (40, 40, 40), 
                           (0, 0, self.game_width, self.height))
            
            # Draw grid
            for x in range(0, self.game_width, self.grid_size):
                for y in range(0, self.height, self.grid_size):
                    rect = pygame.Rect(x, y, self.grid_size, self.grid_size)
                    pygame.draw.rect(self.screen, (0, 40, 0), rect)  # Dark green for placeable areas
                    pygame.draw.rect(self.screen, (40, 40, 40), rect, 1)  # Grid lines
            
            # Draw path if it exists
            if self.path:
                self.draw_path()
            
            # Draw game objects
            for tower in self.towers:
                tower.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            for projectile in self.projectiles:
                projectile.draw(self.screen)
            
            # Draw UI
            self.draw_ui()
        elif self.game_state == "game_over":
            # Draw the game state behind the game over screen
            # Draw game area background
            pygame.draw.rect(self.screen, (40, 40, 40), 
                           (0, 0, self.game_width, self.height))
            
            # Draw grid
            for x in range(0, self.game_width, self.grid_size):
                for y in range(0, self.height, self.grid_size):
                    rect = pygame.Rect(x, y, self.grid_size, self.grid_size)
                    pygame.draw.rect(self.screen, (0, 40, 0), rect)  # Dark green for placeable areas
                    pygame.draw.rect(self.screen, (40, 40, 40), rect, 1)  # Grid lines
            
            # Draw path if it exists
            if self.path:
                self.draw_path()
            
            # Draw game objects
            for tower in self.towers:
                tower.draw(self.screen)
            
            # Draw game over screen
            self.menu.draw(self.screen, "game_over")
        
        # Update display
        pygame.display.flip()

    def reset_game(self):
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.gold = 650  # Increased starting gold
        self.lives = 10
        self.wave = 1
        self.game_over = False
        self.paused = False
        self.wave_in_progress = False
        self.spawn_timer = 0
        self.selected_tower = None
        self.selected_placed_tower = None
        self.last_spawn = 0
        self.enemies_spawned = 0
        self.spawning = True
        self.active_power_ups = {}
        
        # Spawn pattern variables
        self.spawn_pattern = "normal"  # normal, cluster, rush
        self.next_spawn_delay = 2000   # milliseconds
        self.cluster_size = 0
        self.current_cluster = 0
        
        # Reset grid
        self.grid = [[0 for _ in range(self.grid_width)] 
                    for _ in range(self.grid_height)]
        
        # Mark path tiles as occupied
        if self.path:  # Only mark path if it exists
            for x, y in self.path:
                if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                    self.grid[y][x] = 2  # 2 represents path
                    
    def get_spawn_delay(self):
        """Calculate a variable spawn delay based on wave and spawn pattern"""
        if self.spawn_pattern == "normal":
            # Normal pattern: consistent timing with slight variation
            base_delay = max(2000 - (self.wave * 100), 1000)  # Decreases with wave number
            return base_delay + random.randint(-200, 200)  # Small randomness
            
        elif self.spawn_pattern == "cluster":
            # Cluster pattern: quick bursts with pauses between
            if self.current_cluster < self.cluster_size:
                self.current_cluster += 1
                return random.randint(200, 400)  # Very quick spawn within cluster
            else:
                self.current_cluster = 0
                return random.randint(2500, 3500)  # Longer pause between clusters
                
        elif self.spawn_pattern == "rush":
            # Rush pattern: very quick spawns
            return random.randint(300, 700)
            
        return 2000  # Default fallback
    
    def update_spawn_pattern(self):
        """Determine spawn pattern for next set of enemies"""
        # Set cluster size based on wave
        self.cluster_size = min(2 + self.wave // 2, 5)  # 2-5 enemies per cluster
        
        # Randomize spawn pattern with increasing probability of special patterns
        pattern_roll = random.random()
        
        if self.wave <= 2:
            # Waves 1-2: always normal
            self.spawn_pattern = "normal"
        elif self.wave <= 5:
            # Waves 3-5: 70% normal, 30% cluster
            if pattern_roll < 0.7:
                self.spawn_pattern = "normal"
            else:
                self.spawn_pattern = "cluster"
        else:
            # Waves 6+: 50% normal, 40% cluster, 10% rush
            if pattern_roll < 0.5:
                self.spawn_pattern = "normal"
            elif pattern_roll < 0.9:
                self.spawn_pattern = "cluster"
            else:
                self.spawn_pattern = "rush"
                
        print(f"Wave {self.wave} using {self.spawn_pattern} spawn pattern")

    def spawn_enemy(self):
        if not self.path_points:  # Safety check
            print("Warning: No path points available for enemy spawning")
            return
            
        # Get starting position from first path point
        start_x, start_y = self.path_points[0]
        
        # Determine enemy type based on wave and spawn count
        enemy_type = 'normal'
        if self.wave >= 3:
            if self.enemies_spawned == self.total_enemies_this_wave - 1:  # Last enemy of wave 3+ is a boss
                enemy_type = 'boss'
            elif self.wave >= 5 and self.enemies_spawned % 5 == 0:  # Every 5th enemy in wave 5+ is a tank
                enemy_type = 'tank'
            elif self.enemies_spawned % 3 == 0:  # Every 3rd enemy in wave 3+ is fast
                enemy_type = 'fast'
        
        # Create new enemy with proper path points and type
        enemy = Enemy(start_x, start_y, self.path_points, enemy_type)
        self.enemies.append(enemy)
        self.enemies_spawned += 1
        print(f"Spawning {enemy_type} enemy at ({start_x}, {start_y})")
        print(f"Spawned enemy {self.enemies_spawned}/{self.total_enemies_this_wave}")

    def update(self):
        if self.game_state != "playing":
            return
            
        current_time = pygame.time.get_ticks()
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.health <= 0:
                self.gold += enemy.reward
                self.enemies.remove(enemy)
                print(f"Enemy killed. Remaining: {len(self.enemies)}/{self.current_wave_enemies}")
            elif enemy.reached_end:
                self.lives -= 1
                self.enemies.remove(enemy)
                print(f"Enemy reached end. Lives: {self.lives}")
                if self.lives <= 0:
                    self.game_over = True
                    self.game_state = "game_over"  # Change game state to game_over
                    print("Game Over!")
        
        # Update towers
        for tower in self.towers:
            tower.update(self.enemies, current_time)
            if tower.can_shoot:
                projectile = tower.shoot(self)
                if projectile:
                    self.projectiles.append(projectile)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if projectile.hit_target or projectile.missed:
                self.projectiles.remove(projectile)
        
        # Update wave spawning
        if self.wave_in_progress:
            if self.enemies_spawned < self.total_enemies_this_wave:
                if self.enemies_spawned == 0:
                    # First enemy spawn - set pattern for this wave
                    self.update_spawn_pattern()
                    self.spawn_enemy()
                    self.spawn_timer = current_time
                    self.next_spawn_delay = self.get_spawn_delay()
                elif current_time - self.spawn_timer >= self.next_spawn_delay:
                    self.spawn_enemy()
                    self.spawn_timer = current_time
                    self.next_spawn_delay = self.get_spawn_delay()
            elif len(self.enemies) == 0:
                self.wave_in_progress = False
                self.wave += 1
                print(f"Wave {self.wave-1} completed!")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.game_state == "home":
                    action = self.menu.handle_click(event.pos, "home")
                    if action == "start":
                        self.game_state = "map_select"
                    elif action == "quit":
                        return "quit"
                elif self.game_state == "map_select":
                    selected_path = self.map_selector.handle_click(event.pos)
                    if selected_path:
                        self.initialize_game(selected_path)  # Initialize game with selected path
                        self.game_state = "playing"
                elif self.game_state == "game_over":
                    action = self.menu.handle_click(event.pos, "game_over")
                    if action == "retry":
                        # Reset the game with the same map
                        self.reset_game()
                        self.game_state = "playing"
                    elif action == "change_map":
                        # Go back to map selection
                        self.game_state = "map_select"
                    elif action == "exit":
                        # Return to main menu
                        self.game_state = "home"
                elif self.game_state == "playing":
                    # Check if click is in game area
                    if event.pos[0] < self.game_width:
                        # Check if sell button is clicked when a tower is selected
                        if self.selected_placed_tower and hasattr(self.selected_placed_tower, 'sell_button') and self.selected_placed_tower.sell_button.collidepoint(event.pos):
                            self.sell_tower(self.selected_placed_tower)
                            return
                            
                        # Default to deselecting current tower
                        if self.selected_placed_tower:
                            self.selected_placed_tower.selected = False
                            self.selected_placed_tower = None
                            
                        # Handle tower placement
                        if self.selected_tower:
                            grid_x = event.pos[0] // self.grid_size
                            grid_y = event.pos[1] // self.grid_size
                            
                            if (0 <= grid_x < self.grid_width and 
                                0 <= grid_y < self.grid_height and 
                                self.grid[grid_y][grid_x] == 0):
                                
                                # Find tower cost
                                tower_cost = next(button['cost'] for button in self.tower_buttons 
                                                if button['type'] == self.selected_tower)
                                
                                if self.gold >= tower_cost:
                                    tower = Tower(self.selected_tower, grid_x * self.grid_size, 
                                                grid_y * self.grid_size, self.grid_size)
                                    self.towers.append(tower)
                                    self.grid[grid_y][grid_x] = 1
                                    self.gold -= tower_cost
                                    self.selected_tower = None
                        else:
                            # Handle tower selection
                            tower_clicked = False
                            for tower in self.towers:
                                tower_center_x = tower.x + self.grid_size // 2
                                tower_center_y = tower.y + self.grid_size // 2
                                distance = ((event.pos[0] - tower_center_x)**2 + 
                                         (event.pos[1] - tower_center_y)**2)**0.5
                                
                                if distance <= self.grid_size // 2:
                                    # Deselect previous tower if there was one
                                    if self.selected_placed_tower:
                                        self.selected_placed_tower.selected = False
                                    
                                    tower.selected = True
                                    self.selected_placed_tower = tower
                                    tower_clicked = True
                                    break
                            
                            # If no tower was clicked, the first deselection at the start will handle this
                    else:
                        # Check if we need to handle sell button click
                        if self.selected_placed_tower and hasattr(self.selected_placed_tower, 'sell_button') and self.selected_placed_tower.sell_button.collidepoint(event.pos):
                            self.sell_tower(self.selected_placed_tower)
                            return
                            
                        # Check tower button clicks - only if no tower is selected
                        if not self.selected_placed_tower:
                            for button in self.tower_buttons:
                                if button['rect'].collidepoint(event.pos):
                                    # Deselect any currently selected tower
                                    if self.selected_placed_tower:
                                        self.selected_placed_tower.selected = False
                                        self.selected_placed_tower = None
                                        
                                    self.selected_tower = button['type']
                                    # Deselect all towers
                                    for tower in self.towers:
                                        tower.selected = False
                                    break
                        
                        # Check wave button click - always available
                        wave_button = pygame.Rect(self.game_width + 10, 110, self.ui_width - 20, 40)
                        if wave_button.collidepoint(event.pos) and not self.wave_in_progress:
                            self.wave_in_progress = True
                            self.spawn_timer = pygame.time.get_ticks()
                            self.enemies_spawned = 0
                            self.total_enemies_this_wave = self.wave * self.enemies_per_wave
                            print(f"Starting wave {self.wave} with {self.total_enemies_this_wave} enemies")
            
            elif event.button == 3:  # Right click
                self.selected_tower = None
                if self.selected_placed_tower:
                    self.selected_placed_tower.selected = False
                    self.selected_placed_tower = None
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.game_state == "playing":
                if not self.wave_in_progress:
                    self.wave_in_progress = True
                    self.spawn_timer = pygame.time.get_ticks()
                    self.enemies_spawned = 0
                    self.total_enemies_this_wave = self.wave * self.enemies_per_wave
                    print(f"Starting wave {self.wave} with {self.total_enemies_this_wave} enemies")
            elif event.key == pygame.K_ESCAPE and self.game_state == "playing":
                # Pressing ESC deselects the current tower
                self.selected_tower = None
                if self.selected_placed_tower:
                    self.selected_placed_tower.selected = False
                    self.selected_placed_tower = None
        
        elif event.type == pygame.MOUSEMOTION:
            # Handle tooltips on mouse movement
            self.update_tooltip(event.pos)
            
    def sell_tower(self, tower):
        # Calculate sell value (50% of original cost)
        tower_cost = self.tower_types[tower.tower_type]['cost']
        sell_value = int(tower_cost * 0.5)
        
        # Add the value to player's gold
        self.gold += sell_value
        
        # Find the tower's grid position
        grid_x = tower.x // self.grid_size
        grid_y = tower.y // self.grid_size
        
        # Update the grid to show the space is available
        self.grid[grid_y][grid_x] = 0
        
        # Remove the tower from the list
        self.towers.remove(tower)
        
        # Clear selection
        self.selected_placed_tower = None
        
        print(f"Tower sold for {sell_value} gold")

    def update_tooltip(self, mouse_pos):
        # Reset tooltip state
        self.show_tooltip = False
        
        # Only show tooltips when playing
        if self.game_state != "playing":
            return
            
        # Check if mouse is over a tower button
        for button in self.tower_buttons:
            if button['rect'].collidepoint(mouse_pos):
                self.show_tooltip = True
                self.tooltip_text = self.tower_types[button['type']]['description']
                self.tooltip_position = (mouse_pos[0] + 15, mouse_pos[1] + 15)  # Offset slightly from cursor
                break
    
    def draw_tooltip(self):
        if not self.show_tooltip:
            return
            
        # Split tooltip text into lines
        lines = self.tooltip_text.split('\n')
        
        # Calculate tooltip dimensions
        line_height = 20
        max_line_width = max(self.font_small.size(line)[0] for line in lines)
        tooltip_width = max_line_width + 20  # 10px padding on each side
        tooltip_height = len(lines) * line_height + 20  # 10px padding on top and bottom
        
        # Adjust position if tooltip would go off screen
        x, y = self.tooltip_position
        if x + tooltip_width > self.width:
            x = self.width - tooltip_width - 5
        if y + tooltip_height > self.height:
            y = self.height - tooltip_height - 5
            
        # Draw tooltip background with semi-transparency
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        tooltip_surface.fill((0, 0, 0, 200))  # Black with 80% opacity
        
        # Draw text
        for i, line in enumerate(lines):
            text_surface = self.font_small.render(line, True, (255, 255, 255))
            tooltip_surface.blit(text_surface, (10, 10 + i * line_height))
            
        # Draw border
        pygame.draw.rect(tooltip_surface, (255, 255, 255), 
                        (0, 0, tooltip_width, tooltip_height), 1)
            
        # Draw tooltip on screen
        self.screen.blit(tooltip_surface, (x, y))

    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    result = self.handle_event(event)
                    if result == "quit":
                        running = False
            
            # Update game state
            if self.game_state == "playing":
                self.update()
            
            # Draw everything
            self.screen.fill((0, 0, 0))  # Clear screen
            self.draw()
            
            # Control game speed
            clock.tick(60)  # 60 FPS
        
        return "quit" 