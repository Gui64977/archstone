# ArchStone

**ArchStone** is an assembler and disassembler for the **ARMv4T** instruction set.  
Based on *ARM ARM DDI 0100B*.  

![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python: 3.9+](https://img.shields.io/badge/python-3.9%2B-brightgreen)

---

## 🚧 Current Status

- ⏳ **ARM assembler**: not implemented yet  
- ✅ **ARM disassembler**: done (still in development)  
- ⏳ **Thumb-1 assembler**: not implemented yet  
- ⏳ **Thumb-1 disassembler**: in early development  

---

## 🚀 Roadmap

- Add an **ARM assembler**  
- Add a **Thumb-1 assembler**  
- Expand the **Thumb-1 disassembler**  
- Provide a **full JavaScript port**  
- Improve **documentation and usage examples**  

---

## ⚙️ Tech Stack

- **Language**: 🐍 Python 3.9+  
- **Dependencies**: None (standard library only)  

---

## 📦 Installation & Usage

```bash
# Clone the repository
git clone https://github.com/Gui64977/archstone

# Enter the Python module directory
cd archstone/python

# Install ArchStone module as editable
pip install -e .
```

### ▶️ Run the CLI disassembler

First go to `archstone/python` directory and run the following command:  

```bash
python cli/arm_disassembler_cli.py
```

You can type instructions in hexadecimal **(default)**, or with prefixes `0x` (hex), `0o` (octal), `0b` (binary).  
Type `exit` or `quit`, or press `CTRL+C` to leave the CLI.  

### ▶️ Example how to use the disassembler

```python
from archstone import RawArmInstruction, Armv4TDisassembler

disassembler = Armv4TDisassembler()
instr = RawArmInstruction(0xE8BB0002)  # LDMIA r11!, {r1}
print(disassembler.disassemble(instr)) # Output: LDMIA r11!, {r1}
```

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
See [LICENSE](./LICENSE) for details.  
