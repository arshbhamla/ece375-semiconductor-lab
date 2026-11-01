import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


def extractFile(fileName):
    df = pd.read_csv(fileName)
    print(df)
    return df

# Physical constants
q = 1.6e-19
kB = 1.38e-23
T = 300

# Shockley diode equation
def diode_model(V, Is, n):
    return Is * np.expm1(q * V / (n * kB * T))



def main():

    #extracting the data from the csv file
    df = extractFile("375_lab1_data.csv")


    #plotting the linear IV curve
    plt.plot(df["Voltage"], df["Current mA"])
    plt.title("IV Curve")
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current [mA]")

    plt.show()

    #plotting the logarithmic IV curve
    plt.plot(df["Voltage"], np.log10(df["Current mA"]/1e-3))
    plt.title("IV Curve")
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current Log [mA]")

    plt.show()

    V_data = df["Voltage"].to_numpy()
    I_data = df["Current mA"].to_numpy() / 1000

    mask = (V_data >= 0.25) & (V_data <= 0.6) # linear region 

    V_data_lin = V_data[mask]
    I_data_lin = I_data[mask]

    initial_guess = [1e-10, 1.5]

    # Performing curve fit
    popt, pcov = curve_fit(
        diode_model,
        V_data_lin,
        I_data_lin,
        p0=initial_guess,
        bounds=([0, 0.5], [np.inf, 3]),
        maxfev=20000
    )

    Is_fit, n_fit = popt
    uncertainties = np.sqrt(np.diag(pcov))

    print(f"Is = {Is_fit} A +- {uncertainties[0]}")
    print(f"n = {n_fit} +- {uncertainties[1]}")

    V_fit = np.linspace(min(V_data), max(V_data_lin), 500)
    I_fit = diode_model(V_fit, Is_fit, n_fit)

    plt.figure()
    plt.scatter(V_data_lin, I_data_lin * 1000, label="Experimental Data")
    plt.plot(V_fit, I_fit * 1000, 'r-', label="Curve Fit")

    plt.title("Semiconductor IV Curve Fitting")
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current [mA]")
    plt.legend()
    plt.grid()
    plt.show()




main()