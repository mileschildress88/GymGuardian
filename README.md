# Gym Guardian: Tower Defense Game 🏋️‍♂️

A tower defense game where you defend your gym from waves of invaders using fitness-themed towers!

## Game Overview

In Gym Guardian, you're tasked with defending your gym against waves of invaders. Place fitness-themed towers strategically along the path to stop the enemies from reaching the end.

### Features

- 6 unique fitness-themed towers:
  - Treadmill Turret
  - Protein Cannon
  - Yoga Sniper
  - Kettlebell Dropper
  - HIIT Barracks
  - Spin Class Laser
- Multiple enemy types: normal, fast, and boss enemies
- Wave-based gameplay with increasing difficulty
- Tower selection and placement system
- Grid-based map system

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/mileschildress88/GymGuardian.git
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

Run the game:
```bash
python main.py
```

### Controls
- Left Click: Place/Select towers
- Right Click: Cancel tower selection/placement
- Space: Start new wave

## Game Mechanics

- Place towers on the grid (not on the path)
- Each tower has different properties (damage, range, fire rate)
- Enemies follow the predefined path
- Each enemy that reaches the end will reduce your lives
- Defeat enemies to earn gold, which can be spent on more towers
- Complete waves to progress through the game

## Development

This game is built with Python and Pygame. The project structure is organized as follows:

- `main.py`: Game entry point
- `src/game.py`: Main game logic
- `src/towers.py`: Tower classes and mechanics
- `src/enemies.py`: Enemy classes and mechanics
- `src/projectiles.py`: Projectile system for towers
- `src/menu.py`: Game menu interface
- `src/map_selector.py`: Map selection system

## Future Improvements

- Add more tower types and upgrade system
- Implement power-ups
- Add sound effects and music
- Improve graphics and animations
- Add more enemy types and behaviors 