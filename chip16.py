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
        self.ram = [np.uint8(0)] * 4096
        self.R = [np.uint16(0)] * 16
        self.stack = []
        self.code_ptr = np.uint16(0)
        self.I = np.uint16(0)
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
    
    
    def ret(self):
        """
        Implements the ret instruction.
        Returns from subroutine.
        """
        self.code_ptr = self.stack.pop()

    
    def goto(self, address : np.uint16) -> None:
        """
        Implements the goto instruction.
        Sets the code pointer to a memory pointer.
        """
        assert 0 <= address < 4096
        self.code_ptr = address

    
    def call(self, address : np.uint16) -> None:
        """
        Implements the call instruction.
        Pushes the code pointer to the call stack and sets the code pointer to 
        the address of the subroutine given.
        """
        assert 0 <= address < 4096
        self.stack.append(self.code_ptr)
        self.code_ptr = address
    
    
    def snec(self, index : int, const : np.uint8) -> None:
        """
        Implements the snec instruction.
        Skips the next instruction if R[index] == const.
        """
        assert 0 <= index < 16
        if self.R[index] == constant:
            self.code_ptr += 2
    

    def snuec(self, index : int, const : np.uint8) -> None:
        """
        Implements the snuec instruction.
        Skips the next instruction if R[index] != const.
        """
        assert 0 <= index < 16
        if self.R[index] != constant:
            self.code_ptr += 2
    

    def sne(self, dest : int, src : int) -> None:
        """
        Implements the sne instruction.
        Skips the next instruction if R[dest] == R[src].
        """
        assert 0 <= dest < 16 and 0 <= src < 16
        if self.R[dest] == self.R[src]:
            self.code_ptr += 2
    

    def acr(self, dest : int, const : np.uint8) -> None:
        """
        Implements the acr instruction.
        Sets R[dest] = const.
        """
        assert 0 <= dest < 16
        self.R[dest] = np.uint16(const)
    

    def adc(self, dest : int, const : np.uint8) -> None:
        """
        Implements the adc instruction.
        Sets R[dest] += const without setting a carry flag.
        """
        assert 0 <= dest < 16
        self.R[dest] += np.uint16(const)
    

    def bit_or(self, dest : int, src : int) -> None:
        """
        Implements the or instruction.
        Sets R[dest] |= R[src].
        """
        assert 0 <= dest < 16 and 0 <= src < 16
        self.R[dest] |= self.R[src]
    

    def bit_and(self, dest : int, src : int) -> None:
        """
        Implements the and instruction.
        Sets R[dest] &= R[src].
        """
        assert 0 <= dest < 16 and 0 <= src < 16
        self.R[dest] &= self.R[src]
    

    def bit_xor(self, dest : int, src : int) -> None:
        """
        Implements the xor instruction.
        Sets R[dest] ^= R[src].
        """
        assert 0 <= dest < 16 and 0 <= src < 16
        self.R[dest] ^= self.R[src]
    

    def add(self, dest : int, src : int) -> None:
        """
        Implements the add instruction.
        Sets R[dest] += R[src] setting carry flag if carry generated.
        """
        assert 0 <= dest < 16 and 0 <= src < 16
        tmp = self.R[dest] + self.R[src]
        self.R[0xF] = np.uint16(tmp < self.R[dest])
        self.R[dest] = np.uint16(tmp)
    

    def sub(self, dest : int, src : int) -> None:
        """
        Implements the sub instruction.
        Sets R[dest] -= R[src] setting the carry flag if no-borrow.
        """
        assert 0 <= dest < 16 and 0 <= src < 16
        self.R[0xF] = np.uint16(self.R[dest] >= self.R[src])
        self.R[dest] -= self.R[src]
    

    def shr(self, dest : int, srcv : np.uint8) -> None:
        """
        Implements the shr instruction.
        Sets R[dest] >>= srcv setting the carry flag to the value of the
        (srcv+1)'th bit. If srcv == 0 then carry is set to zero.
        """
        assert 0 <= dest < 16 and 0 <= srcv < 16
        if srcv == 0:
            self.R[0xF] = np.uint16(0)
            return
        tmp = self.R[dest] & np.uint16(1 << (srcv - 1))       
        self.R[0xF] = np.uint16(tmp != 0)
        self.R[dest] >>= np.uint16(srcv)
    

    def shl(self, dest : int, srcv : np.uint8) -> None:
        """
        Implements the shl instruction.
        Sets R[dest] <<= R[src] setting the carry flag to the value of the
        (16-srcv)'th bit. If srcv == 0 then carry is set to zero.
        """
        assert 0 <= dest < 16 and 0 <= srcv < 16
        if srcv == 0:
            self.R[0xF] = np.uint16(0)
            return
        tmp = self.R[dest] & np.uint16(1 << (16 - src_value))
        self.R[0xF] = np.uint16(tmp != 0)
        self.R[dest] <<= np.uint16(srcv)
    

    def snue(self, dest : int, src : int) -> None:
        """
        Implements the snue instruction.
        Skips the next instruction if R[dest] != R[src].
        """
        assert 0 <= dest < 16 and 0 <= src < 16
        if self.R[dest] != self.R[src]:
            self.code_ptr += 2


    def smp(self, address : np.uint16) -> None:
        """
        Implements the smp instruction.
        Sets mem_ptr = value.
        """
        assert 0 <= address < 4096
        self.memory_ptr = value
    

    def cpac(self, const : np.uint8) -> None:
        """
        Implements the cpac instruction.
        Sets code_ptr = R[0] + const
        """
        self.code_ptr = self.R[0] + np.uint16(const)
    

    def bar(self, dest, const : np.uint8) -> None:
        """
        Implements the bar instruction.
        Sets R[dest] = randint(0, 255) & const
        """
        assert 0 <= dest < 255
        self.R[dest] = np.uint16(random.randint(0, 255)) & np.uint16(const)
    

    def mpar(self, index : int) -> None:
        """
        Implements the mpar instruction.
        Sets memory_ptr += R[dest].
        """
        assert 0 <= index < 16
        self.memory_ptr += self.R[index]

    
    def spl(self, index : int) -> None:
        """
        Implements the spl instruction.
        Writes R[index] to address referenced by memory_ptr.
        """
        assert 0 <= index < 16 and 0 <= self.I < len(self.ram)-1
        hi, low = c16u.high_byte(self.R[index]),
            c16u.low_byte(self.R[index])
        self.ram[self.I] = hi
        self.ram[self.I + 1] = lo
    

    def ldr(self, index : int) -> None:
        """
        Implements the ldr instruction.
        Reads a 16 bit word from ram and writes this to R[dest].
        """
        assert 0 <= index < 16 and 0 <= self.I < len(self.ram)-1
        hi, lo = self.ram[self.I], self.ram[self.I + 1]
        self.R[index] = np.uint16((hi << 8) | lo)

    def execute(self, num_of_cycles=None) -> None:
        """
        The main decode/execute loop of the emulator.
        num_of_cycles gives the number of cycles the emulator will run for
        if nothing is specified the emulator will cycle until a hlt is reached.
        """
        while num_of_cycles > 0 or num_of_cycles is None:
            opcode = c16u.concat(
                self.ram[self.code_ptr], self.ram[self.code_ptr + 1]
            )
            code_ptr_increment_flag = True


                continue
            
            if nib0 == 0:
                if opcode == 0x0000:
                    # hlt opcode
                    return
                elif opcode == 0x01EE:
                    self.ret()
                    self.code_ptr += 2

            elif nib3 == 1:
                self.goto(np.uint16(opcode & 0xFFF))
                code_ptr_increment_flag = False
            elif nib3 == 2:
                self.call(np.uint16(opcode & 0xFFF))
                code_ptr_increment_flag = False
            elif nib3 == 3:
                self.snec(c16u.get_nibble(opcode, 2), c16u.low_byte(opcode))
            elif nib3 == 4:
                self.snuec(c16u.get_nibble(opcode, 2), c16u.low_byte(opcode))
            elif nib3 == 5:
                self.sne(c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1))
            elif nib3 == 6:
                self.acr(c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1))
            elif nib3 == 7:
                self.adc(c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1))
            elif nib3 == 8:
                nib0 = c16u.get_nibble(opcode, 0)
                if nib0 == 0:
                    self.ar(
                        c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1)
                    )
                elif nib0 == 1:
                    self.bit_or(
                        c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1)
                    )
                elif nib0 == 2:
                    self.bit_and(
                        c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1)
                    )
                elif nib0 == 3:
                    self.bit_xor(
                        c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1)
                    )
                elif nib0 == 4:
                    self.add(
                        c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1)
                    )
                elif nib0 == 5:
                    self.sub(
                        c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1)
                    )
                elif nib0 == 6:
                    self.shr(
                        c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1)
                    )
                elif nib0 == 7:
                    self.sub(
                        c16u.get_nibble(opcode, 1), c16u.get_nibble(opcode, 2)
                    )
                elif nib0 == 0xE:
                    self.shl(
                        c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1)
                    )

            elif nib3 == 9:
                self.snue(
                    c16u.get_nibble(opcode, 2), c16u.get_nibble(opcode, 1)
                )
            elif nib3 == 0xA:
                self.smp(np.uint16(opcode & 0xFFF))
            elif nib3 == 0xB:
                self.cpac(np.uint16(opcode & 0xFFF))
                code_ptr_increment_flag = False
            elif nib3 == 0xC:
                self.bar(c16u.get_nibble(opcode, 2), c16u.low_byte(opcode))
            
            elif nib3 == 0xE:
                lb = c16u.low_byte(opcode)
                if lb == 0x0:
                    self.devices[
                        c16u.get_nibble(opcode, 2)
                    ].set_ptr(self.R[0xF])
                elif lb == 0x1:
                    self.R[0xF] = self.devices[
                        c16u.get_nibble(opcode, 2)
                    ].get_ptr()
                elif lb == 0x1E:
                    self.mpar(c16u.get_nibble(opcode, 2))
                elif lb == 0x55:
                    self.spl(c16u.get_nibble(opcode, 2))
                elif lb == 0x65:
                    self.ldr(c16u.get_nibble(opcode, 2))
            elif nib3 == 0xF:
                self.devices[
                    c16u.get_nibble(opcode, 2)
                ].write(self.ram[self.I : self.I + c16u.low_byte(opcode)])
            else:
                self.alert = True
            
            if code_ptr_increment_flag:
                self.code_ptr += 2
            
            if num_of_cycles is not None:
                num_of_cycles -= 1