import numpy as np
import pandas as pd
import datetime
import re
import os
import sys
import argparse
import calendar


from NS_wrapper_v1 import *


def main_():
    
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



   # const_sub = input("add amount of money you pay per month for your subscription : ")
   # except_months = input("add number of months where you didn't pay for your subscription (0 if you paid every months) : ")

    pay1, pay2, pay3, months_active = get_price_overall(df)
    #sub = float(const_sub) * (months_active - float(except_months))

    month1, month2, month3, plot1 = get_price_by_month(df)
    day1, day2, day3, plot2 = price_day_of_week(df)


    df_train = get_distances_df(df)
    distance1, distance2, distance3, plot3 = get_distances(df_train)

    
    most_trips = most_traveled_trips(df)
    

    time1, time2, time3 = get_times(df)
    
    time2_1, time2_2, time2_3, plot4 = get_time_by_month(df)
    time3_1, time3_2, time3_3, plot5 = time_day_of_week(df)

    return [plot1, plot2, plot3, plot4, plot5, most_trips, pay1, pay2, pay3, distance1, distance2, distance3, time1, time2, time3, time2_1, time2_2, time2_3, time3_1, time3_2, time3_3, month1, month2, month3, day1, day2, day3]


