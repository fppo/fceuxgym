from fceux_dll import FCEuxDLL
import time
import os

fceux = FCEuxDLL()

rom_path = "res/1.nes"
fceux.run_rom(rom_path1)
fceux.show_window()
while True:
    for i in range(100):
        fceux.step_frame(-1)
    fceux.reset()
