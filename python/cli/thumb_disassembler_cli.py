from archstone import RawThumbInstruction, Thumb1Disassembler

def parse_instruction(instr_str: str) -> int:
    instr_str = instr_str.strip().lower()
    if instr_str.startswith('0x'):
        return int(instr_str, 16)
    elif instr_str.startswith('0o'):
        return int(instr_str, 8)
    elif instr_str.startswith('0b'):
        return int(instr_str, 2)
    else:
        return int(instr_str, 16)

def main():
    disassembler = Thumb1Disassembler()
    print('=' * 7 + ' ArchStone Thumb-1 Disassembler CLI ' + '=' * 7)
    
    while True:
        try:
            instr_str = input('> ')
            
            if not instr_str:
                continue
            
            if instr_str.lower() in ('exit', 'quit'):
                break
            
            instr_value = parse_instruction(instr_str) & 0xFFFF
            instr = RawThumbInstruction(instr_value)
            result = disassembler.disassemble(instr)
            print(f'{instr_value:04X}: {result}')
        except ValueError:
            print('Invalid format! Please try again.')
        except KeyboardInterrupt:
            print('\nAborted.')
            break

if __name__ == '__main__':
    main()
