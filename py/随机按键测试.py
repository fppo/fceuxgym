from fceux_dll import FCEuxDLL
import time
import os
import random

fceux = FCEuxDLL()

rom_path = "res/1.nes"
fceux.run_rom(rom_path)
fceux.show_window()
while True:
    fceux.step_frame(-1)
    fceux.set_input(0, int(random.randint(0, 255)) % 0xFF)
