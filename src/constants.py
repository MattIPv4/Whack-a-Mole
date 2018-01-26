# -*- coding: utf-8 -*-

"""
Whack a Mole
~~~~~~~~~~~~~~~~~~~
A simple Whack a Mole game written with PyGame
:copyright: (c) 2018 Matt Cowley (IPv4)
"""


class GameConstants:

    GAMEWIDTH       = 500
    GAMEHEIGHT      = 750
    GAMEMAXFPS      = 60


class LevelConstants:

    LEVELGAP        = 10 #score
    LEVELMOLESPEED  = 5 #% faster
    LEVELMOLECHANCE = 10 #% less


class HoleConstants:

    HOLEWIDTH       = 100
    HOLEHEIGHT      = int(HOLEWIDTH*(3/8))
    HOLEROWS        = 4
    HOLECOLUMNS     = 3


class MoleConstants:

    MOLEWIDTH       = int(HoleConstants.HOLEWIDTH*(2/3))
    MOLEHEIGHT      = int(MOLEWIDTH)
    MOLEDEPTH       = 15 #% of height
    MOLECOOLDOWN    = 500 #ms

    MOLESTUNNED     = 1000 #ms
    MOLEHITHUD      = 500 #ms
    MOLEMISSHUD     = 250 #ms

    MOLECHANCE      = 1/30
    MOLECOUNT       = 5
    MOLEUPMIN       = 0.3 #s
    MOLEUPMAX       = 2 #s


class TextConstants:

    TITLE           = "Whack a Mole"
    FONTSIZE        = 15


class ImageConstants:

    IMAGEBASE       = "assets/"

    BACKGROUND      = IMAGEBASE + "background.png"

    MOLENORMAL      = IMAGEBASE + "mole.png"
    MOLEHIT         = IMAGEBASE + "mole_hit.png"

    HOLE            = IMAGEBASE + "hole.png"


class Constants(GameConstants, LevelConstants, HoleConstants, MoleConstants, TextConstants, ImageConstants):
    """
    Stores all the constants used in the game
    """

    DEBUGMODE       = True
    LEFTMOUSEBUTTON = 1

    # Checks
    if MoleConstants.MOLECOUNT > HoleConstants.HOLEROWS*HoleConstants.HOLECOLUMNS:
        raise ValueError("MOLECOUNT too high")
    if HoleConstants.HOLEHEIGHT*HoleConstants.HOLEROWS > GameConstants.GAMEHEIGHT:
        raise ValueError("HOLEROWS or HOLEHEIGHT too high (or GAMEHEIGHT too small)")
    if HoleConstants.HOLEWIDTH*HoleConstants.HOLECOLUMNS > GameConstants.GAMEWIDTH:
        raise ValueError("HOLECOLUMNS or HOLEWIDTH too high (or GAMEWIDTH too small)")