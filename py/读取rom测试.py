from fceux_dll import FCEuxDLL
import time
import os

fceux = FCEuxDLL()

rom_path1 = "res/1.nes"
rom_path2 = "res/2.nes"
fceux.run_rom(rom_path2)
fceux.show_window()
while True:
    for i in range(100):
        fceux.step_frame(-1)
    fceux.load_rom(rom_path1)
    for i in range(100):
        fceux.step_frame(-1)
    fceux.load_rom(rom_path2)
