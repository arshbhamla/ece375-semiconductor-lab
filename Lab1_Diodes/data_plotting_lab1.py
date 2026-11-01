
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import lambertw
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
def diode_model1(V, Is, n):
    return Is * np.expm1(q * V / (n * kB * T))

def diode_model2(V, Rs):
    # hard coding the values found from the other best fit curve in
    # V_app = I*R_s + n*Vth*ln(I / I_s + 1)

    Is_fit = 2.9730303629345866e-09
    n_fit = 1.8674256942817924
    Vt = kB * T / q
    a = Rs * Is_fit / (n_fit * Vt)
    exponent = (V + Rs * Is_fit) / (n_fit * Vt)
    I = (n_fit * Vt / Rs) * lambertw(a * np.exp(exponent)) - Is_fit
    return np.real(I)



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
    initial_guess = [1e-9, 1.5]

    # performing curve fit
    popt, pcov = curve_fit(
        diode_model1,
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
    I_fit = diode_model1(V_fit, Is_fit, n_fit)

    # calculate predicted current at experimental voltage points
    I_predicted = diode_model1(V_data_lin, Is_fit, n_fit)

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

    
    # V_app = I*R_s + n*Vth*ln(I / I_s + 1)
    initial_guess_Rs = [1]

    # disregards the bottom bad part of the data
    mask = V_data > 0.4
    V_data_r = V_data[mask]
    I_data_r = I_data[mask]

    popt_Rs, pcov_Rs = curve_fit(
        diode_model2,
        V_data_r,
        I_data_r,
        p0=initial_guess_Rs,
        bounds=([0.001], [1000]),
        maxfev=20000
    )

    Rs_fit = popt_Rs[0]
    Rs_uncertainty = np.sqrt(np.diag(pcov_Rs))[0]

    print(f"Rs = {Rs_fit} Ohms +- {Rs_uncertainty}")

    # calculate predicted current using fitted Rs
    I_predicted_Rs = diode_model2(V_data_r, Rs_fit)

    # calculate logarithmic R^2 for Rs fit
    valid_Rs = (I_data_r > 0) & (I_predicted_Rs > 0)

    I_data_log_Rs = np.log10(I_data_r[valid_Rs])
    I_predicted_log_Rs = np.log10(I_predicted_Rs[valid_Rs])

    R2_Rs = r2_score(I_data_log_Rs, I_predicted_log_Rs)

    print(f"Logarithmic R^2 for Rs fit = {R2_Rs}")

    # plot experimental data and Rs curve fit
    V_fit_Rs = np.linspace(min(V_data_r), max(V_data_r), 500)
    I_fit_Rs = diode_model2(V_fit_Rs, Rs_fit)

    plt.figure()
    plt.scatter(V_data_r, I_data_r * 1000, label="Experimental Data")
    plt.plot(V_fit_Rs, I_fit_Rs * 1000, 'r-', label="Rs Curve Fit")

    plt.yscale("log")
    plt.title("Semiconductor IV Curve Fitting with Series Resistance")
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current [mA]")

    plt.text(
        0.05, 0.95,
        f"$R_s$ = {Rs_fit} $\\Omega$\n"
        f"$R^2$ = {R2_Rs}",
        transform=plt.gca().transAxes,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.8)
    )

    plt.legend()
    plt.grid()
    plt.show()


main()
