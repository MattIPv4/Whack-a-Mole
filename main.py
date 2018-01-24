import pygame
from random import randint as rnd, choice


class GameConstants:
    """
    Stores all the constants used in the game
    """

    # Game
    GAMEWIDTH       = 500
    GAMEHEIGHT      = 750
    GAMEMAXFPS      = 60

    # Levels
    LEVELGAP        = 4 #hits
    LEVELMOLESPEED  = 2 #% faster
    LEVELMOLECOUNT  = 10 #% less

    # Hole Size
    HOLEWIDTH       = 100
    HOLEHEIGHT      = int(HOLEWIDTH*(3/8))

    # Mole Data
    MOLEWIDTH       = int(HOLEWIDTH*(2/3))
    MOLEHEIGHT      = int(MOLEWIDTH)
    MOLEDEPTH       = 15 #% of height
    MOLECOOLDOWN    = 500 #ms
    MOLECHANCE      = 1/30
    MOLECOUNT       = 16
    MOLEUPMIN       = 0.3 #s
    MOLEUPMAX       = 2 #s

    # Holes
    HOLEROWS        = 4
    HOLECOLUMNS     = 4

    # PyGame Button Values
    LEFTMOUSEBUTTON = 1

    # Misc Data
    TITLE           = "Whack a Mole"


    # Checks
    if MOLECOUNT > HOLEROWS*HOLECOLUMNS:
        raise ValueError("MOLECOUNT too high")
    if HOLEHEIGHT*HOLEROWS > GAMEHEIGHT:
        raise ValueError("HOLEROWS or HOLEHEIGHT too high (or GAMEHEIGHT too small)")
    if HOLEWIDTH*HOLECOLUMNS > GAMEWIDTH:
        raise ValueError("HOLECOLUMNS or HOLEWIDTH too high (or GAMEWIDTH too small)")


class Score:
    """
    Handles the scoring for the player
    """

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.level = 1

    @property
    def score(self):
        return self.hits - (self.misses/2)

    def check_level(self):
        if self.score<0:
            self.level = 1
        else:
            self.level = 1 + (self.score // GameConstants.LEVELGAP)

    def hit(self):
        self.hits += 1
        self.check_level()

    def miss(self):
        self.misses += 1

    @property
    def attempts(self):
        return self.hits + self.misses

    @property
    def disp_score(self):
        hits = [self.hits, 0 if self.attempts==0 else self.hits/self.attempts*100]
        misses = [self.misses, 0 if self.attempts==0 else self.misses/self.attempts*100]
        return "Score: {:,} / Hits: {:,} ({:,.1f}%) / Misses: {:,} ({:,.1f}%) / Level: {:,}".format(
            self.score, hits[0], hits[1], misses[0], misses[1], self.level
        )

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
        self.current_hole = (0,0)
        self.last_hole = (0,0)
        self.show_time = 0

        # Current frame of showing animation
        self.show_frame = 0

        # Total number of frames to show for popping up
        self.frames = 5

        # Cooldown from last popup
        self.cooldown = 0
        self.hit = False

    def do_display(self, holes, level):

        # If in cooldown
        if self.cooldown != 0:
            if pygame.time.get_ticks() - self.cooldown < GameConstants.MOLECOOLDOWN:
                return [False]
            else:
                self.cooldown = 0
                return [False, 1, self.last_hole]

        # Random choice if not showing
        new_hole = False
        if self.showing_state == 0 and holes:
            # Reset
            self.show_frame = 0
            self.hit = False

            # Pick
            random = rnd(0, GameConstants.MOLECHANCE**-1)
            if random == 1:
                self.showing_state = 1
                self.showing_counter = 0

                level -= 1 # Start of 0
                level = 1 - ((GameConstants.LEVELMOLESPEED/100)*level)
                if level<0: level=0
                timeMin = int(GameConstants.MOLEUPMIN*1000*level)
                timeMax = int(GameConstants.MOLEUPMAX*1000*level)

                self.show_time = rnd(timeMin, timeMax)

                # Pick a new hole, don't pick the last one, don't infinite loop
                self.current_hole = self.last_hole
                if len(holes)>1 or self.current_hole != holes[0]:
                    while self.current_hole == self.last_hole:
                        self.current_hole = choice(holes)
                    self.last_hole = self.current_hole
                    new_hole = True

        # Show as popped up for a bit
        if self.showing_state == 1 and self.showing_counter != 0:
            if pygame.time.get_ticks() - self.showing_counter >= self.show_time:
                self.showing_state = -1
                self.showing_counter = 0

        # Return if game should display, including new hole data
        if new_hole:
            return [True, 0, self.current_hole]

        # Return if game should display
        return [(not self.showing_state==0)]

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

    def is_hit(self, pos):
        mouseX, mouseY = pos

        # Top Left
        moleX1, moleY1 = self.get_hole_pos(False)
        # Bottom Right
        moleX2, moleY2 = (moleX1+GameConstants.MOLEWIDTH, moleY1+GameConstants.MOLEHEIGHT)

        # Check is in valid to-be hit state
        if self.showing_state != 0 and not self.hit:
            # Check x
            if mouseX >= moleX1 and mouseX <= moleX2:
                # Check y
                if mouseY >= moleY1 and mouseY <= moleY2:
                    self.hit = True
                    self.showing_state = -1
                    self.show_frame = int(self.frames/2)
                    return True
        return False

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
        self.moles = [Mole() for _ in range(GameConstants.MOLECOUNT)]

        # Generate hole positions
        self.holes = []
        self.used_holes = []
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
        self.last_disp_score = ""

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
                    pos = pygame.mouse.get_pos()
                    hit = False
                    for mole in self.moles:
                        if mole.is_hit(pos):
                            hit = True
                            break

                    if hit:
                        self.score.hit()
                    else:
                        self.score.miss()

            # Display bg
            self.screen.blit(self.img_background, (0, 0))

            # Display holes
            for position in self.holes:
                self.screen.blit(self.img_hole, position)

            # Display moles
            for mole in self.moles:
                holes = [f for f in self.holes if f not in self.used_holes]
                mole_display = mole.do_display(holes, self.score.level)

                # If new/old hole given
                if len(mole_display)>1:
                    if mole_display[1]==0: # New hole
                        self.used_holes.append(mole_display[2])
                    else: # Old hole
                        if mole_display[2] in self.used_holes:
                            self.used_holes.remove(mole_display[2])

                # If should display
                if mole_display[0]:
                    # Get pos and display
                    pos = mole.get_hole_pos()
                    self.screen.blit(mole.img, pos)

            # Update display
            self.clock.tick(GameConstants.GAMEMAXFPS)
            pygame.display.flip()
            score = self.score.disp_score
            if score != self.last_disp_score:
                self.last_disp_score = score
                print(score)

    def run(self):
        pygame.init()
        self.start()
        pygame.quit()


theGame = Game()
theGame.run()