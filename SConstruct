import os
import sys
import multiprocessing
from pathlib import Path
from SCons.Environment import Environment
from SCons.Script import Glob, COMMAND_LINE_TARGETS, Default, SetOption

SetOption('num_jobs', multiprocessing.cpu_count())

PROJECT_NAME = 'fceux'

# Build configurations
CONFIGS = {
    'Debug|x64': {
        'name': 'Debug_x64',
        'arch': 'x64',
        'includes': ['.', 'vc/userconfig', 'vc/defaultconfig', 'src/drivers/win/zlib', 'src/drivers/win/directx/x64', 'src', 'src/drivers/win/lua/include', 'userconfig', 'defaultconfig'],
        'defines': ['WIN32', 'WIN64', 'MSVC', '_CRT_SECURE_NO_DEPRECATE', '_WIN32_WINDOWS=0x0410', 'WINVER=0x0410', 'NETWORK', 'LSB_FIRST', 'FCEUDEF_DEBUGGER', '_USE_SHARED_MEMORY_', 'NOMINMAX', 'HAS_vsnprintf', '_S9XLUA_H', '_DEBUG'],
        'runtime': 'DebugMultiThreaded',
        'optimize': False,
        'subsystem': 'windows',
        'libs': ['comctl32.lib', 'ws2_32.lib', 'vfw32.lib', 'winmm.lib', 'htmlhelp.lib', 'psapi.lib', 'mpr.lib', 'lua51.lib', 'luaperks.lib', 'user32.lib', 'gdi32.lib', 'comdlg32.lib', 'uxtheme.lib', 'dwmapi.lib', 'advapi32.lib', 'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'shlwapi.lib', 'ddraw.lib', 'dinput.lib', 'dxguid.lib', 'winspool.lib'],
        'libpath': ['src/drivers/win/lua/x64', 'src/drivers/win/directx/x64'],
    },
    'Release|x64': {
        'name': 'Release_x64',
        'arch': 'x64',
        'includes': ['.', 'vc/userconfig', 'vc/defaultconfig', 'src/drivers/win/zlib', 'src/drivers/win/directx/x64', 'src', 'src/drivers/win/lua/include', 'userconfig', 'defaultconfig'],
        'defines': ['WIN32', 'WIN64', 'MSVC', '_CRT_SECURE_NO_DEPRECATE', '_WIN32_WINDOWS=0x0410', 'WINVER=0x0410', 'NETWORK', 'LSB_FIRST', 'FCEUDEF_DEBUGGER', '_USE_SHARED_MEMORY_', 'NOMINMAX', 'HAS_vsnprintf', '_S9XLUA_H', 'NDEBUG'],
        'runtime': 'MultiThreaded',
        'optimize': True,
        'subsystem': 'windows',
        'libs': ['comctl32.lib', 'ws2_32.lib', 'vfw32.lib', 'winmm.lib', 'htmlhelp.lib', 'psapi.lib', 'mpr.lib', 'lua51.lib', 'luaperks.lib', 'user32.lib', 'gdi32.lib', 'comdlg32.lib', 'uxtheme.lib', 'dwmapi.lib', 'advapi32.lib', 'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'shlwapi.lib', 'ddraw.lib', 'dinput.lib', 'dxguid.lib', 'winspool.lib'],
        'libpath': ['src/drivers/win/lua/x64', 'src/drivers/win/directx/x64'],
    },
}

# Map aliases to configuration keys
ALIAS_MAP = {
    'debug64': 'Debug|x64',
    'release64': 'Release|x64',
}

# Detect requested build target from command line
def get_requested_config():
    build_targets = COMMAND_LINE_TARGETS

    for target in build_targets:
        if target in ALIAS_MAP:
            return ALIAS_MAP[target]
        for cfg_key in CONFIGS:
            if target == CONFIGS[cfg_key]['name']:
                return cfg_key

    return 'Release|x64'

# Build the project
def build_project():
    cfg_key = get_requested_config()
    cfg = CONFIGS[cfg_key]

    build_env = Environment(tools=['default', 'msvc'])
    build_env['TARGET_ARCH'] = cfg['arch']

    variant_dir = f'build/{cfg["name"]}'

    source_files = []
    source_files.extend(Glob('src/boards/*.cpp'))
    source_files.extend(Glob('src/drivers/win/*.cpp'))
    source_files.extend(Glob('src/drivers/common/*.c*'))
    source_files.extend(Glob('src/input/*.cpp'))
    source_files.extend(Glob('src/utils/*.c*'))
    source_files.extend(Glob('src/lua/src/*.c*'))
    source_files.extend(Glob('src/*.cpp'))
    source_files.extend(Glob('src/drivers/win/zlib/*.c'))
    source_files.extend(Glob('src/drivers/win/taseditor/*.cpp'))
    source_files.append('src/boards/emu2413.c')

    obj_dir = f'{variant_dir}/obj'

    if cfg.get('defines'):
        build_env.Append(CCFLAGS=[f"/D{d}" for d in cfg['defines']])

    if cfg.get('includes'):
        build_env.Append(CPPPATH=cfg['includes'])

    if cfg.get('optimize'):
        build_env.Append(CCFLAGS=['/O2', '/Ob2', '/Oi', '/Ot'])
    else:
        build_env.Append(CCFLAGS=['/Od', '/RTC1', '/MTd'])

    if cfg.get('subsystem') == 'windows':
        build_env.Append(LINKFLAGS=['/SUBSYSTEM:WINDOWS'])
    else:
        build_env.Append(LINKFLAGS=['/SUBSYSTEM:CONSOLE'])

    if cfg.get('libs'):
        build_env.Append(LIBS=cfg['libs'])

    if cfg.get('libpath'):
        build_env.Append(LIBPATH=cfg['libpath'])

    target_name = f"{PROJECT_NAME}.exe" if cfg['arch'] == 'x86' else f"{PROJECT_NAME}64.exe"
    target_path = f"{variant_dir}/{target_name}"

    object_files = []
    for src in source_files:
        src_path = str(src)
        src_name = os.path.splitext(src_path)[0]
        obj = build_env.Object(target=os.path.join(obj_dir, src_name + '.obj'), source=src)
        object_files.append(obj)

    executable = build_env.Program(target=target_path, source=object_files)
    return executable

BUILD_TARGET = build_project()
Default(BUILD_TARGET)

for alias_name, cfg_key in ALIAS_MAP.items():
    Alias(alias_name, BUILD_TARGET)
