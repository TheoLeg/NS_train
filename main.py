import numpy as np
import pandas as pd
import datetime
import re
import os
import sys
import argparse
import calendar


from NS_wrapper_v1 import *



# Create the argument parser
parser = argparse.ArgumentParser()

# Add the arguments with shortcuts
parser.add_argument("-ns", "--data", help="your csv data path from NS website", required=True)
parser.add_argument("-d", "--distances", help="distances csv informations", required=False)
parser.add_argument("-s", "--stations", help="stations codes csv", required=False)

# Parse the command-line arguments
args = parser.parse_args()

# Access the values of the arguments
path_df = args.data
path_distances_csv = args.distances
path_stations_codes = args.stations



df = pd.read_csv(path_df)
df = df.drop(['Bij', 'Transactie', 'Kl', 'Prive/ Zakelijk', 'Opmerking'], axis=1)


print("Please choose something you want to know about your travel informations: \n")
print("1. view expenses informations")
print("2. view km traveled informations")
print("3. view time spent informations")
print("q to Quit")

user_input = input()

while True:

    if user_input == '1':
        const_sub = input("add amount of money you pay per month for your subscription : ")
        except_months = input("add number of months where you didn't pay for your subscription (0 if you paid every months) : ")
        print("Your overall expense : \n")
        train_overall, metro_overall, total_overall, months_active = get_price_overall(df)
        sub = float(const_sub) * (months_active - float(except_months))

        print(f"You spent {train_overall}€ in trains, {metro_overall}€ in metro/bus/tram. {round(sub, 2)}€ in subscriptions {round(total_overall+sub, 2)}€ in total", "\n")
        print("--------------")
        print("\n")
        print("expenses without subscriptions : \n")
        print("expense by month : ", "\n")
        price_monts_df = get_price_by_month(df)
        print(f"{price_monts_df}", "\n")

        print("expense by day of week : ", "\n")
        print(f"{price_day_of_week(df)}", "\n")
    
        print("--------------")
        print("1. view expenses informations")
        print("2. view km traveled informations")
        print("3. view time spent informations")
        print("q to Quit")
        user_input = input()

    if  user_input == '2':
        print("Your overall distance traveled : \n")
        df_train = get_distances_df(df)
        total_overall, months, day_of_week = get_distances(df_train)

        print(f"{total_overall} km \n {months} \n {day_of_week}")
        print('--------------')
        print(most_traveled_trips(df))
        print("--------------")
        print("1. view expenses informations")
        print("2. view km traveled informations")
        print("3. view time spent informations")
        print("q to Quit")
        user_input = input()


    if user_input == '3':
        print("Your overall time spent : \n")
        train_overall, metro_overall, total_overall = get_times(df)
        print(f"You spent {train_overall} minutes in trains, {metro_overall} minutes in metro/bus/tram. {total_overall} minutes in total", "\n")

        print("time spent by month : ", "\n")
        time_monts_df = get_time_by_month(df)
        print(f"{time_monts_df}", "\n")

        print("time spent by day of week : ", "\n")
        print(f"{time_day_of_week(df)}", "\n")
        
        print("--------------")
        print("1. view expenses informations")
        print("2. view km traveled informations")
        print("3. view time spent informations")
        print("q to Quit")
        user_input = input()

    if user_input.lower() == 'q':
        sys.exit(0)

    else:
        print("wrong input")
        print("Please choose something you want to know about your travel informations: \n")
        print("1. view expenses informations")
        print("2. view km traveled informations")
        print("3. view time spent informations")
        print("q to Quit \n")
        user_input = input()



"""
- average spending time in train per day of week and per month
- average spending time in metro per day / week / months
- average expense per month  OK kinda
- most traveled trip (one and two ways) OK

- add constants from subscriptions for price functions
"""


