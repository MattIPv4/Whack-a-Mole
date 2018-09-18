# -*- coding: utf-8 -*-

"""
Whack a Mole
~~~~~~~~~~~~~~~~~~~
A simple Whack a Mole game written with PyGame
:copyright: (c) 2018 Matt Cowley (IPv4)
"""

"""Search for '# !!' in the file to find the most common constant to change."""


class GameConstants:
    """
    Constants used for rendering of main game
    """

    GAMEWIDTH       = 500
    GAMEHEIGHT      = 750
    GAMEMAXFPS      = 60


class LevelConstants:
    """
    Constants used to handle leveling
    """

    LEVELGAP        = 10 #score
    LEVELMOLESPEED  = 5 #% faster
    LEVELMOLECHANCE = 10 #% less


class HoleConstants:
    """
    Constants used in the holes
    """

    HOLEWIDTH       = 100
    HOLEHEIGHT      = int(HOLEWIDTH*(3/8))
    HOLEROWS        = 12 # !!
    HOLECOLUMNS     = 5 # !!

    # Checks
    if HOLEHEIGHT*HOLEROWS > GameConstants.GAMEHEIGHT:
        raise ValueError("HOLEROWS or HOLEHEIGHT too high (or GAMEHEIGHT too small)")
    if HOLEWIDTH*HOLECOLUMNS > GameConstants.GAMEWIDTH:
        raise ValueError("HOLECOLUMNS or HOLEWIDTH too high (or GAMEWIDTH too small)")


class MoleConstants:
    """
    Constants used for mole generation and calculations
    """

    MOLEWIDTH       = int( HoleConstants.HOLEWIDTH*(2/3) )
    MOLEHEIGHT      = int(MOLEWIDTH)
    MOLEDEPTH       = 15 #% of height
    MOLECOOLDOWN    = 500 #ms

    MOLESTUNNED     = 1000 #ms
    MOLEHITHUD      = 500 #ms
    MOLEMISSHUD     = 250 #ms

    MOLECHANCE      = 1/30
    MOLECOUNT       = 30 # !!
    MOLEUPMIN       = 0.3 #s
    MOLEUPMAX       = 2 #s

    # Checks
    if MOLECOUNT > HoleConstants.HOLEROWS*HoleConstants.HOLECOLUMNS:
        raise ValueError("MOLECOUNT too high")


class TextConstants:
    """
    Constants used for text rendering
    """

    TEXTTITLE       = "Whack a Mole"
    TEXTFONTSIZE    = 15
    TEXTFONTFILE    = "assets/OxygenMono-Regular.ttf"


class ImageConstants:
    """
    Constants that are image based
    """

    IMAGEBASE       = "assets/"

    IMAGEBACKGROUND = IMAGEBASE + "background.png"

    IMAGEMOLENORMAL = IMAGEBASE + "mole.png"
    IMAGEMOLEHIT    = IMAGEBASE + "mole_hit.png"

    IMAGEHOLE       = IMAGEBASE + "hole.png"
    IMAGEMALLET     = IMAGEBASE + "mallet.png"


class MalletConstants:
    """
    Constants used for rendering the mallet
    """

    MALLETWIDTH     = int(HoleConstants.HOLEWIDTH)
    MALLETHEIGHT    = int(MALLETWIDTH)

    MALLETROTNORM   = 15
    MALLETROTHIT    = 30


class Constants(GameConstants, LevelConstants, HoleConstants, MoleConstants, TextConstants, ImageConstants, MalletConstants):
    """
    Stores all the constants used in the game
    """

    DEBUGMODE       = False
    LEFTMOUSEBUTTON = 1