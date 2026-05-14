# PacAI - Labirinto das Pérolas

A 2D AI-driven maze game implemented in Python using the Pygame library. This project was developed as part of an Artificial Intelligence curriculum to demonstrate pathfinding algorithms and real-time state management.

## Architecture & Design

The project is structured around a classic Game Loop pattern, maintaining a consistent 60 FPS for event handling, logic updates, and rendering.

### Key Technical Features:
* Finite State Machine (FSM): Robust state management handling transitions between MAIN_MENU, PLAYING, PAUSED, GAME_OVER, and EXIT.
* Dynamic Map Parsing: Implements a custom level loader that reads .txt files and converts character matrices into logical grids for the engine.
* Entity Component Logic: Entities (Pacman and Ghosts) utilize an accumulator-based movement system to synchronize logical positioning with visual rendering.
* AI Pathfinding: Initial implementation of search algorithms for ghost behavior, including randomized and targeted movement logic.

## Technologies
* Python 3.x
* Pygame: Used for rendering, event polling, and sound management.

## How to Run

1. Ensure you have Python and Pygame installed:
   ```bash
   pip install pygame
2. Run the main script:
   ```bash
   python main.py

## Legal Disclaimer

This is an educational project developed for university assignments. Graphic assets and audio files are used strictly for non-commercial, academic demonstration purposes. All rights belong to their respective owners.
