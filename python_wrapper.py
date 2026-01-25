from ctypes import cdll, c_int, c_uint8, c_uint16, c_uint32, c_char_p, byref, POINTER, create_string_buffer

dll_path = "build/DLL_x64/fceux64.dll"
dll = cdll.LoadLibrary(dll_path)

dll.add.argtypes = [c_int, c_int]
dll.add.restype = c_int

dll.run_rom.restype = c_int
dll.run_rom()