import chip16_asm as c16a

import numpy as np
import unittest.mock as utm

def test_register_mnemonics():
    """
    Makes sure that the register_mnemonics are correct and not been tampered with.
    """
    assert c16a.register_mnemonics == [
        'r0', 'r1', 'r2', 'r3',
        'r4', 'r5', 'r6', 'r7',
        'r8', 'r9', 'rA', 'rB',
        'rC', 'rD', 'rE', 'rF'
    ]

def test_device_mnemonics():
    """
    As above but for the device mnemonics.
    """
    assert c16a.device_mnemonics == [
        'dev0', 'dev1', 'dev2', 'dev3',
        'dev4', 'dev5', 'dev6', 'dev7',
        'dev8', 'dev9', 'devA', 'devB',
        'devC', 'devD', 'devE', 'devF'
    ]

def test_build_opcode4():
    assert c16a.build_opcode((0x8, 0x0, 0x1, 0xF)) == np.uint16(0x801F)

def test_build_opcode3():
    assert c16a.build_opcode((0x3, 0x0, 0xAA)) == np.uint16(0x30AA)

def test_build_opcode2():
    assert c16a.build_opcode((0x2, 0xABC)) == np.uint16(0x2ABC)

def test_reg_tk_int():
    assert c16a.reg_tk_int("rF") == 0xF

def test_dev_tk_int():
    assert c16a.dev_tk_int("dev5") == 5

