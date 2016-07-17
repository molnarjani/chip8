import pytest

from cpu import Cpu, OpCode


@pytest.fixture
def cpu():
    cpu = Cpu()
    return cpu

def test_cpu_opcode_identifier(cpu):
    cpu.opcode = OpCode(0x1234)
    assert cpu.opcode.identifier == 1

def test_cpu_opcode_value(cpu):
    cpu.opcode = OpCode(0x1234)
    assert cpu.opcode.value == 0x34

def test_cpu_opcode_address(cpu):
    cpu.opcode = OpCode(0x1234)
    assert cpu.opcode.address == 0x234

def test_cpu_opcode_nibble(cpu):
    cpu.opcode = OpCode(0x1234)
    assert cpu.opcode.nibble == 0x4

def test_cpu_opcode_x(cpu):
    cpu.opcode = OpCode(0x1234)
    assert cpu.opcode.x == 2

def test_cpu_opcode_y(cpu):
    cpu.opcode = OpCode(0x1234)
    assert cpu.opcode.y == 3

def test_00E0(cpu):
    cpu.display = [[1] * 64] * 32
    cpu.opcode = OpCode(0x00e0)
    cpu._00E0_or_00EE()
    assert cpu.display == [[0] * 64] * 32

def test_00EE(cpu):
    cpu.opcode = OpCode(0x00ee)
    cpu.stack_pointer = 1
    cpu.stack[0] = 0xff
    cpu._00E0_or_00EE()
    assert cpu.program_counter == 0xff
    assert cpu.stack_pointer == 0

def test_2nnn_adds_program_counter_to_stack(cpu):
    old_program_counter = cpu.program_counter
    cpu._2nnn()
    assert cpu.stack[0] == old_program_counter

def test_2nnn_sets_pc_to_address(cpu):
    cpu.opcode = OpCode(0x2bab)
    cpu._2nnn()
    assert cpu.program_counter == 0xbab

def test_3xkk_if_not_equal(cpu):
    cpu.opcode = OpCode(0x43ff)
    cpu.program_counter = 6
    cpu.gprs[3] = 0x33
    cpu._3xkk()
    assert cpu.program_counter == 6

def test_3xkk_if_equal(cpu):
    cpu.opcode = OpCode(0x43ff)
    cpu.program_counter = 6
    cpu.gprs[3] = 0xff
    cpu._3xkk()
    assert cpu.program_counter == 8

def test_4xkk_if_not_equal(cpu):
    cpu.opcode = OpCode(0x43ff)
    cpu.program_counter = 6
    cpu.gprs[3] = 0x33
    cpu._4xkk()
    assert cpu.program_counter == 8

def test_4xkk_if_equal(cpu):
    cpu.opcode = OpCode(0x43ff)
    cpu.program_counter = 6
    cpu.gprs[3] = 0xff
    cpu._4xkk()
    assert cpu.program_counter == 6

def test_6xkk(cpu):
    cpu.opcode = OpCode(0x63ff)
    cpu._6xkk()
    assert cpu.gprs[3] == 0xff

def test_7xkk(cpu):
    cpu.opcode = OpCode(0x7312)
    cpu.gprs[3] = 0x66
    cpu._7xkk()
    assert cpu.gprs[3] == 120

def test_8xy4_if_lower_than_255(cpu):
    cpu.opcode = OpCode(0x8344)
    cpu.gprs[3] = 3
    cpu.gprs[4] = 5
    cpu._8xy4()
    assert cpu.gprs[3] == 8
    assert cpu.gprs[0xf] == 0

def test_8xy4_if_lower_than_255(cpu):
    cpu.opcode = OpCode(0x8784)
    cpu.gprs[7] = 0xff
    cpu.gprs[8] = 10
    cpu._8xy4()
    assert cpu.gprs[7] == 265
    assert cpu.gprs[0xf] == 1

def test_Annn(cpu):
    cpu.opcode = OpCode(0xA3ff)
    cpu._Annn()
    assert cpu.index_register == 0x3ff

def test_ExA1(cpu):
    assert 0

def test_Ex9E(cpu):
    assert 0

def test_Fx18(cpu):
    cpu.opcode = OpCode(0xfd18)
    cpu.gprs[0xd] = 2
    cpu._Fx18()
    assert cpu.sound_timer == 2

def test_Fx33_three_digits(cpu):
    cpu.opcode = OpCode(0xf033)
    cpu.gprs[0] = 213
    cpu._Fx33()
    assert cpu.memory[0:3] == [2, 1, 3]

def test_Fx33_two_digits(cpu):
    cpu.opcode = OpCode(0xf033)
    cpu.gprs[0] = 64
    cpu._Fx33()
    assert cpu.memory[0:3] == [0, 6, 4]

def test_Fx33_one_digit(cpu):
    cpu.opcode = OpCode(0xf033)
    cpu.gprs[0] = 9
    cpu._Fx33()
    assert cpu.memory[0:3] == [0, 0, 9]

def test_Fx65(cpu):
    cpu.opcode = OpCode(0xf365)
    cpu.memory[0:3] = [7, 6, 9]
    cpu._Fx65()
    assert cpu.gprs[0:3] == [7, 6, 9]

def test_Fx29(cpu):
    assert 0

def test_Dxyn(cpu):
    assert 0
