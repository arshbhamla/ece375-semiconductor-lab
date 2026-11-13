import os, pyvisa

ktbin = r"C:\Program Files\IVI Foundation\VISA\Win64\ktvisa\ktbin"
iobin = r"C:\Program Files\Keysight\IO Libraries Suite\bin"

os.add_dll_directory(ktbin)
os.add_dll_directory(iobin)

rm = pyvisa.ResourceManager(ktbin + r"\ktvisa32.dll")
print(rm)
print(rm.list_resources())

