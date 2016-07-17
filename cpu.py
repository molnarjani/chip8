import random


class OpCode(int):
    @property
    def identifier(self):
        return (self & 0xf000) >> 12

    @property
    def nibble(self):
        return self & 0x000f

    @property
    def value(self):
        return self & 0x00ff

    @property
    def address(self):
        return self & 0x0fff

    @property
    def x(self):
        return (self & 0x0f00) >> 8

    @property
    def y(self):
        return (self & 0x00f0) >> 4

class Cpu(object):
    def __init__(self):
        # TODO: Maybe this is not needed at all
        self.running = True

        # 4 kilobytes of memory
        # 512 blocks reserver for interpreter
        # Thus most programs start at 0x200
        self.memory = [0] * 4 * 1024

        # 64x32 monochrome screen
        # A pixel is either 1 or 0
        self.display = [[0] * 64] * 32

        # 16bit program counter 
        # Stores currently executing memory address
        self.program_counter = 0x200

        # 16 8bit general purpose registers
        # V0 - VF, VF is used as a carry flag
        self.gprs = [0] * 16

        # 16bit index register
        # Used to store memory addresses
        self.index_register = 0

        # Stack is an array of 16 16bit value at max
        # Used to store previous address to return to from a subroutine
        # 8bit stack pointer
        # Stack pointer points to the top of the stack
        self.stack = [0] * 16
        self.stack_pointer = 0 

        # Timers
        # Autodecremented if > 0 at 60Hz
        # When sound timer is > 0 it play a buzz sound
        self.delay_timer = 0
        self.sound_timer = 0

        # stores current instruction
        self.opcode = OpCode(0)

        # maps identifier bits to instructions
        self.instruction_mapping = { 
            0x0: self._00E0_or_00EE,
            0x2: self._2nnn,
            0x3: self._3xkk,
            0x4: self._4xkk,
            0x6: self._6xkk,
            0x7: self._7xkk,
            0x8: self.map_logical_instructions,
            0xa: self._Annn,
            0xc: self._Cxkk,
            0xd: self._Dxyn,
            0xe: self.keypress_skips,
            0xf: self.map_misc_instructions,
        }

        self.misc_instruction_mapping = {
            0x18: self._Fx18,
            0x33: self._Fx33,        
            0x65: self._Fx65,
            0x29: self._Fx29,
        }

        self.logical_instruction_mapping = {
            0x4: self._8xy4,
        }

    def load_rom(self, rom_path):
        with open(rom_path, 'rb') as rom:
            for index, byte in enumerate(rom.read()):
                self.memory[index+0x200] = byte

    def map_misc_instructions(self):
        instruction = self.misc_instruction_mapping.get(self.opcode.value, None)
        if not instruction:
            raise Exception('Instruction not found {:x}'.format(self.opcode))
        else:
            instruction()

    def map_logical_instructions(self):
        instruction = self.logical_instruction_mapping.get(self.opcode.nibble, None)
        if not instruction:
            raise Exception('Instruction not found {:x}'.format(self.opcode))
        else:
            instruction()
    
    def _00E0_or_00EE(self):
        """ 00E0 - CLS
        Clear the display.

        00EE - RET
        Return from a subroutine.

        The interpreter sets the program counter to the address at the top of the stack, then subtracts 1 from the stack pointer.
        """
        if self.opcode.nibble == 0:
            self.display = [[0] * 64] * 32
        elif self.opcode.nibble == 0xe:
            self.stack_pointer -= 1
            self.program_counter = self.stack[self.stack_pointer]

    def _2nnn(self):
        """ 2nnn - CALL addr
        Call subroutine at nnn.

        The interpreter increments the stack pointer, then puts the current PC on the top of the stack.
        The PC is then set to nnn.
        """
        self.stack[self.stack_pointer] = self.program_counter
        self.stack_pointer += 1
        self.program_counter = self.opcode.address

    def _3xkk(self):
        """ 3xkk - SE Vx, byte
        Skip next instruction if Vx = kk.
        """
        if self.gprs[self.opcode.x] == self.opcode.value:
            self.program_counter += 2

    def _4xkk(self):
        """ 4xkk - SNE Vx, byte
        Skip next instruction if Vx != kk.
        """
        if self.gprs[self.opcode.x] != self.opcode.value:
            self.program_counter += 2

    def _6xkk(self):
        """ 6xkk - LD Vx, byte
        Set Vx = kk.

        The interpreter puts the value kk into register Vx.
        """
        self.gprs[self.opcode.x] = self.opcode.value

    def _7xkk(self):
        """ 7xkk - ADD Vx, byte
        Set Vx = Vx + kk.

        Adds the value kk to the value of register Vx, then stores the result in Vx. 
        """
        self.gprs[self.opcode.x] += self.opcode.value

    def _8xy4(self):
        """ Set Vx = Vx + Vy, set VF = carry.

        The values of Vx and Vy are added together. If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored in Vx.
        """
        self.gprs[self.opcode.x] += self.gprs[self.opcode.y]
        if self.gprs[self.opcode.x] > 0xff:
            self.gprs[0xf] = 1
        else:
            self.gprs[0xf] = 0


    def _Annn(self):
        """ Annn - LD I, addr

        The value of register I is set to nnn.
        """
        self.index_register = self.opcode.address

    def keypress_skips(self):
        if self.opcode.value == 0x9e:
            """ Ex9E - SKP Vx
            Skip next instruction if key with the value of Vx is pressed.
            """
            pass
        else:
            """ ExA1 - SKNP Vx
            Skip next instruction if key with the value of Vx is not pressed.
            """
            pass

    def _Cxkk(self):
        """ Cxkk - RND Vx, byte
        Set Vx = random byte AND kk.
        """
        self.gprs[self.opcode.x] = random.randint(0, 255) & self.opcode.value


    def _Fx18(self):
        """ Fx18 - LD ST, Vx
        Set sound timer = Vx.

        ST is set equal to the value of Vx.
        """
        self.sound_timer = self.gprs[self.opcode.x]

    def _Fx33(self):
        """ Fx33 - LD B, Vx
        Store BCD representation of Vx in memory locations I, I+1, and I+2.

        Decimal value of Vx is stored in memory starting at I:
        memory[I] = hunderds
        memory[I+1] = tens
        memory[I+2] = ones
        """
        n = self.gprs[self.opcode.x]
        self.memory[self.index_register] = n // 100
        self.memory[self.index_register+1] = n // 10 % 10
        self.memory[self.index_register+2] = n % 10

    def _Fx65(self):
        """ Fx65 - LD Vx, [I]
        Read registers V0 through Vx from memory starting at location I.
        """
        n = self.opcode.x
        values = self.memory[self.index_register:self.index_register+n]
        self.gprs[0:n] = values

    # TODO: Implement fonts
    def _Fx29(self):
        """ Fx29 - LD F, Vx
        Set I = location of sprite for digit Vx.

        The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx. See section 2.4, Display, for more information on the Chip-8 hexadecimal font.
        """
        pass

    # TODO: Implement and understand sprites
    def _Dxyn(self):
        """ 
        Dxyn - DRW Vx, Vy, nibble
        Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.

        The interpreter reads n bytes from memory, starting at the address stored in I. These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). Sprites are XORed onto the existing screen. If this causes any pixels to be erased, VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it is outside the coordinates of the display, it wraps around to the opposite side of the screen. See instruction 8xy3 for more information on XOR, and section 2.4, Display, for more information on the Chip-8 screen and sprites.
        """
        pass
