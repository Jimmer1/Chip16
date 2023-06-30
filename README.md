# Chip64

A modification of the popular Chip8 virtual machine with adjustments to ease writing mathematical programs.


## Tutorial

In this tutorial, we shall see how to run a basic program using `Chip64`.
Observe the bytecode below:

```python
import chip64

code = [
    0xF0, 0x01, # r0 = input()
    0xD0, 0x02  # print(r0, hex)
]

c64 = chip64.Chip64(code)
c64.execute()
```

This program simply reads a number in from the console in decimal then prints that number in binary.

The `Chip64` library requires the `numpy` python library as an external dependency.


## How-To Guides

### How to Write Opcodes

`Chip64` uses a fixed width 16-bit instruction format stored high order byte first.
This means that the instruction 81E1 is represented as follows:

```python
instruction =  [0x81, 0xE1]
```


You will see opcodes written in the following formats in the following documentation, all values are in hexadecimal representation:  

PXYQ - P and Q indicate the operation and X and Y encode the register operands.  
PXNN - P indicates the operation, X encodes the register operand and NN is a code embedded constant.  
PNNN - P encodes the operation, NNN is a code embedded pointer value,  
PX0Q - P and Q encode the operation, X encodes the register operand.  
PXRR - P and RR encode the operation, X encodes the register operand.  

### How to assign values to registers.

There are two opcodes for assigning values to registers.

AR - 8XY0  
ACR - 6XNN  

AR copies the value from register Y into register X. This is demonstrated below:

```python
code = [
    0x80, 0x50 # copies the value held in register 5 to register 0
]
```

ACR copies the value NN into register X

ACR copies the value NN into register X, This is demonstrated below:

```python
code = [
    0x6F, 0x2a # register[0xF] = 42
]
```

### How to perform numeric arithmetic.

There are four opcodes for adding and subtraction operations:

Mnemonic - Opcode  
ADC - 7XNN  
ADD - 8XY4  
SUB - 8XY5  
RSUB - 8XY7  

ADC adds value NN to register X, without modifying the carry register, this is demonstrated below:

```python
code = [
    0x78, 0x2a # register[8] += 42
]
```

ADD adds register Y to register X, setting the carry flag if there is overflow and clearing if not, this is demonstrated below:

```python
code = [
    0x84, 0x14 # register[4] += register[1]
]
```

SUB subtracts register Y from register X, setting the carry flag if there is no borrow and clearing otherwise, this is demonstrated below:

```python
code = [
    0x8A, 0xE5 # register[10] -= register[14]
]
```

RSUB assigns to register X the value of register Y minus register X, setting the carry flag if there is no borrow and clearing otherwise, this is demonstrated below:

```python
code = [
    0x80, 0xD7 # register[0] = register[13] - register[0]
]
```

### How to perform bitwise arithmetic.

There are five opcodes for bitwise operations:

Mnemonic - Opcode  
OR - 8XY1  
AND - 8XY2  
XOR - 8XY3  
SHR - 8XY6  
SHL - 8XYE  

OR, AND, XOR implement the bitwise operations of the same names, modifying no flags. These are demonstrated below:

```python
code = [
    0x8B, 0x11, # register[11] |= register[1]
    0x83, 0x82, # register[3] &= register[2]
    0x86, 0x83  # register[6] ^= register[8]
]
```

SHR and SHL implement bit shift operators:  
SHR shifts register X right by Y places where Y in this instance represents a 4 bit encoded constant. The flag register is modified to hold the Yth bit in the destination register before the shift.
The SHR instruction is demonstrated below:

```python
code = [
    0x85, 0x36 # register[5] >>= 3
]
```

SHL shifts register X left by Y places where Y in this instance represents a 4 bit encoded constant. The flag register is modified to hold the (16-Y)th bit in the destination register before the shift.
The SHL instruction is demonstrated below:

```python
code = [
    0x87, 0xFE # register[7] <<= 14
]
```

### How to perform basic control flow.

Control flow in the Chip64 architecture typically takes the form of skipping the next instruction and unconditional jumps.

#### Unconditional Jumps

There are two opcodes that perform unconditional jumps:

Mnemonic - Opcode  
GOTO - 1NNN  
CPAC - BNNN  

GOTO unconditionally jumps to code address NNN, this is demonstrated below:

```python
code = [
    # 0x1004, GOTO $4
    0x10, # $0
    0x04, # $1 jumps to code address $4
    0x23, # $2
    0x2a, # $3
    0x87, # $4 execution carries on from here.
    0xFE  # $5
]
```

CPAC adds register 0 to constant NNN and sets the code pointer to this, this is demonstrated below

```python
code = [
    0x60, 0x2,  # register[0] = 2
    0xB0, 0x04, # goto register[0] + 4 essentially goto $6
    0x23, 0x65, # this gets skipped.
    0x80, 0     # execution resumes here.
]
```

#### Skipping Instructions

There are four opcodes that skip the next instruction.

Mnemonic - Opcode  
SNEC - 3XNN  
SNUEC - 4XNN  
SNE - 5XY0  
SNUE - 9XY0  

SNEC skips the next instruction if register X is equal to constant NN. This is demonstrated below:

```python
code = [
    0x30, 0x00 # if register[0] == 0 then
    0x70, 0x01 # skip register[0] += 1
]
```

SNUEC skips the next instruction if register X is unequal to constant NN. This is demonstrated below:

```python
code = [
    0x40, 0x00   # if register[0] != 0 then
    0x70, 0x1 # skip register[0] += 1
]
```

SNE skips the next instruction if register X is equal to register Y. This is demonstrated below:

```python
code = [
    0x50, 0x10, # if register[0] == register[1] then
    0x70, 0x01  # skip register[0] += 1
]
```

SNUE skips the next instruction if register X is unequal to register Y. This is demonstrated below:

```python
code = [
    0x90, 0x10, # if register[0] != register[1] then
    0x70, 0x01  # skip register[0] += 1
]
```

### How to call and return from subroutines.

There are two opcodes for calling and returning from subroutines:

Mnemonic - Opcode
RET - 01EE
CALL - 2NNN
CALLR - EX1C

CALL calls the subroutine at address NNN, CALL pushes the code pointer onto the top of the stack then sets the code pointer to NNN.

CALLR calls the subroutine at address rX.

RET returns from the current current subroutine. This instruction sets the code pointer to the to value held at the top of the call stack then pops the call stack.

These opcodes are demonstrated below:

```python 
code = [
    0x20, 0xFF, # calls the instruction at $0xFF.
    0xD0, 0,    # print register 0
    # .
    # .
    # .
    # $0xFF
    0x80, 0x10, # register[0] += register[1]
    0x1, 0xEE   # returns from the subroutine
]
```

### Using Devices.

A key feature of the Chip16 VM is the ability to use Devices. Devices are modular extensions to the Chip16 architecture which
implement additional functionality to enable the user to write more complex programs.

The basic interface of a Device consists of 4 operations:
    - Writing data to the Device.
    - Reading data from the Device.
    - Setting the Device's internal pointer.
    - Getting the Device's internal pointer.

This is the basic interface, what each operation does is defined by the device itself.

Any given instance of the Chip16 VM can support a maximum of 16 devices.
A number of standard devices are provided. They are as follows:
    - ConsoleIO Device:
        A device to allow the programmer to accept user input and output through the terminal.
        The read operation reads n bytes from the console in the format specified by the format code.
        The write operation prints the range of bytes to the console in a big endian format in the format specified by the format code.
        The set pointer operation sets the format code to the value held in rF.
        The get pointer operation stores the format code in rF.
        The format code sets i/o to be either textual if it's 0 and hexadecimal if it's 1.
        The ConsoleIO Device is available by default at index 0.
    - Memory Extension Device:
        A device to allow the VM to have access to an extra 64k of memory.
    - Rom Device:
        Allows the programmer to read data from the file rom.crm up to a limit of 64k, cannot write to that file.
    - Floating Point Device:
        Implements 32 bit floating point arithmetic.

There are 4 opcodes for interacting with Devices:

Mnemonic - Opcode  
WRITE - DXNN  
READ - FXNN  
DPS - 0xEX00  
DPG - 0xEX01  

WRB writes NN bytes to Device X from the memory pointed to by memory_ptr.
RDB reads NN bytes from Device X to the memory pointed to by memory_ptr.
DPS - sets Device X's pointer to the value held in rF.
DPG - sets rF to Device X's internal pointer.

### How to input and output from the console.

Using the console I/O Device shall be demonstrated below:

We shall print the value held in register 0 in hex.

```python
code = [
    0xAA, 0xBC # memory_ptr = 0xABC
    0xE0, 0x55 # *memory_ptr = r0
    0xE0, 0x00 # set console to format in hex
    0xD0, 0x02 # print the two bytes representing r0
]
```

### How to generate random numbers

There is a single opcode for generating random numbers:

Mnemonic - Opcode  
BAR - CXNN  

BAR sets register X to be a randomly generated integer in the range [0, 255] bitwise and constant NN.
This is demonstrated below:

```python
code = [
    0xC5, 0x00 # register[5] = rand(0, 255) & 0 
]
```

### How to read and write from memory

There are four opcodes for reading and writing to memory:

Mnemonic - Opcode  
SMP - ANNN  
RMP - EX1D
MPAR - EX1E  
SPL - EX55  
LD - EX65  

SMP sets the memory address to constant NNN. This is demonstrated below:

```python
code = [
    0xAA, 0xBC # memory pointer = 0xABC
]
```

RMP sets register X to the value of memory ptr.

MPAR increments the memory pointer by the value held in register X. This is demonstrated below:

```python
code = [
    0xE0, 0x1E # memory pointer += register[0]
]
```

SPL writes the contents of register X to memory. Data is written in a big endian format from the memory pointer without modifying the memory pointer. This is demonstrated below:

```python
code = [
    0xE5, 0x55 # write register 5 to memory.
]
```

LD reads from the memory pointed to by the memory pointer and writes these data to registers 0 to X inclusive. Data is read in a big endian format from register 0 first to register X last. This is demonstrated below:

```python
code = [
    0xE6, 0x65 # load from memory pointer to register 6.
]
```

### How to terminate a program

Upon encountering a 0000 opcode, the program will terminate. This opcode is represented by the HALT mnemonic.

### Illegal Opcodes

If an opcode is encountered which isn't does not encode a valid instruction, then an alert is raised.
The VM will continue execution as normal but the alert flag is raised.

## Explanation

### Chip64 Architectural Specification

The architecture is detailed below:

 - 16 16-bit registers
 - 1 12-bit program counter
 - 1 12-bit memory pointer
 - 4096 byte address space
 - call stack of 12-bit addressses with a depth of a minimum of 16 addresses.

The initial values that all registers and memory bytes take is unspecified, therefore one should not reply on the emulator to zero these data
for maximum portability.

Program execution begins from memory address 0, therefore if one wants to place subroutines at the beginning of the address space then the programmer is mandated to make the initial instruction and unconditional jump to the address where your main code begins.

### Value Signedness

All register and address space values are unsigned.

### Carry and Borrow

In the addition and subtraction instructions, the terms carry and borrow were defined.

Carry is defined as being when two given addition operands give a result that is too large to fit in a register.
For example, if I try to evaluate 0xFF + 0xFF in 8-bit arithmetic. then the result given is 0x1FE, which is too large to fit in an 8-bit register.
To indicate this to the programmer, a carry flag is set, in this case it is registers[0xF]. And the truncated 8-bit value 0xFE is given as the result of the addition.

Borrow is defined similarly as when two given subtraction operands give a result that is too small to fit in a register.
For example, if I try to evaluate 0 - 1 in 8 bit arithmetic. This is outside the range 0 - 0xFF so the value wraps around to the value 0xFF and so this needs to be indicated by a borrow flag.

## References

### List of functionality

This software exposes the `Chip64` object through which the user interacts with the system through the `Chip64::execute()` function.

Due to `Python`'s object oriententation model, there are a litany of internal implementation methods which are also exposed.
These methods should not be relied upon, nor should any code depend on any undocumented behaviour of the library.

### Bibliography

The wikipedia page on the Chip8 virtual machine can be useful background reading:  
https://en.wikipedia.org/wiki/CHIP-8

The design of the SHR and SHL opcodes is heavily based on the SHR/SHL opcodes from the x86 instruction set. More information can be found here:  
https://c9x.me/x86/html/file_module_x86_id_285.html

