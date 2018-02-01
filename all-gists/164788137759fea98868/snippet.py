#!/usr/bin/python

import sys
import os
import glob
import subprocess
import getopt

def parse_project_option(keys, value, target):
    key = keys.pop(0)

    if(len(keys) >= 1): # still more than one element in list
        if(not target.has_key(key)):
            target[key] = {}
        parse_project_option(keys, value, target[key])
    else:
        target[key] = value

def print_help():
    print("Usage: " + sys.argv[0] + " [--cpp] [-d|--debug] [-r|--relative] Project_Directory")
    sys.exit()

def make_path(path):
	if use_relative_paths:
		return path[len(project_directory)+1:]
	else:
		return path

has_cpp = False
has_debug = False
use_relative_paths = False
use_11 = False

opts, args = getopt.getopt(sys.argv[1:],"hp:dr",["cpp", "debug", "relative", "use11"])

if len(args) < 1:
    print_help();

for opt, arg in opts:
    if opt == "-h":
        print_help()
    elif opt == "--cpp":
        has_cpp = True
    elif opt == "--debug" or opt == "-d":
        has_debug = True
    elif opt == "--relative" or opt == "-r":
        use_relative_paths = True
    elif opt == "use11":
        use_11 = True
    else:
        print opt, "=", arg

project_directory = os.path.abspath(args[0])

if (not os.path.exists(project_directory)):
    sys.exit("Project directory " + project_directory + " does not exist!")

eoc_file = glob.glob(os.path.join(project_directory, "*.ioc"))
if(len(eoc_file) == 0):
    sys.exit("Unable to find project file (*.ioc)")

eoc_file = eoc_file[0]

project_settings = {}

with open(eoc_file, 'r') as fh:
    for line in fh:
        data = line.strip().split("=")
        if(len(data) != 2):
            continue

        [key, value] = data
        parse_project_option(key.split('.'), value, project_settings)
    fh.close()

processor = project_settings['Mcu']['UserName']
processor_line = processor[:7] # STM32FX
processor_family = processor[:9] # STM32FXXX

print "Generating Makefile for Project Directory", project_directory, " Processor: ", processor, "(", processor_line, "/", processor_family, ")"

process = subprocess.Popen(['arm-none-eabi-gcc', '--print-sysroot'], stdout=subprocess.PIPE)
process.wait()
if (not process.returncode == 0):
    sys.exit("arm-none-eabi-gcc not found! Please add it to your PATH.")

compiler_root = os.path.abspath(process.communicate()[0].strip())
print("arm-none-eabi-gcc sysroot at " + compiler_root)

# Buffer for targets to write to Makefile
targets = ""
filename = os.path.join(project_directory, "Makefile")

#""" + ('g++' if has_cpp else 'gcc') +"""

with open(filename, 'w+') as fh:
    # write header
    fh.write("""#
# Automatically generated - Do not change!
#
CC=arm-none-eabi-gcc
CXX=arm-none-eabi-g++
LD=arm-none-eabi-lc
AS=arm-none-eabi-as
OBJ=arm-none-eabi-objcopy
COMPILER_SYSROOT=$(shell $(CC) -print-sysroot)
SEP="""+("\\\\" if os.sep == "\\" else os.sep)+"""
# -g3
CFLAGS="""+('-g ' if has_debug else '')+('-std=c11 ' if use_11 else '')+"""-mcpu=cortex-m3 -mthumb -mfloat-abi=soft -DUSE_HAL_DRIVER -D"""+processor_family+"""xx -Wall -fmessage-length=0 -ffunction-sections
CXXFLAGS="""+('-g ' if has_debug else '')+('-std=c++11 ' if use_11 else '')+"""-mcpu=cortex-m3 -mthumb -mfloat-abi=soft -DUSE_HAL_DRIVER -D"""+processor_family+"""xx -Wall -fmessage-length=0 -ffunction-sections
LFLAGS="""+('-g ' if has_debug else '')+"""-mcpu=cortex-m3 -mthumb -mfloat-abi=soft -specs=nosys.specs -specs=nano.specs -Wl,-Map=output.map -Wl,--gc-sections -lm
LIBS=
CFLAGS += -I\"$(COMPILER_SYSROOT)$(SEP)include\"
CXXFLAGS += -I\"$(COMPILER_SYSROOT)$(SEP)include\"
""")

# \"""" + os.path.join(compiler_root, "include") + """\"

    fh.write("BUILD_DIR="+make_path(os.path.join(project_directory, "build"))+"\n")

    if (os.name == "nt"):
        fh.write("SHELL=C:/Windows/System32/cmd.exe\n")
        fh.write("RM=del /S\n")
    else:
        fh.write("RM=rm -rf\n")

    fh.write("""USER_DIR="""+make_path(os.path.join(project_directory, "User"))+"""
-include $(USER_DIR)/Makefile
""");

    path_drivers = os.path.join(project_directory, "Drivers")
    path_hal = os.path.join(path_drivers, "*HAL_Driver")
    path_cmsis = os.path.join(path_drivers, "CMSIS")
    path_cmsis_device = os.path.join(path_cmsis, "Device", "ST", processor_line + "xx")

    path_src = os.path.join(project_directory, "Src")
    path_cmsis_src = os.path.join(path_cmsis, "Src")
    path_hal_src = os.path.join(path_hal, "Src")
    path_cmsis_device_source = os.path.join(path_cmsis_device, "Source")
    path_cmsis_device_templates = os.path.join(path_cmsis_device_source, "Templates")

    path_inc = os.path.join(project_directory, "Inc")
    path_cmsis_include = os.path.join(path_cmsis, "Include")
    path_hal_inc = os.path.join(path_hal, "Inc")
    path_cmsis_device_include = os.path.join(path_cmsis_device, "Include")
    path_configuration = os.path.join(project_directory, "SW4STM32", "*Configuration")
    # path_startup = os.path.join()

    source_files = []
    header_files = []
    include_paths = set()
    objects = []
    source_files += glob.glob(os.path.join(path_src, "*.c")) # "Src" + os.pathsep + "*.c"
    source_files += glob.glob(os.path.join(path_hal_src, "*.c")) # project_directory + "Drivers" + os.pathsep + "*HAL_Driver" + os.pathsep + "Src" + os.pathsep + "*.c"
    source_files += glob.glob(os.path.join(path_cmsis_device_source, "*.c")) # project_directory + "Drivers" + os.pathsep + "CMSIS" + os.pathsep + "Device" + os.pathsep + "ST" + os.pathsep +processor_family+"xx" + os.pathsep + "Source" + os.pathsep + "*.c"
    source_files += glob.glob(path_cmsis_src) # project_directory + "Drivers" + os.pathsep + "CMSIS" + os.pathsep + "Source" + os.pathsep + "*.c"
    source_files += glob.glob(os.path.join(path_cmsis_device_templates, "*.c")) # project_directory + "Drivers" + os.pathsep + "CMSIS" + os.pathsep + "Device" + os.pathsep + "ST" + os.pathsep + ""+processor_family+"xx" + os.pathsep + "Source" + os.pathsep + "Templates" + os.pathsep + "system_stm32*.c"

    for f in glob.glob(os.path.join(path_hal_src, "*_template.c")):
        source_files.remove(f)

    header_files += glob.glob(os.path.join(path_inc, "*.h")) # project_directory + "Inc" + os.pathsep + "*.h"
    header_files += glob.glob(os.path.join(path_hal_inc, "*.h")) # project_directory + "Drivers" + os.pathsep + "*HAL_Driver" + os.pathsep + "Inc" + os.pathsep + "*.h"
    header_files += glob.glob(os.path.join(path_cmsis_device_include, "*.h")) # project_directory + "Drivers" + os.pathsep + "CMSIS" + os.pathsep + "Device" + os.pathsep + "ST" + os.pathsep + ""+processor_family+"xx" + os.pathsep + "Include" + os.pathsep + "*.h"
    header_files += glob.glob(os.path.join(path_cmsis_include, "*.h")) # project_directory + "Drivers" + os.pathsep + "CMSIS" + os.pathsep + "Include" + os.pathsep + "*.h"
    header_files += glob.glob(os.path.join(path_cmsis_device_include, "system_stm32*.h")) # project_directory + "Drivers" + os.pathsep + "CMSIS" + os.pathsep + "Device" + os.pathsep + "ST" + os.pathsep + ""+processor_family+"xx" + os.pathsep + "Include" + os.pathsep + "system_stm32*.h"

    linker_files = glob.glob(os.path.join(path_configuration, "*.ld"))
    for linker_file in linker_files:
        fh.write("LFLAGS+= -T\""+make_path(linker_file)+"\"\n")

    for header_file in header_files:
        include_paths.add(make_path(os.path.dirname(header_file)))

    for p in source_files:
        f = os.path.basename(p)
        object_name = (f[:-2]) + ".o"
        objects += ["$(BUILD_DIR)/"+object_name]
        targets += "$(BUILD_DIR)/"+object_name + ": " + make_path(p) + "\n" + "\t$(CC) $(CFLAGS) -o $@ -c $<" + "\n\n"

    startup_files = glob.glob(os.path.join(path_cmsis_device_templates, "gcc", "startup_"+processor_family.lower()+"xx.s"))
    if (not len(startup_files) == 1):
	    print "WARNING: No startup file found!"
    else:
        objects += ["$(BUILD_DIR)/startup.o"]
        targets += "$(BUILD_DIR)/startup.o : " + make_path(startup_files[0]) + "\n" + "\t" + "$(AS) -mcpu=cortex-m3 -mthumb -mfloat-abi=soft -o $@ $<\n\n"

    targets += "all: $(BUILD_DIR)/project.bin\n\techo \"Making all\"\n\n"

    targets += "$(BUILD_DIR)/project.elf: $(OBJECTS)\n" + "\t" + "$("+('CXX' if has_cpp else 'CC')+") $(LFLAGS) -o $@ $+\n\n"

    targets += "$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf\n" + "\t" + "$(OBJ) -O binary $< $@\n\n"

    targets += "%.upload: %.bin\n" + "\t" + "st-flash --reset write $< 0x08000000\n\n"

    if (os.name == "nt"):
        targets += "clean:\n\t$(RM) $(BUILD_DIR)$(SEP)*.o $(BUILD_DIR)$(SEP)*.elf $(BUILD_DIR)$(SEP)*.bin"
    else:
        targets += "clean:\n\t$(RM) $(BUILD_DIR)$(SEP)*.o $(BUILD_DIR)$(SEP)*.elf $(BUILD_DIR)$(SEP)*.bin"

    for path in include_paths:
        fh.write("CFLAGS+=-I\""+path+"\"\n")
        fh.write("CXXFLAGS+=-I\""+path+"\"\n")

    fh.write("OBJECTS+="+" ".join(objects)+"\n")

    fh.write("""$(OBJECTS) : | $(BUILD_DIR)

$(BUILD_DIR):
\tmkdir -p $(BUILD_DIR)

""")

    fh.write(targets)

    fh.close()

print("Done.")
