from fceux_dll import FCEuxDLL
import time
import os

fceux = FCEuxDLL()
fceux2 = FCEuxDLL()

rom_path = "res/1.nes"
fceux.run_rom(rom_path)
fceux.show_window()
# ret = fceux.load_config('E:/code/aiplayer/fceuxsimple/res/fceux.cfg')
# print(ret)

state1 = fceux.save_state_lz4()
# state2 = fceux.save_state_to_memory()

while True:
    fceux.reset()
    for i in range(100):
        fceux.step_frame(-1)
    fceux.load_state_lz4(state1)
    for i in range(1000):
        fceux.step_frame(-1)
        