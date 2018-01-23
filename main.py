from enum import Enum
import pygame


class GameConstants(Enum):
    """
    Stores all the constants used in the game
    """
    WIDTH   = 500
    HEIGHT  = 750
    TITLE   = "Whack a Mole"


class Score:
    """
    Handles the scoring for the player
    """

    def __init__(self):
        self.score = 0
        self.misses = 0
        self.level = 1


class Game:
    """
    Handles the main game
    """

    def __init__(self):
        # Create pygame screen
        self.screen = pygame.display.set_mode((GameConstants.WIDTH, GameConstants.HEIGHT))
        pygame.display.set_caption(GameConstants.TITLE)
