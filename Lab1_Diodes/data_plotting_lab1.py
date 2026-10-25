import pandas as pd
import os
import matplotlib.pyplot as plt

def main():
    df = pd.read_csv("375_lab1_data.csv")
    print(df)

    

    plt.plot(df["Voltage"], df["Current mA"])
    plt.title("IV Curve")
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current [mA]")


    plt.show()



main()