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

time.sleep(2)

print("\n=== Testing DLL Functions ===\n")

print("1. Testing hide_window()...")
result = fceux.hide_window()
print(f"   hide_window() returned: {result}")

time.sleep(1)

print("2. Testing show_window()...")
result = fceux.show_window()
print(f"   show_window() returned: {result}")

time.sleep(1)

print("3. Testing read_memory()...")
memory = fceux.read_memory()
if memory:
    print(f"   read_memory() returned valid pointer")
else:
    print(f"   read_memory() returned NULL")

print("4. Testing read_screen()...")
screen = fceux.read_screen()
if screen:
    print(f"   read_screen() returned valid pointer")
else:
    print(f"   read_screen() returned NULL")

print("5. Testing set_input()...")
for port in range(4):
    test_input = 0x01 | (0x02 << (port * 8))
    result = fceux.set_input(port, test_input)
    print(f"   set_input(port={port}, input=0x{test_input:02X}) returned: {result}")

print("6. Testing clear_input()...")
result = fceux.clear_input()
print(f"   clear_input() returned: {result}")

print("7. Testing get_scroll()...")
scroll_x, scroll_y = fceux.get_scroll()
if scroll_x is not None:
    print(f"   get_scroll() returned: scroll_x={scroll_x}, scroll_y={scroll_y}")
else:
    print(f"   get_scroll() failed")

print("\n8. Testing step_frame()...")
print("   Stepping 5 frames...")
for i in range(5):
    result = fceux.step_frame(1)
    print(f"   step_frame(1) frame {i+1} returned: {result}")
    time.sleep(0.1)

print("\n9. Testing save_state() and load_state()...")
save_path = "test_state.fcs"
result = fceux.save_state(save_path)
print(f"   save_state('{save_path}') returned: {result}")

time.sleep(0.5)

result = fceux.load_state(save_path)
print(f"   load_state('{save_path}') returned: {result}")

if os.path.exists(save_path):
    os.remove(save_path)
    print(f"   Cleaned up test state file")

print("\n=== All tests completed ===")

print("\nContinuous reading of memory and screen...")
frame_count = 0
try:
    while frame_count < 100:
        memory = fceux.read_memory()
        screen = fceux.read_screen()
        scroll_x, scroll_y = fceux.get_scroll()
        
        if memory and frame_count % 30 == 0:
            print(f"Frame {frame_count}: Memory ptr={hex(memory[0])}, Screen ptr={hex(screen[0] if screen else 0)}, Scroll=({scroll_x}, {scroll_y})")
        
        frame_count += 1
        time.sleep(0.033)
except KeyboardInterrupt:
    print("\nTest interrupted by user")
