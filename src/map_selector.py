import pygame

class MapSelector:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, 48)  # Increased font size
        self.font_small = pygame.font.Font(None, 24)
        
        # Define map previews
        self.map_previews = [
            {
                'name': 'Straight Path',
                'path': [(0, 5)] + [(x, 5) for x in range(1, 20)],  # Simplified straight path
                'description': 'A straightforward path perfect for beginners'
            },
            {
                'name': 'Zigzag Path',
                'path': ([(0, 5)] + [(x, 5) for x in range(1, 19)] +  # First horizontal line
                        [(19, y) for y in range(5, 10)] +  # First vertical line
                        [(x, 10) for x in range(19, 0, -1)] +  # Second horizontal line
                        [(0, y) for y in range(10, 15)] +  # Second vertical line
                        [(x, 15) for x in range(0, 20)]),  # Final horizontal line
                'description': 'A challenging path with multiple turns'
            },
            {
                'name': 'Spiral Path',
                'path': ([(0, 2)] +  # Start point
                        [(x, 2) for x in range(1, 18)] +  # Top edge
                        [(18, y) for y in range(2, 16)] +  # Right edge
                        [(x, 16) for x in range(18, 2, -1)] +  # Bottom edge
                        [(2, y) for y in range(16, 4, -1)] +  # Left edge
                        [(x, 4) for x in range(2, 16)] +  # Inner top
                        [(16, y) for y in range(4, 14)] +  # Inner right
                        [(x, 14) for x in range(16, 4, -1)] +  # Inner bottom
                        [(4, y) for y in range(14, 6, -1)] +  # Inner left
                        [(x, 6) for x in range(4, 14)] +  # Inner horizontal
                        [(14, y) for y in range(6, 8)] +  # Final vertical to center
                        [(x, 8) for x in range(14, 9, -1)]),  # Final move to center
                'description': 'A complex spiral path for experienced players'
            }
        ]
        
        # Calculate preview dimensions and spacing
        self.preview_width = 250  # Increased preview size
        self.preview_height = 250
        self.preview_spacing = 100  # Increased spacing
        self.start_x = (self.width - (self.preview_width * 3 + self.preview_spacing * 2)) // 2
        self.start_y = 150  # Moved up to make room for descriptions
        
        # Create preview rectangles
        self.preview_rects = []
        for i in range(3):
            rect = pygame.Rect(
                self.start_x + i * (self.preview_width + self.preview_spacing),
                self.start_y,
                self.preview_width,
                self.preview_height
            )
            self.preview_rects.append(rect)
        
        # Title
        self.title = self.font.render("Choose Your Map", True, (255, 255, 255))
        self.title_rect = self.title.get_rect(center=(self.width // 2, 80))

    def draw(self, screen):
        # Fill background
        screen.fill((20, 20, 20))
        
        # Draw title
        screen.blit(self.title, self.title_rect)
        
        # Draw map previews
        for i, (map_data, rect) in enumerate(zip(self.map_previews, self.preview_rects)):
            # Draw preview background (darker than game background)
            pygame.draw.rect(screen, (40, 40, 40), rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 2)
            
            # Draw grid and path
            grid_size = self.preview_width / 20
            for y in range(20):
                for x in range(20):
                    cell_rect = pygame.Rect(
                        rect.x + x * grid_size,
                        rect.y + y * grid_size,
                        grid_size, grid_size
                    )
                    # Draw placeable area in dark green
                    pygame.draw.rect(screen, (0, 40, 0), cell_rect)
                    # Draw grid lines
                    pygame.draw.rect(screen, (60, 60, 60), cell_rect, 1)
            
            # Draw path with gradient and end marker
            path_points = map_data['path']
            for j in range(len(path_points) - 1):
                start_x, start_y = path_points[j]
                end_x, end_y = path_points[j + 1]
                
                # Calculate progress through path for gradient
                progress = j / (len(path_points) - 1)
                color = (
                    int(60 + progress * 40),
                    int(60 + progress * 40),
                    int(80 + progress * 40)
                )
                
                # Draw path segment
                pygame.draw.rect(screen, color,
                               (rect.x + start_x * grid_size,
                                rect.y + start_y * grid_size,
                                grid_size, grid_size))
            
            # Draw end marker (black tile)
            end_x, end_y = path_points[-1]
            pygame.draw.rect(screen, (0, 0, 0),
                           (rect.x + end_x * grid_size,
                            rect.y + end_y * grid_size,
                            grid_size, grid_size))
            
            # Draw map name with larger font
            name_text = self.font.render(map_data['name'], True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(rect.centerx, rect.bottom + 40))
            screen.blit(name_text, name_rect)
            
            # Draw description with better spacing
            desc_text = self.font_small.render(map_data['description'], True, (200, 200, 200))
            desc_rect = desc_text.get_rect(center=(rect.centerx, rect.bottom + 70))
            screen.blit(desc_text, desc_rect)

    def handle_click(self, pos):
        for i, rect in enumerate(self.preview_rects):
            if rect.collidepoint(pos):
                return self.map_previews[i]['path']
        return None 