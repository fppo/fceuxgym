from fceux_dll import FCEuxDLL
import time
import os

fceux = FCEuxDLL()

rom_path = "1.nes"
fceux.run_rom(rom_path)
fceux.show_window()
fceux.step_frame(1000)

print("-----------------")
for i in range(100):
    fceux.step_frame(1000)
    state = fceux.save_state_lz4(1)
    print(f"状态大小: {len(state)}")
    
print("-----------------")
for i in range(100):
    print(f"i: {i}",end="\t")
    state = fceux.save_state_lz4(i)
    print(f"状态大小: {len(state)}",end="\t")
    start_time = time.time()
    for i in range(1000):
        state = fceux.save_state_lz4(i)
    end_time = time.time()
    # 时间小数点后4位
    print(f"1000次: {end_time - start_time:.4f} 秒")
