import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

raw_data = "375_lab2_raw_data.csv"
T = 300
q = 1.6e-19
k = 1.381e-23

def solar_cell_model(v_app, i_gen, i_s, n, T):
    return i_gen - i_s * (np.exp(q * v_app / (n * k * T)) - 1)

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

    n_guess = 1
    i_gen_guess = isc
    i_s_guess = 1e-9

    popt, pcov = curve_fit(
    lambda V, Iph, Is, n: solar_cell_model(V, Iph, Is, n, T),
    lab_data_V,
    lab_data_I,
    p0=[i_gen_guess, i_s_guess, n_guess],
    bounds=([0, 0, 1], [100, 1e-2, 1.75]),
    maxfev=50000
    )

    Iph_fit, Is_fit, n_fit = popt

    print(f"\nPhotocurrent: {round(Iph_fit,3)} mA")
    print(f"Saturation Current: {round(Is_fit*10e3, 3)} uA")
    print(f"Ideality Factor: {round(n_fit, 3)}")



main()