#!/usr/bin/env python3
from cpu import Cpu, OpCode

def main():
    cpu = Cpu()
    cpu.load_rom('games/UFO')

    while cpu.running:
        # each instruction is 2bytes long
        # so they need to be put together
        high_byte = cpu.memory[cpu.program_counter]
        low_byte = cpu.memory[cpu.program_counter+1]
        opcode = high_byte << 8 | low_byte
        cpu.opcode = OpCode(opcode)

        instruction = cpu.instruction_mapping.get(cpu.opcode.identifier, None)
        if not instruction:
            raise Exception('Instruction not found {:x}'.format(cpu.opcode))
        else:
            instruction()

        cpu.program_counter += 2


if __name__ == '__main__':
    main()
    
