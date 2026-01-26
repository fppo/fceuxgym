from fceux_dll import FCEuxDLL
import time
import os

fceux = FCEuxDLL()

rom_path = "res/1.nes"
fceux.run_rom(rom_path)
fceux.show_window()
while True:
    fceux.step_frame(100)
    fceux.step_frame(-1)
