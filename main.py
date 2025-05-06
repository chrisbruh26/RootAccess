"""
Main entry point for the grid-based template version of Root Access.
This is a simplified template that can be expanded with features from the main game.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from grid_game import GridGame

if __name__ == "__main__":
    game = GridGame()
    game.create_world()
    game.run()
