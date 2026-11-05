
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

def diode_model_full(V, Is, n, Rs):
    Vt = kB * T / q
    a = Rs * Is / (n * Vt)
    exponent = (V + Rs * Is) / (n * Vt)
    I = (n * Vt / Rs) * lambertw(a * np.exp(exponent)) - Is
    return np.real(I)

def diode_model_full_temp(V, Is, n, Rs, T_diode):
    Vt = kB * T_diode / q
    a = Rs * Is / (n * Vt)
    exponent = (V + Rs * Is) / (n * Vt)
    I = (n * Vt / Rs) * lambertw(a * np.exp(exponent)) - Is
    return np.real(I)


def main():

    # extracting the data from the csv file
    df = extractFile("375_lab1_data.csv")
    df_calc = extractFile("375_lab1_simulation_data.csv")

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

    # Full diode model using calculated Is, n, and Rs
    Is_full = 2.973030437569094e-09
    n_full = 1.867425697874471
    Rs_full = 2.207621937224117

    # Sweep input voltage
    V_sweep = np.linspace(0, 0.8, 1000)

    # Calculate current using the full diode model
    I_sweep = diode_model_full(V_sweep, Is_full, n_full, Rs_full)

    # Plot calculated IV curve
    plt.figure()

    plt.plot(V_sweep, I_sweep * 1000, 'b-', linewidth=2,
             label="Full Diode Model")

    plt.yscale("log")
    plt.title("Calculated Semiconductor IV Curve")
    plt.xlabel("Input Voltage [V]")
    plt.ylabel("Calculated Current [mA]")

    plt.text(
        0.05, 0.95,
        f"$I_s$ = {Is_full} A\n"
        f"$n$ = {n_full}\n"
        f"$R_s$ = {Rs_full} $\\Omega$",
        transform=plt.gca().transAxes,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.8)
    )

    plt.legend()
    plt.grid()
    plt.show()

    # Compare experimental data with the full diode model
    plt.figure()

    # Experimental data
    plt.scatter(
        V_data,
        I_data * 1000,
        color='black',
        s=20,
        label="Experimental Data"
    )

    # Calculated full diode model
    plt.plot(
        V_sweep,
        I_sweep * 1000,
        color='red',
        linewidth=2,
        label="Calculated Full Diode Model"
    )

    plt.yscale("log")
    plt.title("Experimental vs. Calculated Semiconductor IV Curve")
    plt.xlabel("Input Voltage [V]")
    plt.ylabel("Current [mA]")

    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    plt.text(
        0.05, 0.95,
        f"$I_s$ = {Is_full} A\n"
        f"$n$ = {n_full}\n"
        f"$R_s$ = {Rs_full} $\\Omega$",
        transform=plt.gca().transAxes,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.8)
    )

    plt.tight_layout()
    plt.show()

    # Compare experimental data, simulation data, and full diode model

    # Extract simulation data
    V_sim = df_calc["Voltage"].to_numpy()
    I_sim = df_calc["Current mA"].to_numpy()

    plt.figure(figsize=(10, 7))

    # Experimental data
    plt.scatter(
        V_data,
        I_data * 1000,
        color='black',
        s=20,
        label="Experimental Data",
        zorder=3
    )

    # Simulation data
    plt.scatter(
        V_sim,
        I_sim,
        color='green',
        s=20,
        label="Simulation Data",
        zorder=2
    )

    # Full diode model
    plt.plot(
        V_sweep,
        I_sweep * 1000,
        color='red',
        linewidth=2,
        label="Full Diode Model",
        zorder=1
    )

    plt.yscale("log")
    plt.title("Comparison of Experimental, Simulation, and Theoretical IV Curves")
    plt.xlabel("Input Voltage [V]")
    plt.ylabel("Current [mA]")

    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    plt.text(
        0.05, 0.95,
        f"$I_s$ = {Is_full} A\n"
        f"$n$ = {n_full}\n"
        f"$R_s$ = {Rs_full} $\\Omega$",
        transform=plt.gca().transAxes,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.8)
    )

    plt.tight_layout()
    plt.show()




    # Full diode model with temperature dependence

    # Reference parameters at 300 K
    Is_300 = 2.973030437569094e-09
    n_full = 1.867425697874471
    Rs_full = 2.207621937224117

    T_ref = 300

    # Silicon intrinsic carrier concentration parameters
    Eg0 = 1.17       # eV
    alpha = 4.73e-4  # eV/K
    beta = 636       # K
    kB_eV = 8.617333262e-5  # eV/K

    # Silicon bandgap as a function of temperature
    def Eg(T):
        return Eg0 - alpha * T**2 / (T + beta)

    # Intrinsic carrier concentration ratio
    def ni_ratio(T):
        return (T / T_ref)**1.5 * np.exp(
            -Eg(T) / (2 * kB_eV * T)
            + Eg(T_ref) / (2 * kB_eV * T_ref)
        )

    # Saturation current calculated from intrinsic carrier concentration
    def Is_temperature(T):
        return Is_300 * ni_ratio(T)**2

    # Temperatures
    T1 = 375
    T2 = 250

    Is_T1 = Is_temperature(T1)
    Is_T2 = Is_temperature(T2)

    # Thermal voltages
    Vth_T1 = kB * T1 / q
    Vth_T2 = kB * T2 / q

    print("\nTemperature-dependent diode parameters")

    print(f"T1 = {T1} K")
    print(f"Is(T1) = {Is_T1} A")
    print(f"Vth(T1) = {Vth_T1} V")

    print(f"\nT2 = {T2} K")
    print(f"Is(T2) = {Is_T2} A")
    print(f"Vth(T2) = {Vth_T2} V")

    print(f"\nn = {n_full}")
    print(f"Rs = {Rs_full} Ohms")

    # Voltage sweep
    V_reverse = np.arange(-5, 0, 0.02)
    V_forward = np.arange(0, 3.0001, 0.005)

    V_sweep = np.concatenate((V_reverse, V_forward))

    # Calculate currents at both temperatures
    I_T1 = diode_model_full_temp(
        V_sweep, Is_T1, n_full, Rs_full, T1
    )

    I_T2 = diode_model_full_temp(
        V_sweep, Is_T2, n_full, Rs_full, T2
    )

    # Plot both temperature-dependent I-V characteristics
    plt.figure(figsize=(10, 7))

    plt.plot(
        V_sweep,
        I_T1 * 1000,
        color='red',
        linewidth=2,
        label=f'T = {T1} K'
    )

    plt.plot(
        V_sweep,
        I_T2 * 1000,
        color='blue',
        linewidth=2,
        label=f'T = {T2} K'
    )

    plt.title("Temperature-Dependent Semiconductor I-V Characteristics")
    plt.xlabel("Input Voltage [V]")
    plt.ylabel("Current [mA]")

    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.axhline(0, color='black', linewidth=0.8)
    plt.axvline(0, color='black', linewidth=0.8)

    plt.legend()
    plt.tight_layout()
    plt.show()

    # Logarithmic I-V plot for both temperatures

    # Remove zero-voltage point
    mask_nonzero = V_sweep != 0

    V_plot = V_sweep[mask_nonzero]
    I_T1_plot = I_T1[mask_nonzero]
    I_T2_plot = I_T2[mask_nonzero]

    # Logarithmic I-V plot
    plt.figure(figsize=(10, 7))

    plt.plot(
        V_plot,
        np.abs(I_T1_plot),
        color='red',
        linewidth=2,
        label=f'T = {T1} K'
    )

    plt.plot(
        V_plot,
        np.abs(I_T2_plot),
        color='blue',
        linewidth=2,
        label=f'T = {T2} K'
    )

    plt.yscale("log")

    plt.title("Temperature-Dependent Semiconductor I-V Characteristics")
    plt.xlabel("Voltage [V]")
    plt.ylabel("Absolute Current [A]")

    plt.xlim(-5, 3)
    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    plt.legend()
    plt.tight_layout()
    plt.show()

    # Export calculated data to CSV file

    V_export = np.linspace(0, 1, 101)

    I_export = diode_model_full(
        V_export, Is_full, n_full, Rs_full
    )

    df_export = pd.DataFrame({
        "Voltage": V_export,
        "Current mA": I_export * 1000
    })

    df_export.to_csv("375_lab1_calculated_data.csv", index=False)








main()
