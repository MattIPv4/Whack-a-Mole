# -*- coding: utf-8 -*-

"""
Whack a Mole
~~~~~~~~~~~~~~~~~~~
A simple Whack a Mole game written with PyGame
:copyright: (c) 2018 Matt Cowley (IPv4)
"""

import pygame
from random import randint, choice

class GameConstants:
    """
    Stores all the constants used in the game
    """

    # Game
    GAMEWIDTH       = 500
    GAMEHEIGHT      = 750
    GAMEMAXFPS      = 60

    # Levels
    LEVELGAP        = 5 #score
    LEVELMOLESPEED  = 5 #% faster
    LEVELMOLECHANCE = 10 #% less

    # Hole Size
    HOLEWIDTH       = 100
    HOLEHEIGHT      = int(HOLEWIDTH*(3/8))

    # Mole Data
    MOLEWIDTH       = int(HOLEWIDTH*(2/3))
    MOLEHEIGHT      = int(MOLEWIDTH)
    MOLEDEPTH       = 15 #% of height
    MOLECOOLDOWN    = 500 #ms
    MOLESTUNNED     = 1000 #ms
    MOLECHANCE      = 1/30
    MOLECOUNT       = 5
    MOLEUPMIN       = 0.3 #s
    MOLEUPMAX       = 2 #s

    # Holes
    HOLEROWS        = 3
    HOLECOLUMNS     = 3

    # PyGame Button Values
    LEFTMOUSEBUTTON = 1

    # Misc Data
    TITLE           = "Whack a Mole"
    FONTSIZE        = 12


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

    @property
    def score(self):
        return self.hits - (self.misses/2)

    @property
    def level(self):
        if self.score<0:
            return 1
        else:
            return int(1 + (self.score // GameConstants.LEVELGAP))

    def wrap(self, string, length, break_char):
        safe_lines = []
        unsafe = string
        while len(unsafe) > length:
            slash_index = unsafe.rfind(break_char, 0, length)

            if slash_index == -1:
                safe_lines.append(unsafe)
                break

            _s = unsafe[0:slash_index].strip()
            _u = unsafe[slash_index + 1:].strip()
            safe_lines.append(_s)
            unsafe = _u

        safe_lines.append(unsafe)
        return safe_lines

    @property
    def label(self):
        # Can't be done in init as needs to be called after pygame.init()
        if not hasattr(self, 'font'):
            self.font = pygame.font.SysFont("monospace", GameConstants.FONTSIZE)

        # Generate test char
        test = self.font.render("a", 1, (0, 0, 0))
        # Calc line sizes
        max_line_width = GameConstants.GAMEWIDTH//test.get_width()
        line_height = test.get_height()

        # Get wrapped text
        lines = self.wrap(self.disp_score, max_line_width, "/")
        # Generate blank surface
        surface = pygame.Surface((GameConstants.GAMEWIDTH, GameConstants.GAMEHEIGHT), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()

        # Add lines
        y = 0
        for line in lines:
            label = self.font.render(line, 1, (255, 255, 0))
            surface.blit(label, (0, y))
            y += line_height+2

        return surface

    @property
    def attempts(self):
        return self.hits + self.misses

    @property
    def disp_score(self):
        hits = [self.hits, 0 if self.attempts==0 else self.hits/self.attempts*100]
        misses = [self.misses, 0 if self.attempts==0 else self.misses/self.attempts*100]
        return "Score: {:,.2f} / Hits: {:,} ({:,.1f}%) / Misses: {:,} ({:,.1f}%) / Level: {:,.0f}".format(
            self.score, hits[0], hits[1], misses[0], misses[1], self.level
        )

    def hit(self):
        self.hits += 1

    def miss(self):
        self.misses += 1

class Mole:
    """
    Provides the mole used in game
    """

    def __init__(self):
        # Load images
        self.img_normal = pygame.image.load("assets/mole.png")
        self.img_normal = pygame.transform.scale(self.img_normal, (GameConstants.MOLEWIDTH, GameConstants.MOLEHEIGHT))
        self.img_hit = pygame.image.load("assets/mole_hit.png")
        self.img_hit = pygame.transform.scale(self.img_hit, (GameConstants.MOLEWIDTH, GameConstants.MOLEHEIGHT))

        # State of showing animation
        # 0 = No, 1 = Doing Up, -1 = Doing Down
        self.showing_state = 0

        # Hold timestamp for staying up
        self.showing_counter = 0

        # Hold how long mole will stay up
        self.show_time = 0

        # Our current hole data
        self.current_hole = (0,0)
        self.last_hole = (0,0)

        # Current frame of showing animation
        self.show_frame = 0

        # Total number of frames to show for popping up (not timed)
        self.frames = 5

        # Cooldown from last popup
        self.cooldown = 0

        # Indicates if mole is hit
        # False = Not hit, timestamp for stunned freeze
        self.hit = False

    @property
    def image(self):
        if self.hit != False: return self.img_hit
        return self.img_normal

    def chance(self, level):
        level -= 1  # Start at 0

        levelChance = 1 - ((GameConstants.LEVELMOLECHANCE / 100) * level)
        if levelChance < 0: levelChance = 0  # TODO: Something better than 0 cause this essentially stops the game

        chance = int((GameConstants.MOLECHANCE ** -1) * levelChance)
        return chance

    def timeLimits(self, level):
        level -= 1  # Start at 0

        levelTime = 1 - ((GameConstants.LEVELMOLESPEED / 100) * level)
        if levelTime < 0: levelTime = 0  # TODO: Something better than 0 cause this essentially stops the game

        timeMin = int(GameConstants.MOLEUPMIN * 1000 * levelTime)
        timeMax = int(GameConstants.MOLEUPMAX * 1000 * levelTime)

        return (timeMin, timeMax)

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
            random = randint(0, self.chance(level))
            if random == 0:
                self.showing_state = 1
                self.showing_counter = 0

                self.show_time = randint(*self.timeLimits(level))

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

        # Stunned
        if self.hit != False:
            if pygame.time.get_ticks() - self.hit >= GameConstants.MOLESTUNNED:
                # Unfrozen after hit, hide
                if self.showing_state != 0:
                    self.showing_state = -1
            else:
                # Frozen from hit
                do_tick = False

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
        if self.showing_state != 0:
            # Check x
            if mouseX >= moleX1 and mouseX <= moleX2:
                # Check y
                if mouseY >= moleY1 and mouseY <= moleY2:
                    # Check is not stunned
                    if self.hit == False:
                        self.hit = pygame.time.get_ticks()
                        return 1
                    else:
                        return 2
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
        self.img_background = pygame.image.load("assets/background.png")
        self.img_background = pygame.transform.scale(self.img_background, (GameConstants.GAMEWIDTH, GameConstants.GAMEHEIGHT))

        # Load hole
        self.img_hole = pygame.image.load("assets/hole.png")
        self.img_hole = pygame.transform.scale(self.img_hole, (GameConstants.HOLEWIDTH, GameConstants.HOLEHEIGHT))

        # Load moles
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
                    missed = True
                    for mole in self.moles:
                        if mole.is_hit(pos) == 1: # Hit
                            hit = True
                            missed = False
                        if mole.is_hit(pos) == 2: # Hit but stunned
                            missed = False

                    if hit:
                        self.score.hit()
                    if missed:
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
                    self.screen.blit(mole.image, pos)

            # Display score
            score = self.score.label
            self.screen.blit(score, (5, 5))

            # Update display
            self.clock.tick(GameConstants.GAMEMAXFPS)
            pygame.display.flip()

    def run(self):
        pygame.init()
        self.start()
        pygame.quit()


theGame = Game()
theGame.run()