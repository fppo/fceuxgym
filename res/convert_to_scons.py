#!/usr/bin/env python3
"""
VCXPROJ to SCons Converter
Converts Visual Studio .vcxproj files to SCons build system.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import argparse


class VCXProjParser:
    """Parser for Visual Studio project files."""
    
    MSBUILD_NS = {'ms': 'http://schemas.microsoft.com/developer/msbuild/2003'}
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.project_dir = self.project_path.parent
        self.tree = ET.parse(self.project_path)
        self.root = self.tree.getroot()
        
        self.configurations: Dict[str, Dict] = {}
        self.source_files: List[Dict] = []
        self.header_files: List[str] = []
        self.resource_files: List[str] = []
        self.custom_build_files: List[Dict] = []
        self.none_files: List[str] = []
        
    def get_text(self, element: Optional[ET.Element], tag: str) -> str:
        """Get text from an element with namespace."""
        if element is None:
            return ''
        ns_tag = f"ms:{tag}"
        child = element.find(ns_tag, self.MSBUILD_NS)
        if child is None:
            child = element.find(tag)
        return child.text if child is not None else ''
    
    def get_all_text(self, element: Optional[ET.Element], tag: str) -> List[str]:
        """Get all text from elements with specific tag."""
        if element is None:
            return []
        ns_tag = f"ms:{tag}"
        children = element.findall(ns_tag, self.MSBUILD_NS)
        if not children:
            children = element.findall(tag)
        return [child.text.strip() for child in children if child.text]
    
    def parse_configurations(self):
        """Parse project configurations."""
        configs = self.root.find("ms:ItemGroup[@Label='ProjectConfigurations']", self.MSBUILD_NS)
        if configs is None:
            configs = self.root.find("ItemGroup[@Label='ProjectConfigurations']")
        
        for config in configs:
            config_name = config.get('Include')
            config_type = config.find('ms:Configuration', self.MSBUILD_NS)
            if config_type is None:
                config_type = config.find('Configuration')
            platform = config.find('ms:Platform', self.MSBUILD_NS)
            if platform is None:
                platform = config.find('Platform')
            
            if config_type is not None and platform is not None:
                cfg_key = f"{config_type.text}|{platform.text}"
                self.configurations[cfg_key] = {
                    'configuration': config_type.text,
                    'platform': platform.text,
                    'properties': {}
                }
    
    def parse_properties(self):
        """Parse configuration properties."""
        for cfg_key, cfg_data in self.configurations.items():
            config = cfg_data['configuration']
            platform = cfg_data['platform']
            condition = f"'$(Configuration)|$(Platform)'=='Debug|Win32'"
            
            property_group = self.root.find(f"ms:PropertyGroup[@Label='Configuration']", self.MSBUILD_NS)
            if property_group is None:
                property_group = self.root.find("PropertyGroup[@Label='Configuration']")
            
            if property_group is not None:
                cfg_data['properties']['ConfigurationType'] = self.get_text(property_group, 'ConfigurationType')
    
    def parse_item_definitions(self):
        """Parse ItemDefinitionGroup elements for each configuration."""
        for item_def in self.root.findall("ms:ItemDefinitionGroup", self.MSBUILD_NS):
            condition = item_def.get('Condition', '')
            cfg_key = condition.replace("'$(Configuration)|$(Platform)'=='", "").strip("'")
            
            if cfg_key in self.configurations:
                cfg_data = self.configurations[cfg_key]
                
                cl_compile = item_def.find('ms:ClCompile', self.MSBUILD_NS)
                if cl_compile is None:
                    cl_compile = item_def.find('ClCompile')
                
                if cl_compile is not None:
                    cfg_data['clcompile'] = {
                        'additional_include_directories': self.get_text(cl_compile, 'AdditionalIncludeDirectories'),
                        'preprocessor_definitions': self.get_text(cl_compile, 'PreprocessorDefinitions'),
                        'runtime_library': self.get_text(cl_compile, 'RuntimeLibrary'),
                        'optimization': self.get_text(cl_compile, 'Optimization'),
                        'warning_level': self.get_text(cl_compile, 'WarningLevel'),
                        'debug_information_format': self.get_text(cl_compile, 'DebugInformationFormat'),
                    }
                
                link = item_def.find('ms:Link', self.MSBUILD_NS)
                if link is None:
                    link = item_def.find('Link')
                
                if link is not None:
                    cfg_data['link'] = {
                        'additional_dependencies': self.get_text(link, 'AdditionalDependencies'),
                        'sub_system': self.get_text(link, 'SubSystem'),
                        'entry_point_symbol': self.get_text(link, 'EntryPointSymbol'),
                        'target_machine': self.get_text(link, 'TargetMachine'),
                    }
                
                pre_build = item_def.find('ms:PreBuildEvent', self.MSBUILD_NS)
                if pre_build is None:
                    pre_build = item_def.find('PreBuildEvent')
                
                if pre_build is not None:
                    cfg_data['prebuild'] = {
                        'command': self.get_text(pre_build, 'Command')
                    }
                
                post_build = item_def.find('ms:PostBuildEvent', self.MSBUILD_NS)
                if post_build is None:
                    post_build = item_def.find('PostBuildEvent')
                
                if post_build is not None:
                    cfg_data['postbuild'] = {
                        'command': self.get_text(post_build, 'Command')
                    }
    
    def parse_source_files(self):
        """Parse source files (ClCompile items)."""
        for compile_group in self.root.findall("ms:ItemGroup", self.MSBUILD_NS):
            for item in compile_group:
                if item.tag.endswith('ClCompile') or item.tag == 'ClCompile':
                    include = item.get('Include')
                    if include:
                        file_info = {
                            'path': include,
                            'excluded_from_build': False,
                            'compile_as': None,
                            'object_filename': None,
                            'disable_specific_warnings': []
                        }
                        
                        for child in item:
                            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                            if tag == 'ExcludedFromBuild':
                                file_info['excluded_from_build'] = child.text.lower() == 'true'
                            elif tag == 'CompileAs':
                                file_info['compile_as'] = child.text
                            elif tag == 'ObjectFileName':
                                file_info['object_filename'] = child.text
                            elif tag == 'DisableSpecificWarnings':
                                file_info['disable_specific_warnings'] = child.text.split(';')
                        
                        if not file_info['excluded_from_build']:
                            self.source_files.append(file_info)
    
    def parse_header_files(self):
        """Parse header files (ClInclude items)."""
        for include_group in self.root.findall("ms:ItemGroup", self.MSBUILD_NS):
            for item in include_group:
                if item.tag.endswith('ClInclude') or item.tag == 'ClInclude':
                    include = item.get('Include')
                    if include and not self._is_excluded(include, item):
                        self.header_files.append(include)
    
    def parse_resource_files(self):
        """Parse resource files."""
        for resource_group in self.root.findall("ms:ItemGroup", self.MSBUILD_NS):
            for item in resource_group:
                if item.tag.endswith('ResourceCompile') or item.tag == 'ResourceCompile':
                    include = item.get('Include')
                    if include:
                        self.resource_files.append(include)
    
    def parse_custom_build(self):
        """Parse custom build items."""
        for item_group in self.root.findall("ms:ItemGroup", self.MSBUILD_NS):
            for item in item_group:
                if item.tag.endswith('CustomBuild') or item.tag == 'CustomBuild':
                    include = item.get('Include')
                    if include:
                        commands = []
                        for child in item:
                            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                            if tag == 'Command':
                                commands.append(child.text)
                        
                        self.custom_build_files.append({
                            'file': include,
                            'commands': commands
                        })
    
    def _is_excluded(self, include: str, item: ET.Element) -> bool:
        """Check if file is excluded from build."""
        for child in item:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag == 'ExcludedFromBuild':
                return child.text.lower() == 'true'
        return False
    
    def parse(self):
        """Parse all project information."""
        self.parse_configurations()
        self.parse_properties()
        self.parse_item_definitions()
        self.parse_source_files()
        self.parse_header_files()
        self.parse_resource_files()
        self.parse_custom_build()
        
        return self


class SConsGenerator:
    """Generator for SCons build files."""
    
    def __init__(self, parser: VCXProjParser):
        self.parser = parser
        self.sconstruct_content = []
    
    def _escape_path(self, path: str) -> str:
        """Escape path for Python/SCons."""
        path = path.replace('\\', '/')
        path = path.replace('"', '\\"')
        return path
    
    def _clean_msbuild_vars(self, text: str) -> str:
        """Remove or replace MSBuild-specific variables."""
        if not text:
            return text
        text = re.sub(r'%\([^)]+\)', '', text)
        text = text.replace(';;', ';')
        text = text.strip(';')
        return text
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path separators."""
        path = path.replace('\\', '/')
        path = path.replace('..\\', '../')
        return path
    
    def generate(self):
        """Generate SConstruct content."""
        self._generate_header()
        self._generate_environments()
        self._generate_source_files()
        self._generate_build_targets()
        self._generate_post_build()
        
        return '\n'.join(self.sconstruct_content)
    
    def _generate_header(self):
        """Generate file header."""
        self.sconstruct_content.append('#!/usr/bin/env python3')
        self.sconstruct_content.append("'''")
        self.sconstruct_content.append(f'SCons build script for {self.parser.project_path.stem}')
        self.sconstruct_content.append('Generated from Visual Studio project')
        self.sconstruct_content.append("'''")
        self.sconstruct_content.append('')
        self.sconstruct_content.append('import os')
        self.sconstruct_content.append('import sys')
        self.sconstruct_content.append('from pathlib import Path')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('# Ensure we\'re using MSVC on Windows')
        self.sconstruct_content.append('env = Environment(tools=[\'msvc\'])')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('# Project settings')
        self.sconstruct_content.append("PROJECT_NAME = 'fceux'")
        self.sconstruct_content.append('')
    
    def _generate_environments(self):
        """Generate environment configurations."""
        self.sconstruct_content.append('# Build configurations')
        self.sconstruct_content.append("CONFIGS = {")
        
        for cfg_key, cfg_data in self.parser.configurations.items():
            config = cfg_data['configuration']
            platform = cfg_data['platform']
            platform_arch = 'x86' if platform == 'Win32' else 'x64'
            
            self.sconstruct_content.append(f"    '{cfg_key}': {{")
            self.sconstruct_content.append(f"        'name': '{config}_{platform}',")
            self.sconstruct_content.append(f"        'arch': '{platform_arch}',")
            
            if 'clcompile' in cfg_data:
                cl = cfg_data['clcompile']
                
                if cl.get('additional_include_directories'):
                    inc_dirs = self._clean_msbuild_vars(cl['additional_include_directories'])
                    if inc_dirs:
                        inc_dirs = inc_dirs.replace(';', "', '")
                        self.sconstruct_content.append(f"        'includes': ['{inc_dirs}'],")
                
                if cl.get('preprocessor_definitions'):
                    defs = self._clean_msbuild_vars(cl['preprocessor_definitions'])
                    if defs:
                        defs = defs.replace(';', "', '")
                        self.sconstruct_content.append(f"        'defines': ['{defs}'],")
                
                if cl.get('runtime_library'):
                    rt_lib = cl['runtime_library']
                    if 'MultiThreadedDebug' in rt_lib:
                        self.sconstruct_content.append("        'runtime': 'DebugMultiThreaded',")
                    elif 'MultiThreaded' in rt_lib:
                        self.sconstruct_content.append("        'runtime': 'MultiThreaded',")
                
                if cl.get('optimization'):
                    opt = cl['optimization']
                    if opt == 'Disabled':
                        self.sconstruct_content.append("        'optimize': False,")
                    elif opt == 'Full':
                        self.sconstruct_content.append("        'optimize': True,")
            
            if 'link' in cfg_data:
                link = cfg_data['link']
                
                if link.get('sub_system'):
                    subsys = link['sub_system']
                    if subsys == 'Windows':
                        self.sconstruct_content.append("        'subsystem': 'windows',")
                    elif subsys == 'Console':
                        self.sconstruct_content.append("        'subsystem': 'console',")
                
                if link.get('additional_dependencies'):
                    deps = link['additional_dependencies'].split(';')
                    libs = [d for d in deps if d and not d.startswith('../') and not d.startswith('%')]
                    if libs:
                        self.sconstruct_content.append(f"        'libs': {libs},")
            
            if 'prebuild' in cfg_data:
                cmd = cfg_data['prebuild'].get('command', '')
                if cmd:
                    cmd = self._clean_msbuild_vars(cmd)
                    cmd_escaped = cmd.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '; ')
                    self.sconstruct_content.append(f"        'prebuild_cmd': r\"{cmd_escaped}\",")
            
            if 'postbuild' in cfg_data:
                cmd = cfg_data['postbuild'].get('command', '')
                if cmd:
                    cmd = self._clean_msbuild_vars(cmd)
                    cmd_escaped = cmd.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '; ')
                    self.sconstruct_content.append(f"        'postbuild_cmd': r\"{cmd_escaped}\",")
            
            self.sconstruct_content.append("    },")
        
        self.sconstruct_content.append('}')
        self.sconstruct_content.append('')
    
    def _generate_source_files(self):
        """Generate source file list using glob patterns."""
        self.sconstruct_content.append('# Source files using glob patterns')
        self.sconstruct_content.append("SOURCES = {")
        
        patterns = [
            ('boards', '../src/boards/*.cpp'),
            ('drivers_win', '../src/drivers/win/*.cpp'),
            ('drivers_common', '../src/drivers/common/*.c*'),
            ('input', '../src/input/*.cpp'),
            ('utils', '../src/utils/*.c*'),
            ('core', '../src/*.cpp'),
            ('zlib', '../src/drivers/win/zlib/*.c'),
            ('taseditor', '../src/drivers/win/taseditor/*.cpp'),
        ]
        
        for group, pattern in patterns:
             self.sconstruct_content.append(f"    '{group}': Glob('{pattern}'),")
        
        self.sconstruct_content.append('}')
        self.sconstruct_content.append('')
    
    def _generate_build_targets(self):
        """Generate build targets."""
        self.sconstruct_content.append('# Build targets for each configuration')
        self.sconstruct_content.append('def get_build_targets():')
        self.sconstruct_content.append('    targets = {}')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('    for cfg_key, cfg in CONFIGS.items():')
        self.sconstruct_content.append('        env = DefaultEnvironment().Clone()')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        # Configure environment')
        self.sconstruct_content.append("        env['TARGET_ARCH'] = cfg['arch']")
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        # Set output directory for this configuration')
        self.sconstruct_content.append("        cfg_name = cfg['name']")
        self.sconstruct_content.append("        variant_dir = f'build/{cfg_name}'")
        self.sconstruct_content.append("        env.VariantDir(variant_dir, '../src', duplicate=0)")
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        # Get all source files')
        self.sconstruct_content.append('        all_sources = []')
        self.sconstruct_content.append('        for group, files in SOURCES.items():')
        self.sconstruct_content.append('            all_sources.extend(files)')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        # Compiler flags')
        self.sconstruct_content.append('        if cfg.get(\'defines\'):')
        self.sconstruct_content.append('            env.Append(CCFLAGS=[f"/D{d}" for d in cfg[\'defines\']])')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        if cfg.get(\'includes\'):')
        self.sconstruct_content.append('            env.Append(CPPPATH=cfg[\'includes\'])')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        if cfg.get(\'optimize\'):')
        self.sconstruct_content.append('            env.Append(CCFLAGS=[')
        self.sconstruct_content.append("                '/O2',")
        self.sconstruct_content.append("                '/Ob2',")
        self.sconstruct_content.append("                '/Oi',")
        self.sconstruct_content.append("                '/Ot',")
        self.sconstruct_content.append("            ])")
        self.sconstruct_content.append('        else:')
        self.sconstruct_content.append("            env.Append(CCFLAGS=['/Od'])")
        self.sconstruct_content.append("            env.Append(CCFLAGS=['/RTC1', '/MTd'])")
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        # Subsystem')
        self.sconstruct_content.append('        if cfg.get(\'subsystem\'):')
        self.sconstruct_content.append('            if cfg[\'subsystem\'] == \'windows\':')
        self.sconstruct_content.append("                env.Append(LINKFLAGS=['/SUBSYSTEM:WINDOWS'])")
        self.sconstruct_content.append('            else:')
        self.sconstruct_content.append("                env.Append(LINKFLAGS=['/SUBSYSTEM:CONSOLE'])")
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        # Libraries')
        self.sconstruct_content.append('        if cfg.get(\'libs\'):')
        self.sconstruct_content.append('            env.Append(LIBS=cfg[\'libs\'])')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        # Build executable with variant directory')
        self.sconstruct_content.append('        target_name = f"{PROJECT_NAME}.exe" if cfg[\'arch\'] == \'x86\' else f"{PROJECT_NAME}64.exe"')
        self.sconstruct_content.append('        executable = env.Program(target=target_name, source=all_sources, variant_dir=variant_dir)')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        # Pre-build command')
        self.sconstruct_content.append('        if cfg.get(\'prebuild_cmd\'):')
        self.sconstruct_content.append('            env.Command(')
        self.sconstruct_content.append('                target=env.File(\'dummy\'),')
        self.sconstruct_content.append('                source=[],')
        self.sconstruct_content.append('                action=cfg[\'prebuild_cmd\']')
        self.sconstruct_content.append('            )')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        # Post-build command')
        self.sconstruct_content.append('        if cfg.get(\'postbuild_cmd\'):')
        self.sconstruct_content.append('            env.AddPostAction(executable, cfg[\'postbuild_cmd\'])')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('        targets[cfg_key] = executable')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('    return targets')
        self.sconstruct_content.append('')
    
    def _generate_post_build(self):
        """Generate post-build operations."""
        self.sconstruct_content.append('# Build all targets')
        self.sconstruct_content.append('BUILD_TARGETS = get_build_targets()')
        self.sconstruct_content.append('')
        self.sconstruct_content.append('# Aliases for common builds')
        self.sconstruct_content.append("Alias('debug', BUILD_TARGETS.get('Debug|Win32'))")
        self.sconstruct_content.append("Alias('release', BUILD_TARGETS.get('Release|Win32'))")
        self.sconstruct_content.append("Alias('debug64', BUILD_TARGETS.get('Debug|x64'))")
        self.sconstruct_content.append("Alias('release64', BUILD_TARGETS.get('Release|x64'))")
        self.sconstruct_content.append("Alias('publicrelease', BUILD_TARGETS.get('PublicRelease|Win32'))")
        self.sconstruct_content.append("Alias('publicrelease64', BUILD_TARGETS.get('PublicRelease|x64'))")
        self.sconstruct_content.append('')
        self.sconstruct_content.append('# Default target')
        self.sconstruct_content.append("Default(BUILD_TARGETS.get('Debug|Win32'))")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Convert Visual Studio project to SCons')
    parser.add_argument('project_file', nargs='?', default='vc/vc14_fceux.vcxproj',
                        help='Path to .vcxproj file')
    parser.add_argument('-o', '--output', default='SConstruct',
                        help='Output file name (default: SConstruct)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.project_file):
        print(f"Error: Project file not found: {args.project_file}")
        sys.exit(1)
    
    print(f"Parsing: {args.project_file}")
    
    vcxproj = VCXProjParser(args.project_file)
    vcxproj.parse()
    
    print(f"Found {len(vcxproj.configurations)} configurations")
    print(f"Found {len(vcxproj.source_files)} source files")
    print(f"Found {len(vcxproj.header_files)} header files")
    print(f"Found {len(vcxproj.resource_files)} resource files")
    
    generator = SConsGenerator(vcxproj)
    sconstruct_content = generator.generate()
    
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sconstruct_content)
    
    print(f"Generated: {output_path}")
    print("\nTo build:")
    print("  scons                    # Default build (Debug|Win32)")
    print("  scons debug              # Debug build")
    print("  scons release            # Release build")
    print("  scons debug64            # Debug x64 build")
    print("  scons release64          # Release x64 build")
    print("  scons -c                 # Clean")


if __name__ == '__main__':
    main()
