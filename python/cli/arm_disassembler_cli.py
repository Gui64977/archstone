from archstone import RawArmInstruction, Armv4TDisassembler

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
    disassembler = Armv4TDisassembler()
    print('=' * 11 + ' ArchStone Disassembler CLI ' + '=' * 11)
    
    while True:
        try:
            instr_str = input('> ')
            if instr_str.lower() in ('exit', 'quit'):
                break
            
            instr_value = parse_instruction(instr_str)
            instr = RawArmInstruction(instr_value)
            result = disassembler.disassemble(instr)
            print(f'{instr_value:08X}: {result}')
        except ValueError:
            print('Invalid format! Please try again.')
        except KeyboardInterrupt:
            print('\nAborted.')
            break

if __name__ == '__main__':
    main()
