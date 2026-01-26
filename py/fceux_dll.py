from ctypes import cdll, c_int, c_uint8, c_char_p, byref, POINTER
import numpy as np



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

        self.dll.save_state_to_memory.argtypes = [POINTER(c_uint8), c_int]
        self.dll.save_state_to_memory.restype = c_int

        self.dll.load_state_from_memory.argtypes = [POINTER(c_uint8), c_int]
        self.dll.load_state_from_memory.restype = c_int

        self.dll.load_rom.argtypes = [c_char_p]
        self.dll.load_rom.restype = c_char_p

        self.dll.reset.argtypes = []
        self.dll.reset.restype = c_int

        self.dll.save_state_lz4.argtypes = [POINTER(c_uint8), c_int]
        self.dll.save_state_lz4.restype = c_int

        self.dll.load_state_lz4.argtypes = [POINTER(c_uint8), c_int]
        self.dll.load_state_lz4.restype = c_int

        self.dll.load_config.argtypes = [c_char_p]
        self.dll.load_config.restype = c_int
        
    # 运行指定ROM文件，初始化模拟器
    def run_rom(self, rom_path):
        if isinstance(rom_path, str):
            rom_path = rom_path.encode('utf-8')
        return self.dll.run_rom(rom_path)
    
    # 清理模拟器，关闭当前ROM
    def close_rom(self):
        return self.dll.close_rom()

    # 加载ROM文件
    def load_rom(self, filename=None):
        if filename is not None:
            if isinstance(filename, str):
                filename = filename.encode('utf-8')
        result = self.dll.load_rom(filename)
        if result:
            return result.decode('utf-8')
        return None
    
    # 重置游戏
    def reset(self):
        return self.dll.reset()

    # 读取内存 0x800 字节
    def read_memory(self):
        return self.dll.read_memory()

    # 隐藏窗口
    def hide_window(self):
        return self.dll.hide_window()

    # 显示窗口
    def show_window(self):
        return self.dll.show_window()

    # 获取屏幕图像，未上色，索引组成
    def read_screen(self):
        ret = self.dll.read_screen()
        if ret:
            screen_np = np.ctypeslib.as_array(ret, shape=(224, 256))
            mask = (screen_np >= 128) & (screen_np <= 195)
            screen_np[~mask] = 0
            screen_np = (screen_np - 128) * 2
            return screen_np
        return None

    # 大于0时执行指定帧数，图形不渲染到窗口，小于0时，执行1帧，图形渲染到窗口
    def step_frame(self, frames):
        return self.dll.step_frame(frames)

    # 保存存档
    def save_state(self, filename):
        if isinstance(filename, str):
            filename = filename.encode('utf-8')
        return self.dll.save_state(filename)

    # 加载存档
    def load_state(self, filename):
        if isinstance(filename, str):
            filename = filename.encode('utf-8')
        return self.dll.load_state(filename)

    # 设置输入 port 0-3, input_value 0-255
    def set_input(self, port, input_value):
        return self.dll.set_input(port, input_value)

    # 清除输入
    def clear_input(self):
        return self.dll.clear_input()
    
    # 获取PPU滚轴坐标
    def get_scroll(self):
        scroll_x = c_int()
        scroll_y = c_int()
        result = self.dll.get_scroll(byref(scroll_x), byref(scroll_y))
        if result == 0:
            return scroll_x.value, scroll_y.value
        return None, None
    
    # 保存未压缩的存档
    def save_state_to_memory(self):
        size = 1024 * 200
        buffer = (c_uint8 * size)()
        result = self.dll.save_state_to_memory(buffer, size)
        if result == 0:
            return None
        return np.frombuffer(buffer, dtype=np.uint8)[:result].copy()
    
    # 加载未压缩的存档
    def load_state_from_memory(self, data):
        if data is None or len(data) == 0:
            return -1
        data = np.ascontiguousarray(data, dtype=np.uint8)
        buffer = data.ctypes.data_as(POINTER(c_uint8))
        size = len(data)
        return self.dll.load_state_from_memory(buffer, size)
    
    # LZ4压缩的存档，compressionLevel越大压缩越快
    def save_state_lz4(self, compressionLevel=1):
        size = 1024 * 200
        buffer = (c_uint8 * size)()
        result = self.dll.save_state_lz4(buffer, size, compressionLevel)
        if result == 0:
            return None
        return np.frombuffer(buffer, dtype=np.uint8)[:result].copy()
    
    # 读取LZ4压缩的存档
    def load_state_lz4(self, data):
        if data is None or len(data) == 0:
            return -1
        data = np.ascontiguousarray(data, dtype=np.uint8)
        buffer = data.ctypes.data_as(POINTER(c_uint8))
        size = len(data)
        return self.dll.load_state_lz4(buffer, size)
    
    # 加载FCEUX配置文件
    def load_config(self, filename):
        if isinstance(filename, str):
            filename = filename.encode('utf-8')
        return self.dll.load_config(filename)
