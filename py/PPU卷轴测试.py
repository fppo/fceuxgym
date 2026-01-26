from fceux_dll import FCEuxDLL
import time
import os

fceux = FCEuxDLL()

rom_path = "res/1.nes"
fceux.run_rom(rom_path)
while True:
    fceux.step_frame(1)
    scroll_x, scroll_y = fceux.get_scroll()
    print(f"Scroll: {scroll_x}, {scroll_y}")
