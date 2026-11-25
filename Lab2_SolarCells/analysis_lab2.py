import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.special import lambertw
from sklearn.metrics import r2_score
from scipy.integrate import quad


raw_data = "375_lab2_raw_data.csv"
T = 300
q = 1.6e-19
k = 1.381e-23

def solar_cell_model(v_app, i_gen, i_s, n, R_s, T):
    v_app = np.asarray(v_app, dtype=float)
    i_gen_A = i_gen / 1000
    i_s_A = i_s / 1000
    a = q / (n * k * T)
    exponent = a * (
        v_app + R_s * (i_gen_A + i_s_A)
    )
    z = (
        a * R_s * i_s_A
        * np.exp(exponent)
    )
    I_A = (
        i_gen_A + i_s_A
        - np.real(lambertw(z)) / (a * R_s)
    )
    return I_A * 1000

def blackbody_radiation(wavelength, temp):
    h = 6.62607015e-34 # planck's constant
    c = 3e8 # speed of light
    kb = 1.380649e-23

    return 2*h*c**2 / wavelength**5 * (1/(np.exp(h*c/(wavelength*kb*temp))-1))

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

    n_guess = 1.5
    i_gen_guess = isc
    R_s_guess = 1.0
    i_s_guess = i_gen_guess / (np.exp(q*voc/(n_guess*k*T))-1)
    print(f"The I_sat guess is {i_s_guess}")

    popt, pcov = curve_fit(
        lambda V, Iph, Is, n, Rs:
            solar_cell_model(V, Iph, Is, n, Rs, T),
        lab_data_V,
        lab_data_I,
        p0=[i_gen_guess, i_s_guess, n_guess, R_s_guess],
        bounds=(
            [0, 1e-15, 1, 1e-9],
            [100, 1e-2, 2, 100]
        ),
        maxfev=100000
    )

    Iph_fit, Is_fit, n_fit, Rs_fit = popt

    print(f"\nPhotocurrent: {round(Iph_fit,3)} mA")
    print(f"Saturation Current: {round(Is_fit*1e6,3)} nA")
    print(f"Ideality Factor: {round(n_fit,3)}")
    print(f"Series Resistance: {round(Rs_fit,3)} Ohms")


    V_data = lab_data_V.to_numpy()
    I_data = lab_data_I.to_numpy()
    V_fit = np.linspace(min(V_data), max(V_data), 500)

    I_fit = solar_cell_model(
        V_fit,
        Iph_fit,
        Is_fit,
        n_fit,
        Rs_fit,
        T
    )

    I_predicted = solar_cell_model( # using this for the R^2 calculation
        V_data,
        Iph_fit,
        Is_fit,
        n_fit,
        Rs_fit,
        T
    )

    r_squared = r2_score(I_data, I_predicted)

    print(f"\nR-squared: {r_squared}")

    diode_sim_location = "375_lab2_spice_simulated_data.csv"
    diode_sim_data = df_from_csv(diode_sim_location)
    # print(diode_sim_data)
    diode_sim_data_V = diode_sim_data["V1"]
    diode_sim_data_I = diode_sim_data["I(V1)"] * 1e3

    # plt.figure()

    # plt.scatter(
    #     V_data,
    #     I_data,
    #     color='blue',
    #     label='Experimental Data',
    #     zorder=3
    # )

    # plt.plot(
    #     V_fit,
    #     I_fit,
    #     color='red',
    #     linewidth=2,
    #     label='Calculated Model'
    # )

    # plt.plot(
    #     diode_sim_data_V.to_numpy(),
    #     diode_sim_data_I.to_numpy(),
    #     color='green',
    #     linewidth=2,
    #     label='Spice Model'
    # )

    # plt.xlabel("Voltage [V]")
    # plt.ylabel("Current [mA]")
    # plt.title("Solar Cell I-V Curve: Experimental vs Fitted")
    # plt.legend()
    # plt.grid(True, alpha=0.3)

    # plt.show()

    temp = 5800 # surface of the sun
    lower_lim = 420e-9
    upper_lim = 1000e-9
    sigma = 5.670374419e-8

    total_5800 = sigma * temp**4 / np.pi

    visible_5800, error = quad(blackbody_radiation, lower_lim, upper_lim, args=(temp,))

    efficiency_5800 = (visible_5800 / total_5800) * 100
    print(f"Efficiency 5800 of {efficiency_5800}")

    temp = 7200
    
    visible_7200, error = quad(blackbody_radiation, lower_lim, upper_lim, args=(temp,))

    total_7200 = sigma * temp**4 / np.pi

    efficiency_7200 = (visible_7200 / total_7200) * 100
    print(f"Efficiency 7200 of {efficiency_7200}")





main()