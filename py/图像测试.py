from fceux_dll import FCEuxDLL
import time
import os
import numpy as np
import PIL.Image

fceux = FCEuxDLL()

rom_path = "1.nes"
fceux.run_rom(rom_path)
# 高精度时间
start_time = time.perf_counter()
for i in range(10000):
    fceux.step_frame(1)
end_time = time.perf_counter()
print(f"10000帧耗时: {end_time - start_time} 秒")
# 高精度时间
start_time = time.perf_counter()
fceux.step_frame(10000)
end_time = time.perf_counter()
print(f"10000帧耗时: {end_time - start_time} 秒")

screen = fceux.read_screen()
if screen is not None:
    img = PIL.Image.fromarray(screen)
    img.show()
else:
    print("空图片")