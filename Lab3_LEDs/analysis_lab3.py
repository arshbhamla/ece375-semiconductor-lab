
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

blue_LED_location = "lab3_output_blueLED_csv.csv"
green_LED_location = "lab3_output_greenLED_csv.csv"
red_LED_location = "lab3_output_redLED_csv.csv"

def df_from_csv(file_location):
    return pd.read_csv(file_location)

def iv_curve_plot(dataframe, title):
    voltage = dataframe["Input Voltage"]
    current = dataframe["Measured Current"]
    plt.figure()
    plt.plot(voltage, current*1e3)
    plt.title(f"IV Curve: {title}")
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current [mA]")

def two_iv_curves(dataframe1, dataframe2, title):
    voltage = dataframe1["Input Voltage"]
    current1 = dataframe1["Measured Current"]
    current2 = dataframe2["Calculated Current"]
    plt.figure()
    plt.plot(voltage, current1*1e3, 'r', label="Measured Current")
    plt.plot(voltage, current2*1e3, 'b', label="Calculated Current")
    plt.title(f"IV Curve: {title}")
    plt.legend()
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current [mA]")

def led_model(Vapp, n, log_Is):
    kb = 1.38e-23
    q = 1.602e-19
    T = 300
    Vth = kb*T/q
    Is = np.exp(log_Is)
    return Is*(np.exp(Vapp/n/Vth)-1)

def led_curve_fitting(model, dataframe):
    # no weights
    voltage = dataframe["Input Voltage"]
    current = dataframe["Measured Current"]
    return curve_fit(
        model, 
        voltage, 
        current, 
        p0=[1, np.log(1e-25)],
        bounds=([1, np.log(1e-30)], [2, np.log(1e-5)]),
        maxfev=2000000
    )

def main():
    blue_LED_data = df_from_csv(blue_LED_location)
    green_LED_data = df_from_csv(green_LED_location)
    red_LED_data = df_from_csv(red_LED_location)

    # data plotting
    # iv_curve_plot(blue_LED_data, "Blue LED")
    # iv_curve_plot(green_LED_data, "Green LED")
    # iv_curve_plot(red_LED_data, "Red LED")
    # plt.show()

    # curve fitting
    popt_blue, pcov_blue = led_curve_fitting(led_model, blue_LED_data)
    popt_green, pcov_green = led_curve_fitting(led_model, green_LED_data)
    popt_red, pcov_red = led_curve_fitting(led_model, red_LED_data)

    print(f"\nBlue parameters:\n"
        f"n = {round(popt_blue[0],6)}\n"
        f"Is = {round(np.exp(popt_blue[1])*1e26,6)} x 1e-26 A\n"
        )
    print(f"Green parameters:\n"
        f"n = {round(popt_green[0],6)}\n"
        f"Is = {round(np.exp(popt_green[1])*1e27,6)} x 1e-27 A\n"
        )
    print(f"Red parameters:\n"
        f"n = {round(popt_red[0],6)}\n"
        f"Is = {round(np.exp(popt_red[1])*1e21,6)} x 1e-21 A\n"
        )

     # plotting measured vs calculated
    blue_LED_data["Calculated Current"] = led_model(
        blue_LED_data["Input Voltage"], *popt_blue
    )
    two_iv_curves(blue_LED_data, blue_LED_data, "Blue LED")

    green_LED_data["Calculated Current"] = led_model(
        green_LED_data["Input Voltage"], *popt_green
    )
    two_iv_curves(green_LED_data, green_LED_data, "Green LED")

    red_LED_data["Calculated Current"] = led_model(
        red_LED_data["Input Voltage"], *popt_red
    )
    two_iv_curves(red_LED_data, red_LED_data, "Red LED")

    # calculate R^2 values
    r2_blue = r2_score(
        blue_LED_data["Measured Current"],
        blue_LED_data["Calculated Current"]
    )
    r2_green = r2_score(
        green_LED_data["Measured Current"],
        green_LED_data["Calculated Current"]
    )
    r2_red = r2_score(
        red_LED_data["Measured Current"],
        red_LED_data["Calculated Current"]
    )

    print(f"\nR^2 Blue LED: {round(r2_blue,4)}")
    print(f"R^2 Green LED: {round(r2_green,4)}")
    print(f"R^2 Red LED: {round(r2_red,4)}")

    plt.show()

    # Eg calculations
    # energy_blue = 4.14e-15*3e8/(455e-9)
    # print(energy_blue)
    # energy_green = 4.14e-15*3e8/(520e-9)
    # print(energy_green)
    # energy_red = 4.14e-15*3e8/(630e-9)
    # print(energy_red)




main()
