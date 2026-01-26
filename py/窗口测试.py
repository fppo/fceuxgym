from fceux_dll import FCEuxDLL
import time
import os

fceux = FCEuxDLL()

rom_path = "res/1.nes"
fceux.run_rom(rom_path)
time.sleep(5)
while True:
    print("显示")
    fceux.show_window()
    for i in range(1000):
        fceux.step_frame(-1)
    print("隐藏")
    fceux.hide_window()
    for i in range(1000):
        fceux.step_frame(-1)
