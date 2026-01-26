from ctypes import cdll, c_int, c_uint8, c_char_p, byref, POINTER
import os


class FCEuxDLL:
    def __init__(self, dll_path="build/DLL_x64/fceux64.dll"):
        self.dll = cdll.LoadLibrary(dll_path)
        self._setup_function_signatures()
        
    def __del__(self):
        self.close_rom()
        
    def _setup_function_signatures(self):
        self.dll.run_rom.argtypes = [c_char_p]
        self.dll.run_rom.restype = c_int

        self.dll.close_rom.argtypes = []
        self.dll.close_rom.restype = c_int

        self.dll.read_memory.argtypes = []
        self.dll.read_memory.restype = POINTER(c_uint8)

        self.dll.hide_window.argtypes = []
        self.dll.hide_window.restype = c_int

        self.dll.show_window.argtypes = []
        self.dll.show_window.restype = c_int

        self.dll.read_screen.argtypes = []
        self.dll.read_screen.restype = POINTER(c_uint8)

        self.dll.step_frame.argtypes = [c_int]
        self.dll.step_frame.restype = c_int

        self.dll.save_state.argtypes = [c_char_p]
        self.dll.save_state.restype = c_int

        self.dll.load_state.argtypes = [c_char_p]
        self.dll.load_state.restype = c_int

        self.dll.set_input.argtypes = [c_int, c_uint8]
        self.dll.set_input.restype = c_int

        self.dll.clear_input.argtypes = []
        self.dll.clear_input.restype = c_int

        self.dll.get_scroll.argtypes = [POINTER(c_int), POINTER(c_int)]
        self.dll.get_scroll.restype = c_int

    def run_rom(self, rom_path):
        if isinstance(rom_path, str):
            rom_path = rom_path.encode('utf-8')
        return self.dll.run_rom(rom_path)
    
    def close_rom(self):
        return self.dll.close_rom()

    def read_memory(self):
        return self.dll.read_memory()

    def hide_window(self):
        return self.dll.hide_window()

    def show_window(self):
        return self.dll.show_window()

    def read_screen(self):
        return self.dll.read_screen()

    def step_frame(self, frames):
        return self.dll.step_frame(frames)

    def save_state(self, filename):
        if isinstance(filename, str):
            filename = filename.encode('utf-8')
        return self.dll.save_state(filename)

    def load_state(self, filename):
        if isinstance(filename, str):
            filename = filename.encode('utf-8')
        return self.dll.load_state(filename)

    def set_input(self, port, input_value):
        return self.dll.set_input(port, input_value)

    def clear_input(self):
        return self.dll.clear_input()

    def get_scroll(self):
        scroll_x = c_int()
        scroll_y = c_int()
        result = self.dll.get_scroll(byref(scroll_x), byref(scroll_y))
        if result == 0:
            return scroll_x.value, scroll_y.value
        return None, None
