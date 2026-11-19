import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

raw_data = "375_lab2_raw_data.csv"

def df_from_csv(file_location):
    return pd.read_csv(file_location)

def main():
    lab_data = df_from_csv(raw_data)
    # print(lab_data)
    voc =  0.562 # V
    isc = 24.85 # mA 

    lab_data["P [mW]"] = lab_data["V [V]"] * lab_data["I [mA]"]
    print(f"\n{lab_data}")

    lab_data_R = lab_data["R [Ohm]"]
    lab_data_I = lab_data["I [mA]"]
    lab_data_V = lab_data["V [V]"]
    lab_data_P = lab_data["P [mW]"]

    # print(lab_data_R)
    # print(lab_data_I)
    # print(lab_data_V)

    # plt.figure()
    # plt.plot(lab_data_V, lab_data_I)
    # plt.title("Voltage vs Current Graph Solar Cell")
    # plt.xlabel("Voltage [V]")
    # plt.ylabel("Current [mA]")

    # plt.figure()
    # plt.plot(lab_data_V, lab_data_P)
    # plt.title("Voltage vs Power")
    # plt.xlabel("Voltage [V]")
    # plt.ylabel("Power [mW]")
    # plt.show()

    max_power = 0
    vmp = 0
    imp = 0
    for i in range(len(lab_data)):
        test_power = lab_data_P.iloc[i]
        if(test_power > max_power):
            max_power = test_power
            vmp = lab_data_V.iloc[i]
            imp = lab_data_I.iloc[i]

    ff = vmp * imp / (voc * isc)

    print(f"\n\nMax power is {max_power}mW\nMP voltage is {vmp}V\nMP current is {imp}mA\nField factor is {round(ff, 4)}")

    conversion_efficiency = 0.17
    P_in = isc * voc * ff / conversion_efficiency
    print(f"The input power is {round(P_in, 3)}mW")

    


main()