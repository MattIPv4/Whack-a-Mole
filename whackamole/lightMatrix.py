from gpiozero import LED
from .constants import Constants

class LightMatrix :
    """Handels the pysical light matrix"""
    def __init__(self, pins: list = Constants.PINS):
        self.leds = []
        for pin in pins:
            self.leds.append(LED(pin))

    def lightOn(self, pos: int):
        self.leds[pos].on()

    def lightOff(self, pos: int):
        self.leds[pos].off()

