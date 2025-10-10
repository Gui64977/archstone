'''
ArchStone - An assembler and disassembler for the ARMv4T instruction set.
Copyright (C) 2025 Gui64977

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

class RawThumbInstruction:
    def __init__(self, value: int) -> None:
        self.value = value & 0xFFFF # Must be big-endian
    
    def get_bit(self, n: int) -> int:
        return (self.value >> n) & 1
    
    def get_bits(self, start: int, end: int) -> int:
        mask = (1 << (end - start + 1)) - 1
        return (self.value >> start) & mask


class Thumb1Disassembler: # For ARMv4T, but it's based on ARM ARM DDI 0100D (ARMv5 documentation) due to the inaccuracy of ARM ARM DDI 0100B (ARMv4 documentation)
    def get_decoder(self, instr: RawThumbInstruction):
        PATTERNS = [
            (0xF800, 0x1800, self.disassemble_add_or_sub_reg),
            (0xE000, 0x0000, self.disassemble_shift_by_imm),
            (0xE000, 0x2000, self.disassemble_add_or_sub_or_cmp_or_mov_imm),
            (0xFC00, 0x4000, self.disassemble_dp_reg),
            (0xFC00, 0x4400, self.disassemble_special_dp),
            (0xF800, 0x4800, self.disassemble_load_from_literal_pool),
            (0xF000, 0x5000, self.disassemble_load_or_store_reg_offset),
            (0xE000, 0x6000, self.disassemble_load_or_store_word_or_byte_imm_offset),
            (0xF000, 0x8000, self.disassemble_load_or_store_halfword_imm_offset),
            (0xF000, 0x9000, self.disassemble_load_or_store_to_or_from_stack),
            (0xF000, 0xA000, self.disassemble_add_to_sp_or_pc),
            (0xFF00, 0xB000, self.disassemble_adjust_sp),
            (0xF600, 0xB400, self.disassemble_push_or_pop_reg_list),
            (0xF000, 0xC000, self.disassemble_load_or_store_multiple),
            (0xF000, 0xD000, self.disassemble_conditional_branch),
            (0xFF00, 0xDF00, self.disassemble_software_interrupt),
            (0xF800, 0xE000, self.disassemble_unconditional_branch),
            # Not implemented: (0xF000, 0xF000, self.disassemble_bl_prefix),
            # Not implemented: (0xF800, 0xF800, self.disassemble_bl_suffix),
        ]
        
        # Returns the function (decoder) matching the instruction pattern, or None if no match
        for (mask, expected_value, decoder) in PATTERNS:
            if instr.value & mask == expected_value:
                return decoder
    
    def disassemble(self, instr: RawThumbInstruction) -> str:
        decoder = self.get_decoder(instr)
        
        return (decoder(instr) if decoder else None) or 'UNKNOWN'
    
    def disassemble_add_or_sub_reg(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Add/subtract register instructions.'''
        i, op = [instr.get_bit(n) for n in (10, 9)]
        rm_imm = instr.get_bits(6, 8)
        rn = instr.get_bits(3, 5)
        rd = instr.get_bits(0, 2)
        
        if i:
            return f"{'SUB' if op else 'ADD'}S r{rd}, r{rn}, #{rm_imm}"
        else:
            return f"{'SUB' if op else 'ADD'}S r{rd}, r{rn}, r{rm_imm}"
    
    def disassemble_shift_by_imm(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Shift by immediate instructions.'''
        opcode = instr.get_bits(11, 12)
        mnem = ['LSL', 'LSR', 'ASR'][opcode]
        imm = instr.get_bits(6, 10)
        rm = instr.get_bits(3, 5)
        rd = instr.get_bits(0, 2)
        
        return f'{mnem}S r{rd}, r{rm}, #{imm}'
    
    def disassemble_add_or_sub_or_cmp_or_mov_imm(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Add/subtract/compare/move immediate instructions.'''
        opcode = instr.get_bits(11, 12)
        mnem = ['MOVS', 'CMP', 'ADDS', 'SUBS'][opcode]
        rd_rn = instr.get_bits(8, 10)
        imm = instr.get_bits(0, 7)
        
        return f'{mnem} r{rd_rn}, #0x{imm:x}'
    
    def disassemble_dp_reg(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Data-processing register instructions.'''
        OPCODES = [
            'ANDS', 'EORS', 'LSLS', 'LSRS', 'ASRS', 'ADCS', 'SBCS', 'RORS',
            'TST',  'NEGS', 'CMP',  'CMN',  'ORRS', 'MULS', 'BICS', 'MVNS'
        ]
        
        op = instr.get_bits(6, 9)
        mnem = OPCODES[op]
        rm_rs = instr.get_bits(3, 5)
        rd_rn = instr.get_bits(0, 2)
        
        return f'{mnem} r{rd_rn}, r{rm_rs}'
    
    def disassemble_special_dp(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Special data processing instructions.'''
        opcode = instr.get_bits(8, 9)
        mnem = ['ADD', 'CMP', 'MOV', 'BX'][opcode]
        h1, h2 = [instr.get_bit(n) for n in (7, 6)]
        rm = instr.get_bits(3, 5)
        rd_rn = instr.get_bits(0, 2)
        
        if mnem == 'BX':
            if h1 or rd_rn != 0: # SBZ
                return None
            
            return f'BX r{rm+8 if h2 else rm}'
        
        return f'{mnem} r{rd_rn+8 if h1 else rd_rn}, r{rm+8 if h2 else rm}'
    
    def disassemble_load_from_literal_pool(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Load from literal pool instructions.'''
        rd = instr.get_bits(8, 10)
        offset = instr.get_bits(0, 7) * 4
        
        return f'LDR r{rd}, [r15, #0x{offset:x}]'
    
    def disassemble_load_or_store_reg_offset(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Load/store register offset instructions.'''
        opcode = instr.get_bits(9, 11)
        mnem = ['STR', 'STRH', 'STRB', 'LDRSB', 'LDR', 'LDRH', 'LDRB', 'LDRSH'][opcode]
        rm = instr.get_bits(6, 8)
        rn = instr.get_bits(3, 5)
        rd = instr.get_bits(0, 2)
        
        return f'{mnem} r{rd}, [r{rn}, r{rm}]'
    
    def disassemble_load_or_store_word_or_byte_imm_offset(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Load/store word/byte immediate offset instructions.'''
        b, l = [instr.get_bit(n) for n in (12, 11)]
        imm = instr.get_bits(6, 10) * (1 if b else 4)
        rn = instr.get_bits(3, 5)
        rd = instr.get_bits(0, 2)
        
        return f"{'LDR' if l else 'STR'}{'B' if b else ''} r{rd}, [r{rn}, #0x{imm:x}]"
    
    def disassemble_load_or_store_halfword_imm_offset(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Load/store halfword immediate offset instructions.'''
        l = instr.get_bit(11)
        imm = instr.get_bits(6, 10) * 2
        rn = instr.get_bits(3, 5)
        rd = instr.get_bits(0, 2)
        
        return f"{'LDR' if l else 'STR'}H r{rd}, [r{rn}, #0x{imm:x}]"
    
    def disassemble_load_or_store_to_or_from_stack(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Load/store to/from stack instructions.'''
        l = instr.get_bit(11)
        rd = instr.get_bits(8, 10)
        offset = instr.get_bits(0, 7) * 4
        
        return f"{'LDR' if l else 'STR'} r{rd}, [r13, #0x{offset:x}]"
    
    def disassemble_add_to_sp_or_pc(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Add to SP or PC instructions.'''
        sp = instr.get_bit(11)
        rd = instr.get_bits(8, 10)
        imm = instr.get_bits(0, 7) * 4
        
        return f"ADD r{rd}, {'r13' if sp else 'r15'}, #0x{imm:x}"
    
    def disassemble_adjust_sp(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Adjust stack pointer instructions.'''
        op = instr.get_bit(7)
        imm = instr.get_bits(0, 6) * 4
        
        return f"{'SUB' if op else 'ADD'} r13, #0x{imm:x}"
    
    def disassemble_push_or_pop_reg_list(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Push/pop register list instructions.'''
        l, r = [instr.get_bit(n) for n in (11, 8)]
        reg_list = instr.get_bits(0, 7)
        
        if not (r or reg_list):
            return None
        
        registers = [f'r{i}' for i in range(8) if reg_list & (1 << i)]
        
        if r:
            registers.append(f"{'r15' if l else 'r14'}")
        
        return f"{'POP' if l else 'PUSH'} {{{', '.join(registers)}}}"
    
    def disassemble_load_or_store_multiple(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Load/store multiple instructions.'''
        l = instr.get_bit(11)
        rn = instr.get_bits(8, 10)
        reg_list = instr.get_bits(0, 7)
        
        if not reg_list:
            return None
        
        registers = [f'r{i}' for i in range(8) if reg_list & (1 << i)]
        
        return f"{'LDM' if l else 'STM'}IA r{rn}!, {{{', '.join(registers)}}}"
    
    def disassemble_conditional_branch(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Conditional branch instructions.'''
        CONDITION_CODES = [
            'EQ', 'NE', 'CS', 'CC', 'MI', 'PL', 'VS', 'VC',
            'HI', 'LS', 'GE', 'LT', 'GT', 'LE', 'AL', 'NV' # 'NV' cond may be ignored in the future
        ]
        
        cond_code = CONDITION_CODES[instr.get_bits(8, 11)]
        cond = '' if cond_code == 'AL' else cond_code
        imm = instr.get_bits(0, 7) << 1
        
        if imm & (1 << 8): # Sign-extend immediate
            imm |= ~((1 << 9) - 1)
        
        imm = (imm + 4) & 0xFFFFFFFF
        
        return f'B{cond} #0x{imm:x}'
    
    def disassemble_software_interrupt(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Software interrupt instructions.'''
        imm = instr.get_bits(0, 7)
        
        return f'SWI 0x{imm:x}'
    
    def disassemble_unconditional_branch(self, instr: RawThumbInstruction) -> str:
        '''Disassemble Unconditional branch instructions.'''
        imm = instr.get_bits(0, 10) << 1
        
        if imm & (1 << 11): # Sign-extend immediate
            imm |= ~((1 << 12) - 1)
        
        imm = (imm + 4) & 0xFFFFFFFF
        
        return f'B 0x{imm:x}'
    
    def disassemble_bl_prefix(self):
        raise NotImplemented
    
    def disassemble_bl_suffix(self):
        raise NotImplemented
