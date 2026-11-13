import os
import pyvisa
import time
import pandas as pd
import threading





# setup 
ktbin = r"C:\Program Files\IVI Foundation\VISA\Win64\ktvisa\ktbin"
iobin = r"C:\Program Files\Keysight\IO Libraries Suite\bin"
os.add_dll_directory(ktbin)
os.add_dll_directory(iobin)

rm = pyvisa.ResourceManager(ktbin + r"\ktvisa32.dll")

all_addresses = rm.list_resources()
print(all_addresses)





# connection parameters
def connect(addr):
    inst = rm.open_resource(addr)
    inst.timeout = 20000            # ms
    inst.read_termination = "\n"
    inst.write_termination = "\n"
    return inst




# info about connections
instrument_addresses = []
instrument_ping_response = []
instrument_names = []


for addr in all_addresses:
    try:
        inst = rm.open_resource(addr)
        instrument_addresses.append(addr)
        query = inst.query("*IDN?").strip()
        instrument_ping_response.append(query)
        id_parts = query.split(",")
        instrument_names.append(id_parts[1])
        inst.close()
    except pyvisa.errors.VisaIOError as e:
        print(f"Failed to connect to {addr}: {e}")


    


for i in range(len(instrument_addresses)):
    print("\nDevice Name: " + instrument_names[i] + "\nDevice Address: " + instrument_addresses[i] + "\n")






# device map
# this part has to be manually mapped using the device name and address provided above
multimeter = connect(instrument_addresses[0])
power_supply = connect(instrument_addresses[1])
# oscilloscope = connect(instrument_addresses[2])

print(multimeter)
print(power_supply)





# saving the data
multimeter_current_reading = []
power_supply_input_voltage = []




# break test parameter
# stop_event = threading.Event()
# def listen_for_stop():
#     while not stop_event.is_set():
#         command = input("Type 'stop' to terminate the experiment: ")

#         if command.strip().lower() == "stop":
#             stop_event.set()
#             break

# listener = threading.Thread(target=listen_for_stop, daemon=True)
# listener.start()



# test
power_supply.write(f"INST:NSEL 1")
power_supply.write(f"VOLT 0")
power_supply.write(f"CURR 0.02")

points = 200
v_max = 3.4
v_min = 2.2

for i in range(points+1):
    power_supply_voltage = i / points * (v_max - v_min) + v_min
    power_supply_input_voltage.append(power_supply_voltage)
    power_supply.write(f"VOLT {power_supply_voltage}")
    power_supply.write("OUTP ON")
    time.sleep(0.01) # in seconds
    response = multimeter.query(f"MEAS:CURR:DC?")
    multimeter_current_reading.append(response)
    print(f"{response}\n")
    power_supply.write("OUTP OFF")
    if float(response.strip()) > 2e-3:
        break
    print("\n\n")
    time.sleep(0.01)


# print("\n\n\nResults:\n")
# print(power_supply_input_voltage)
# print(multimeter_voltage_reading)


results = {
    "Input Voltage": power_supply_input_voltage,
    "Measured Voltage": multimeter_current_reading
} 

results = pd.DataFrame(results)

results.to_csv("Lab3_LEDs/lab3_output.csv", index=False)

print(results)