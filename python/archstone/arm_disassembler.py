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

class RawArmInstruction:
    def __init__(self, value: int) -> None:
        self.value = value & 0xFFFFFFFF # Must be big-endian
    
    def get_bit(self, n: int) -> int:
        return (self.value >> n) & 1
    
    def get_bits(self, start: int, end: int) -> int:
        mask = (1 << (end - start + 1)) - 1
        return (self.value >> start) & mask


class Armv4TDisassembler:
    def get_decoder(self, instr: RawArmInstruction):
        PATTERNS = [ # (mask, expected_value, decoder)
            (0x0F000000, 0x0F000000, self.disassemble_software_interrupt),
            (0x0FFFFFF0, 0x012FFF10, self.disassemble_branch_exchange),
            (0x0E000000, 0x0A000000, self.disassemble_branch_and_branch_with_link),
            (0x0F000010, 0x0E000010, self.disassemble_coprocessor_register_transfer),
            (0x0F000010, 0x0E000000, self.disassemble_coprocessor_data_processing),
            (0x0E000000, 0x0C000000, self.disassemble_coprocessor_load_and_store),
            (0x0E000000, 0x08000000, self.disassemble_load_or_store_multiple),
            (0x0C000000, 0x04000000, self.disassemble_load_or_store),
            (0x0FC000F0, 0x00000090, self.disassemble_multiply),
            (0x0F8000F0, 0x00800090, self.disassemble_multiply_long),
            (0x0FB000F0, 0x01000090, self.disassemble_swap),
            (0x0D900000, 0x01000000, self.disassemble_move_from_or_to_status_reg),
            (0x0E000090, 0x00000090, self.disassemble_load_or_store_halfword_or_signed_byte),
            (0x0C000000, 0x00000000, self.disassemble_data_processing),
        ]
        
        # Returns the function (decoder) matching the instruction pattern, or None if no match
        for (mask, expected_value, decoder) in PATTERNS:
            if instr.value & mask == expected_value:
                return decoder
    
    def get_cond(self, instr: RawArmInstruction) -> str:
        CONDITION_CODES = [
            'EQ', 'NE', 'CS', 'CC', 'MI', 'PL', 'VS', 'VC',
            'HI', 'LS', 'GE', 'LT', 'GT', 'LE', 'AL', 'NV' # 'NV' cond may be ignored in the future
        ]
        
        cond_code = self.CONDITION_CODES[instr.get_bits(28, 31)]
        
        return '' if cond_code == 'AL' else cond_code
    
    def disassemble(self, instr: RawArmInstruction, lowerCaseOutput: bool = False) -> str:
        decoder = self.get_decoder(instr)
        if decoder is None:
            result = 'UNKNOWN'
        else:
            result = decoder(instr)
        
        return result.lower() if lowerCaseOutput else result
    
    def format_addressing_mode1(self, instr: RawArmInstruction) -> str:
        '''Format Data-processing Operands.'''
        i = instr.get_bit(25)
        
        if i: # Immediate operand
            imm = instr.get_bits(0, 7)
            rot = instr.get_bits(8, 11) * 2
            rotated = ((imm >> rot) | (imm << (32 - rot))) & 0xFFFFFFFF
            return f'#0x{rotated:x}'
        
        # Register operand
        shift_imm = instr.get_bits(7, 11) # In ARM ARM DDI 0100B page 3-84 this appears as 'Rs' instead of 'shift_imm'
        shift = instr.get_bits(5, 6)
        shift_name = ['LSL', 'LSR', 'ASR', 'ROR'][shift]
        rm = instr.get_bits(0, 3)
        
        if shift_name == 'LSL' and shift_imm == 0:
            return f'r{rm}'
        
        if shift_name == 'ROR' and shift_imm == 0:
            return f'r{rm}, RRX'
        
        if instr.get_bit(4): # Register shift
            if instr.get_bit(7): # SBZ
                return None
            rs = instr.get_bits(8, 11)
            return f'r{rm}, {shift_name} r{rs}'
        
        # Immediate shift
        return f'r{rm}, {shift_name} #{shift_imm}'
    
    def format_addressing_mode2(self, instr: RawArmInstruction) -> str:
        '''Format Load and Store Word or Unsigned Byte Addressing Modes.'''
        i, p, u, w = [instr.get_bit(n) for n in (25, 24, 23, 21)]
        rn = instr.get_bits(16, 19)
        sign = '' if u else '-'
        
        if not i: # Immediate offset
            offset = instr.get_bits(0, 11)
            if p:
                return f"[r{rn}, #{sign}0x{offset:x}]{'!' if w else ''}"
            else:
                return f'[r{rn}], #{sign}0x{offset:x}'
        
        # Register offset
        if instr.get_bit(4): # SBZ
            return None
        
        shift_imm = instr.get_bits(7, 11)
        shift = instr.get_bits(5, 6)
        rm = instr.get_bits(0, 3)
        shift_name = ['LSL', 'LSR', 'ASR', 'ROR'][shift]
        
        if shift_name == 'LSL' and shift_imm == 0:
            if p:
                return f"[r{rn}, {sign}r{rm}]{'!' if w else ''}"
            else:
                return f'[r{rn}], {sign}r{rm}'
        
        if shift_name == 'ROR' and shift_imm == 0:
            if p:
                return f"[r{rn}, {sign}r{rm}, RRX]{'!' if w else ''}"
            else:
                return f'[r{rn}], {sign}r{rm}, RRX'
        
        if p:
            return f"[r{rn}, {sign}r{rm}, {shift_name} #{shift_imm}]{'!' if w else ''}"
        else:
            return f'[r{rn}], {sign}r{rm}, {shift_name} #{shift_imm}'
    
    def format_addressing_mode3(self, instr: RawArmInstruction) -> str:
        '''Format Load and Store Halfword or Load Signed Byte Addressing Modes.'''
        p, u, i, w = [instr.get_bit(n) for n in (24, 23, 22, 21)]
        rn = instr.get_bits(16, 19)
        sign = '' if u else '-'
        
        if i: # Immediate offset
            imm_high = instr.get_bits(8, 11)
            imm_low = instr.get_bits(0, 3)
            imm = (imm_high << 4) | imm_low
            if p:
                return f"[r{rn}, #{sign}0x{imm:x}]{'!' if w else ''}"
            elif not w:
                return f'[r{rn}], #{sign}0x{imm:x}'
            else:
                return None
        
        # Register offset
        if instr.get_bits(8, 11) != 0: # SBZ
            return None
        
        rm = instr.get_bits(0, 3)
        
        if p:
            return f"[r{rn}, {sign}r{rm}]{'!' if w else ''}"
        elif not w:
            return f'[r{rn}], {sign}r{rm}'
        else:
            return None
    
    def format_addressing_mode4(self, instr: RawArmInstruction) -> str:
        '''Format Load and Store Multiple Addressing Modes.'''
        p, u = [instr.get_bit(n) for n in (24, 23)]
        return ['DA', 'IA', 'DB', 'IB'][(p << 1) | u]
    
    def format_addressing_mode5(self, instr: RawArmInstruction) -> str:
        '''Format Load and Store Coprocessor Addressing Modes.'''
        p, u, w = [instr.get_bit(n) for n in (24, 23, 21)]
        rn = instr.get_bits(16, 19)
        offset = instr.get_bits(0, 7) * 4
        sign = '' if u else '-'
        
        if p:
            return f"[r{rn}, #{sign}0x{offset:x}]{'!' if w else ''}"
        elif not w:
            return f'[r{rn}], #{sign}0x{offset:x}'
        else:
            return None
    
    def disassemble_software_interrupt(self, instr: RawArmInstruction) -> str:
        '''Disassemble Software interrupt instructions.'''
        swi_number = instr.get_bits(0, 23)
        
        return f'SWI{self.get_cond(instr)} #0x{swi_number:x}'
    
    def disassemble_branch_exchange(self, instr: RawArmInstruction) -> str:
        '''Disassemble Branch and Exchange instructions.'''
        if instr.get_bits(8, 19) != 0xFFF: # SBO
            return None
        
        rm = instr.get_bits(0, 3)
        
        return f'BX{self.get_cond(instr)} r{rm}'
    
    def disassemble_branch_and_branch_with_link(self, instr: RawArmInstruction) -> str:
        '''Disassemble Branch and Branch with link instructions.'''
        l = instr.get_bit(24)
        offset = instr.get_bits(0, 23)
        
        offset <<= 2
        
        if offset & (1 << 25): # Sign-extend offset
            offset |= ~((1 << 26) - 1)
        
        offset = (offset + 8) & 0xFFFFFFFF
        
        return f"{'BL' if l else 'B'}{self.get_cond(instr)} #0x{offset:x}"
    
    def disassemble_coprocessor_register_transfer(self, instr: RawArmInstruction) -> str:
        '''Disassemble Coprocessor register transfer instructions.'''
        op1 = instr.get_bits(21, 23)
        l = instr.get_bit(20)
        crn = instr.get_bits(16, 19)
        rd = instr.get_bits(12, 15)
        cp_num = instr.get_bits(8, 11)
        op2 = instr.get_bits(5, 7)
        crm = instr.get_bits(0, 3)
        
        return f"{'MRC' if l else 'MCR'}{self.get_cond(instr)} p{cp_num}, #{op1}, r{rd}, c{crn}, c{crm}, #{op2}"
    
    def disassemble_coprocessor_data_processing(self, instr: RawArmInstruction) -> str:
        '''Disassemble Coprocessor data processing instructions.'''
        op1 = instr.get_bits(20, 23)
        crn = instr.get_bits(16, 19)
        crd = instr.get_bits(12, 15)
        cp_num = instr.get_bits(8, 11)
        op2 = instr.get_bits(5, 7)
        crm = instr.get_bits(0, 3)
        
        return f'CDP{self.get_cond(instr)} p{cp_num}, #{op1}, c{crd}, c{crn}, c{crm}, #{op2}'
    
    def disassemble_coprocessor_load_and_store(self, instr: RawArmInstruction) -> str:
        '''Disassemble Coprocessor load and store instructions.'''
        l = instr.get_bit(20)
        crd = instr.get_bits(12, 15)
        cp_num = instr.get_bits(8, 11)
        addressing_mode = self.format_addressing_mode5(instr)
        
        if not addressing_mode:
            return None
        
        return f"{'LDC' if l else 'STC'}{self.get_cond(instr)} p{cp_num}, c{crd}, {addressing_mode}"
    
    def disassemble_load_or_store_multiple(self, instr: RawArmInstruction) -> str:
        '''Disassemble Load/store multiple instructions.'''
        s, w, l = [instr.get_bit(n) for n in (22, 21, 20)]
        reg_list = instr.get_bits(0, 15)
        rn = instr.get_bits(16, 19)
        addressing_mode = self.format_addressing_mode4(instr)
        
        if (s and w) or not reg_list or rn == 15:
            return None
        
        registers = [f'r{i}' for i in range(16) if reg_list & (1 << i)]
        
        return f"{'LDM' if l else 'STM'}{addressing_mode}{self.get_cond(instr)} r{rn}{'!' if w else ''}, {{{', '.join(registers)}}}{' ^' if s else ''}"
    
    def disassemble_load_or_store(self, instr: RawArmInstruction) -> str:
        '''Disassemble Load/Store instructions.'''
        
        p, b, w, l = [instr.get_bit(n) for n in (24, 22, 21, 20)]
        rd = instr.get_bits(12, 15)
        addressing_mode = self.format_addressing_mode2(instr)
        
        if not addressing_mode:
            return None
        
        return f"{'LDR' if l else 'STR'}{'B' if b else ''}{'T' if not p and w else ''}{self.get_cond(instr)} r{rd}, {addressing_mode}"
    
    def disassemble_multiply(self, instr: RawArmInstruction) -> str:
        '''Disassemble Multiply instructions.'''
        a, s = [instr.get_bit(n) for n in (21, 20)]
        rd = instr.get_bits(16, 19)
        rs = instr.get_bits(8, 11)
        rm = instr.get_bits(0, 3)
        
        if a: # MLA
            rn = instr.get_bits(12, 15)
            
            return f"MLA{'S' if s else ''}{self.get_cond(instr)} r{rd}, r{rm}, r{rs}, r{rn}"
        else: # MUL
            if instr.get_bits(12, 15) != 0: # SBZ
                return None
            
            return f"MUL{'S' if s else ''}{self.get_cond(instr)} r{rd}, r{rm}, r{rs}"
    
    def disassemble_multiply_long(self, instr: RawArmInstruction) -> str:
        '''Disassemble Multiply long instructions.'''
        u, a, s = [instr.get_bit(n) for n in (22, 21, 20)]
        rdhi = instr.get_bits(16, 19)
        rdlo = instr.get_bits(12, 15)
        rs = instr.get_bits(8, 11)
        rm = instr.get_bits(0, 3)
        
        if u: # Signed
            return f"{'SMLAL' if a else 'SMULL'}{'S' if s else ''}{self.get_cond(instr)} r{rdlo}, r{rdhi}, r{rm}, r{rs}"
        else: # Unsigned
            return f"{'UMLAL' if a else 'UMULL'}{'S' if s else ''}{self.get_cond(instr)} r{rdlo}, r{rdhi}, r{rm}, r{rs}"
    
    def disassemble_swap(self, instr: RawArmInstruction) -> str:
        '''Disassemble Swap instructions.'''
        if instr.get_bits(8, 11) != 0 or instr.get_bits(20, 21) != 0: # SBZ
            return None
        
        b = instr.get_bit(22)
        rn = instr.get_bits(16, 19)
        rd = instr.get_bits(12, 15)
        rm = instr.get_bits(0, 3)
        
        return f"SWP{'B' if b else ''}{self.get_cond(instr)} r{rd}, r{rm}, [r{rn}]"
    
    def disassemble_move_from_or_to_status_reg(self, instr: RawArmInstruction) -> str:
        '''Disassemble Move from/to Status register instructions.'''
        r = instr.get_bit(22)
        
        if not instr.get_bit(21): # MRS
            if instr.get_bits(0, 11) != 0 or instr.get_bits(16, 19) != 0xF: # SBZ/SBO
                return None
            
            rd = instr.get_bits(12, 15)
            return f"MRS{self.get_cond(instr)} r{rd}, {'SPSR' if r else 'CPSR'}"
        
        else: # MSR
            if instr.get_bits(12, 15) != 0xF: # SBO
                return None
            
            i = instr.get_bit(25)
            field_mask = instr.get_bits(16, 19)
            
            if not field_mask:
                return None
            
            fields = ''
            if field_mask & 0b1000:
                fields += 'f'
            if field_mask & 0b0100:
                fields += 's'
            if field_mask & 0b0010:
                fields += 'x'
            if field_mask & 0b0001:
                fields += 'c'
            
            if i: # Immediate
                if instr.get_bits(4, 11) != 0: # SBZ
                    return None
                
                rot = instr.get_bits(8, 11) * 2
                imm = instr.get_bits(0, 7)
                rotated_imm = ((imm >> rot) | (imm << (32 - rot))) & 0xFFFFFFFF
                
                return f"MSR{self.get_cond(instr)} {'SPSR' if r else 'CPSR'}_{fields}, #0x{rotated_imm:x}"
            else: # Register
                rm = instr.get_bits(0, 3)
                
                return f"MSR{self.get_cond(instr)} {'SPSR' if r else 'CPSR'}_{fields}, r{rm}"
    
    def disassemble_load_or_store_halfword_or_signed_byte(self, instr: RawArmInstruction) -> str:
        '''Disassemble Load/Store halfword/signed byte instructions.'''
        l, s, h = [instr.get_bit(n) for n in (20, 6, 5)]
        rd = instr.get_bits(12, 15)
        addressing_mode = self.format_addressing_mode3(instr)
        
        if not (s or h) or not addressing_mode:
            return None
        
        if l: # Load
            return f"LDR{['', 'H', 'SB', 'SH'][(s << 1) | h]}{self.get_cond(instr)} r{rd}, {addressing_mode}"
        else: # Store
            if instr.get_bits(5, 6) != 1: # Only STRH is valid
                return None
            
            return f'STRH{self.get_cond(instr)} r{rd}, {addressing_mode}'
    
    def disassemble_data_processing(self, instr: RawArmInstruction) -> str:
        '''Disassemble Data processing instructions.'''
        OPCODES = [
            'AND', 'EOR', 'SUB', 'RSB', 'ADD', 'ADC', 'SBC', 'RSC',
            'TST', 'TEQ', 'CMP', 'CMN', 'ORR', 'MOV', 'BIC', 'MVN'
        ]
        
        i, s = [instr.get_bit(n) for n in (25, 20)]
        opcode = instr.get_bits(21, 24)
        mnem = OPCODES[opcode]
        rn = instr.get_bits(16, 19)
        rd = instr.get_bits(12, 15)
        
        op2 = self.format_addressing_mode1(instr)
        if not op2:
            return None
        
        if mnem in ('MOV', 'MVN'):
            return f"{mnem}{'S' if s else ''}{self.get_cond(instr)} r{rd}, {op2}"
        elif mnem in ('TST', 'TEQ', 'CMP', 'CMN'):
            return f'{mnem}{self.get_cond(instr)} r{rn}, {op2}'
        else:
            return f"{mnem}{'S' if s else ''}{self.get_cond(instr)} r{rd}, r{rn}, {op2}"
