from enum import Enum
import pygame


class GameConstants:
    """
    Stores all the constants used in the game
    """

    # Game Size
    GAMEWIDTH   = 500
    GAMEHEIGHT  = 750

    # Hole Size
    HOLEWIDTH  = int(GAMEWIDTH*0.25)
    HOLEHEIGHT  = int(HOLEWIDTH*(3/8))

    # Mole Size
    MOLEWIDTH   = int(HOLEWIDTH*(2/3))
    MOLEHEIGHT  = int(MOLEWIDTH)

    # Holes
    HOLEROWS    = 4
    HOLECOLUMNS = 3

    # PyGame Button Values
    LEFTMOUSEBUTTON = 1

    # Misc Data
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
        self.screen = pygame.display.set_mode((GameConstants.GAMEWIDTH, GameConstants.GAMEHEIGHT))
        pygame.display.set_caption(GameConstants.TITLE)

        # Load background
        self.img_background = pygame.image.load("background.png")
        self.img_background = pygame.transform.scale(self.img_background, (GameConstants.GAMEWIDTH, GameConstants.GAMEHEIGHT))

        # Load hole
        self.img_hole = pygame.image.load("hole.png")
        self.img_hole = pygame.transform.scale(self.img_hole, (GameConstants.HOLEWIDTH, GameConstants.HOLEHEIGHT))

        # Load mole
        self.img_mole = pygame.image.load("mole.png")
        self.img_mole = pygame.transform.scale(self.img_mole, (GameConstants.MOLEWIDTH, GameConstants.MOLEHEIGHT))

        # Generate hole positions
        self.holes = []
        base_row = GameConstants.GAMEHEIGHT/GameConstants.HOLEROWS
        base_column = GameConstants.GAMEWIDTH/GameConstants.HOLECOLUMNS
        for row in range(GameConstants.HOLEROWS):
            rowY = base_row * row
            rowY += (base_row-GameConstants.HOLEHEIGHT)/2
            for column in range(GameConstants.HOLECOLUMNS):
                thisX =  base_column * column
                thisX += (base_column-GameConstants.HOLEWIDTH)/2
                self.holes.append((int(thisX), int(rowY)))

        # Get the score object
        self.score = Score()

    def get_mole_position(self, hole_num):
        if hole_num >= len(self.holes):
            return (0,0)

        holeX, holeY = self.holes[hole_num]
        offset = (GameConstants.HOLEWIDTH-GameConstants.MOLEWIDTH)/2

        moleX = holeX+offset
        moleY = (holeY+GameConstants.HOLEHEIGHT) - (GameConstants.MOLEHEIGHT*1.1)
        return (moleX, moleY)

    def start(self):
        self.clock = pygame.time.Clock()
        self.loop = True

        while self.loop:

            # Handle PyGame events
            for event in pygame.event.get():

                # Handle quit
                if event.type == pygame.QUIT:
                    self.loop = False
                    continue

                # Handle click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == GameConstants.LEFTMOUSEBUTTON:
                    pass
                    # TODO: Do collision checks

            # Display bg
            self.screen.blit(self.img_background, (0, 0))

            # Display holes
            for position in self.holes:
                self.screen.blit(self.img_hole, position)

            # Display test moles
            for num in range(len(self.holes)):
                self.screen.blit(self.img_mole, self.get_mole_position(num))

            # Update display
            pygame.display.flip()

    def run(self):
        pygame.init()
        self.start()
        pygame.quit()


theGame = Game()
theGame.run()