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

def led_model(Vapp, n, Is):
    kb = 1.38e-23
    q = 1.602e-19
    T = 300
    Vth = kb*T/q
    return Is*(np.exp(Vapp/n/Vth)-1)

def led_curve_fitting(model, dataframe):
    voltage = dataframe["Input Voltage"]
    current = dataframe["Measured Current"]
    return curve_fit(
        model, 
        voltage, 
        current, 
        p0=[1, 1e-20],
        bounds=([1, 1e-30], [2, 1e-5]),
        maxfev=200000
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

    print(f"Blue parameters:\n"
          f"n = {round(popt_blue[0],6)}\n"
          f"Is = {round(popt_blue[1]*1e15,6)}fA\n"
          )

    print(f"Green parameters:\n"
              f"n = {round(popt_green[0],6)}\n"
              f"Is = {round(popt_green[1]*1e15,6)}fA\n"
              )

    print(f"Red parameters:\n"
                  f"n = {round(popt_red[0],6)}\n"
                  f"Is = {round(popt_red[1]*1e15,6)}fA\n"
                  )


main()