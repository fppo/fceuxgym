from fceux_dll import FCEuxDLL
import time
import os

fceux = FCEuxDLL()

rom_path = "1.nes"
if os.path.exists(rom_path):
    print(f"Loading ROM: {rom_path}")
    result = fceux.run_rom(rom_path)
    print(f"run_rom result: {result}")
else:
    print(f"ROM file not found: {rom_path}")
    exit(1)

memory = fceux.read_memory()
print(f"Memory: {memory[0]:02X}")
