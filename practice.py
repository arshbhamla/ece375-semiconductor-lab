import os
import glob
import pyvisa

bin_dir = r"C:\Program Files\Keysight\IO Libraries Suite\bin"

print(glob.glob(bin_dir + r"\*visa*.dll"))
print(glob.glob(r"C:\Windows\System32\*visa*.dll"))

os.add_dll_directory(bin_dir)

dll = r"C:\Windows\System32\ktvisa64.dll"
rm = pyvisa.ResourceManager(dll)
print(rm)
print(rm.list_resources())