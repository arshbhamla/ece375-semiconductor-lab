import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
    plt.show()

def main():
    blue_LED_data = df_from_csv(blue_LED_location)
    green_LED_data = df_from_csv(green_LED_location)
    red_LED_data = df_from_csv(red_LED_location)

    print(green_LED_data)

main()