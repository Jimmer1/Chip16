import chip64_util as c16u
import chip16_device as c16d
import chip16_except as c16e
import numpy as np
import itertools as itt
import warnings
import random

# Writing code to emulate low level hardware often requires using things like
# well modelled integer overflow. Numpy warns when this happens and thereby
# clogs the console with warnings about expected behaviour. This imperative
# prevents this.
warnings.filterwarnings("ignore")

deviceList = [
    c16d.ConsoleIO()
]

defaultDevices = deviceList + [None]*(16 - len(deviceList))

class Chip16:
    """
    The main class for the chip16 emulator.
    """

    def __init__(self, code=[], devices=defaultDevices):
        """
        Class constructor which initialises object state and handles relevant errors.
        """
        self.memory = [np.uint8(0)] * 4096
        self.registers = [np.uint16(0)] * 16
        self.stack = []
        self.code_ptr = np.uint16(0)
        self.memory_ptr = np.uint16(0)
        self.alert = False
        if len(code) > len(self.memory):
            raise SizeError()
        for i, byte in enumerate(code):
            self.memory[i] = byte
        self.devices = devices
    
    def reset(self):
        """
        A small helper class that resets the Chip16 object, typically called in tests.
        """
        self.__init__()