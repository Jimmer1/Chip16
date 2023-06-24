"""
A module which implements the standard chip16 devices.
"""

import numpy as np

class MemoryDevice:
    """
    A memory extension device that allows the programmer to access 64k more memory.
    """
    def __init__(self):
        self.ptr = np.uint16(0)
        self.memory = [np.uint8(0) for _ in range(2**16)]
    
    def read(self, nbytes : int) -> list:
        return self.memory[self.ptr : self.ptr + nbytes]
    
    def write(self, bytes : list) -> None:
        for i, byte in enumerate(bytes):
            self.memory[self.ptr + i] = byte

    def get_ptr(self) -> np.uint16:
        return self.ptr

    def set_ptr(self, ptr_value : np.uint16) -> None:
        self.ptr = ptr_value

class FloatingPointDevice:
    """
    A FPU which lets the programmer work with floating point data values.
    """
    def __init__(self):
        pass

class ConsoleIO:
    """
    A device that implements Console Input and Output.
    """
    def __init__(self):
        self.format_code = np.uint16(0)
    
    def read(self, nbytes : int) -> list:
        if self.format_code == 0:
            return [np.uint8(ord(input())) for _ in range(nbytes)]
        elif self.format_code == 1:
            return [np.uint8(input()) for _ in range(nbytes)]
    
    def write(self, byte_list : list) -> None:
        if self.format_code == 0:
            for byte in byte_list:
                print(chr(byte))
        elif self.format_code == 1:
            print(hex(byte_list[0]))
            for byte in byte_list[1:]:
                print(hex(byte_list)[2:])
    
    def get_ptr(self) -> np.uint16:
        return self.format_code
    
    def set_ptr(self, ptr : np.uint16) -> None:
        self.format_code = ptr

class RomDevice:
    """
    A rom extension device that lets the programmer access roms left in rom.crm.
    """
    def __init__(self):
        self.ptr = np.uint16(0)
        self.memory = [np.uint8(0) for _ in range(2**16)]

        with open('rom.crm', 'rb') as rom_file:
            tmp = file.read()
            for i in range(self.memory.size()):
                self.memory[i] = np.uint8(tmp[i])
    
    def read(self, nbytes : int) -> list:
        return self.memory[self.ptr : self.ptr + nbytes]
    
    def write(self, bytes : list) -> None:
        for i, byte in enumerate(bytes):
            self.memory[self.ptr + i] = byte
        
    def get_ptr(self) -> np.uint16:
        return self.ptr
    
    def set_ptr(self, ptr_value : np.uint16) -> None:
        self.ptr = ptr_value