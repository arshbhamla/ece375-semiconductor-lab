import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score


def extractFile(fileName):
    df = pd.read_csv(fileName)
    print(df)
    return df

# constants
q = 1.6e-19
kB = 1.38e-23
T = 300

# diode equation
def diode_model(V, Is, n):
    return Is * np.expm1(q * V / (n * kB * T))



def main():

    # extracting the data from the csv file
    df = extractFile("375_lab1_data.csv")


    # plotting the linear IV curve
    plt.plot(df["Voltage"], df["Current mA"])
    plt.title("IV Curve")
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current [mA]")

    plt.show()

    # plotting the logarithmic IV curve

    mask_positive = df["Current mA"] > 0

    V_positive = df["Voltage"][mask_positive]
    I_positive = df["Current mA"][mask_positive]

    plt.plot(V_positive, I_positive*1e-3)
    plt.title("IV Curve")
    plt.yscale("log")
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current Log [A]")

    plt.show()

    # curve fitting changed to numpy
    V_data = df["Voltage"].to_numpy()
    I_data = df["Current mA"].to_numpy() / 1000

    # use only the linear region
    mask = (V_data >= 0.4) & (V_data <= 0.65) 
    V_data_lin = V_data[mask]
    I_data_lin = I_data[mask]

    # set up my initial guesses
    initial_guess = [1e-10, 1.5]

    # performing curve fit
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

    V_fit = np.linspace(min(V_data_lin), max(V_data_lin), 500)
    I_fit = diode_model(V_fit, Is_fit, n_fit)

    # calculate predicted current at experimental voltage points
    I_predicted = diode_model(V_data_lin, Is_fit, n_fit)

    # calculate R^2 using logarithmic current values
    valid = (I_data_lin > 0) & (I_predicted > 0)

    I_data_log = np.log10(I_data_lin[valid])
    I_predicted_log = np.log10(I_predicted[valid])

    R2 = r2_score(I_data_log, I_predicted_log)
    print(f"Logarithmic R^2 = {R2}\n")

    plt.figure()
    plt.scatter(V_data_lin, I_data_lin * 1000, label="Experimental Data")
    plt.plot(V_fit, I_fit * 1000, 'r-', label="Curve Fit")

    plt.yscale("log")
    plt.title("Semiconductor IV Curve Fitting")
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current [mA]")
    plt.legend()
    plt.grid()
    plt.show()

    



main()
