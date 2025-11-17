# ArchStone

**ArchStone** is an assembler and disassembler for the **ARMv4T** instruction set.  
Based on *ARM ARM DDI 0100B* (and *ARM ARM DDI 0100D*).  

![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python: 3.9+](https://img.shields.io/badge/python-3.9%2B-brightgreen)

---

## 🚧 Current Status

- ⏳ **ARM assembler**: not yet implemented  
- ✅ **ARM disassembler**: done (still in development)  
- ⏳ **Thumb assembler**: not yet implemented   
- ✅ **Thumb disassembler**: done (still in development and `BL` has not been implemented)   

---

## 🚀 Roadmap

- Add an **ARM assembler**  
- Add a **Thumb assembler**  
- Provide a **full JavaScript port**  
- Improve **documentation and usage examples**  

---

## ⚙️ Tech Stack

- **Language**: 🐍 Python 3.9+  
- **Dependencies**: None (standard library only)  

---

## 📦 Installation & Usage (Python)

### ▶️ Install the Python module

```bash
# Clone the repository
git clone https://github.com/Gui64977/archstone

# Enter the Python module directory
cd archstone/python

# Install ArchStone module as editable
pip install -e .
```

### ▶️ Run the CLI disassembler

From `archstone/python` directory, run one of the following commands:  

**ARM disassembler CLI**:  

```bash
python cli/arm_disassembler_cli.py
```

**Thumb disassembler CLI**:  

```bash
python cli/thumb_disassembler_cli.py
```

You can type instructions in hex **(default)**, or with prefixes `0x` (hex), `0o` (octal), and `0b` (binary).  
Type `exit` or `quit`, or press `CTRL+C` to leave the CLI.  

### ▶️ Example how to use the disassembler

**ARM disassembler**:

```python
from archstone import RawArmInstruction, Armv4TDisassembler

disassembler = Armv4TDisassembler()
instr = RawArmInstruction(0xE8BB0002)  # LDMIA r11!, {r1}
print(disassembler.disassemble(instr)) # Output: LDMIA r11!, {r1}
```

**Thumb disassembler**:

```python
from archstone import RawThumbInstruction, Thumb1Disassembler

disassembler = Thumb1Disassembler()
instr = RawThumbInstruction(0x4770)    # BX r14
print(disassembler.disassemble(instr)) # Output: BX r14
```

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
See [LICENSE](./LICENSE) for details.  
