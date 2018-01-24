import pygame
from random import randint as rnd, choice


class GameConstants:
    """
    Stores all the constants used in the game
    """

    # Game
    GAMEWIDTH       = 500
    GAMEHEIGHT      = 750

    # Hole Size
    HOLEWIDTH       = int(GAMEWIDTH*0.25)
    HOLEHEIGHT      = int(HOLEWIDTH*(3/8))

    # Mole Data
    MOLEWIDTH       = int(HOLEWIDTH*(2/3))
    MOLEHEIGHT      = int(MOLEWIDTH)
    MOLEDEPTH       = 15
    MOLECOOLDOWN    = 500 #ms
    MOLECHANCE      = 1/30
    MOLECOUNT       = 1
    MOLEUPMIN       = 0.1 #s
    MOLEUPMAX       = 2 #s

    # Holes
    HOLEROWS        = 4
    HOLECOLUMNS     = 3

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


class Mole:
    """
    Provides the mole used in game
    """

    def __init__(self):
        self.img = pygame.image.load("mole.png")
        self.img = pygame.transform.scale(self.img, (GameConstants.MOLEWIDTH, GameConstants.MOLEHEIGHT))

        # State of showing animation
        # 0 = No, 1 = Doing Up, -1 = Doing Down
        self.showing_state = 0
        self.showing_counter = 0

        # Our current hole data
        self.current_hole = []
        self.last_hole = []
        self.show_time = 0

        # Current frame of showing animation
        self.show_frame = 0

        # Total number of frames to show for popping up
        self.frames = 5

        # Cooldown from last popup
        self.cooldown = 0

    def do_display(self, holes):

        # If in cooldown
        if self.cooldown != 0 and pygame.time.get_ticks() - self.cooldown < GameConstants.MOLECOOLDOWN:
            return False
        else:
            self.cooldown = 0

        # Random choice if not showing
        if self.showing_state == 0:
            # Reset
            self.show_frame = 0

            # Pick
            random = rnd(0, GameConstants.MOLECHANCE**-1)
            if random == 1:
                self.showing_state = 1
                self.showing_counter = 0
                timeMin = int(GameConstants.MOLEUPMIN*1000)
                timeMax = int(GameConstants.MOLEUPMAX*1000)
                self.show_time = rnd(timeMin, timeMax)

                # Pick a new hole, don't pick the last one
                self.current_hole = self.last_hole
                while self.current_hole == self.last_hole:
                    self.current_hole = choice(holes)
                self.last_hole = self.current_hole

        # Show as popped up for a bit
        if self.showing_state == 1 and self.showing_counter != 0:
            if pygame.time.get_ticks() - self.showing_counter >= self.show_time:
                self.showing_state = -1
                self.showing_counter = 0

        # Return if game should display
        return (not self.showing_state==0)

    def get_base_pos(self):
        holeX, holeY = self.current_hole
        offset = (GameConstants.HOLEWIDTH-GameConstants.MOLEWIDTH)/2

        moleX = holeX+offset
        moleY = (holeY+GameConstants.HOLEHEIGHT) - (GameConstants.MOLEHEIGHT*1.2)
        return (moleX, moleY)

    def get_hole_pos(self, do_tick=True):
        moleX, moleY = self.get_base_pos()

        frame = 0

        # Going Up
        if self.showing_state == 1:
            if self.show_frame <= self.frames:
                frame = GameConstants.MOLEDEPTH/self.frames * (self.frames-self.show_frame)
                if do_tick: self.show_frame += 1
            else:
                # Hold
                if self.showing_counter == 0:
                    self.showing_counter = pygame.time.get_ticks()

        # Going Down
        if self.showing_state == -1:
            if do_tick: self.show_frame -= 1
            if self.show_frame >= 0:
                frame = GameConstants.MOLEDEPTH / self.frames * (self.frames-self.show_frame)
            else:
                # Reset
                self.showing_state = 0
                frame = GameConstants.MOLEDEPTH
                # Begin cooldown
                if do_tick: self.cooldown = pygame.time.get_ticks()

        moleY += (GameConstants.MOLEHEIGHT * (frame/100))

        return (moleX, moleY)


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
        self.moles = [Mole()]*GameConstants.MOLECOUNT
        print(self.moles)

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

            # Display moles
            for mole in self.moles:
                if mole.do_display(self.holes):
                    pos = mole.get_hole_pos()
                    self.screen.blit(mole.img, pos)

            # Update display
            self.clock.tick(60)
            pygame.display.flip()

    def run(self):
        pygame.init()
        self.start()
        pygame.quit()


theGame = Game()
theGame.run()