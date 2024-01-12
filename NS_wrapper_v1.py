import numpy as np
import pandas as pd
import datetime
import re
import os
import sys
import requests

import plotly.express as px
import calendar


def get_day_of_week(date_string):
    # Parse the date string into a datetime object
    date_object = datetime.datetime.strptime(date_string, '%d-%m-%Y')
    
    # Get the day of the week (Monday = 0, Sunday = 6)
    day_of_week = date_object.weekday()
        
    return day_of_week #return an int

def time1(t1, t2):
    t = t1 + ' - ' + t2
    datetime_format = '%d-%m-%Y - %H:%M'
    datetime_obj = datetime.datetime.strptime(t, datetime_format)
    return datetime_obj

def unique_months(l):
    unique_month = set()
    
    datetime_format = '%d-%m-%Y'
    for dt in l:
        datetime_obj = datetime.datetime.strptime(dt, datetime_format)

        year_month = (datetime_obj.year, datetime_obj.month)
        # Add the year and month to the set
        unique_month.add(year_month)

    return len(unique_month)

def del_letters(s):
    reg = '[a-zA-Z]+'
    replace = ''
    s2=re.sub(reg, replace, s)
    return s2

def time_diff(datetime_obj1, datetime_obj2):

    timedelta_diff = datetime_obj2 - datetime_obj1
    
    minutes_diff = timedelta_diff.seconds // 60
    
    return minutes_diff


def is_weekend(s):
    if s == 5 or s == 6:
        return 1
    else:
        return 0

def download_data():
    url_distances = "https://opendata.rijdendetreinen.nl/public/tariff-distances/tariff-distances-2018-04.csv"
    url_stations = "https://opendata.rijdendetreinen.nl/public/stations/stations-2022-01.csv"
    
    response_distances = requests.get(url_distances)
    response_stations = requests.get(url_stations)

    if response_distances.status_code == 200:
        distances_name = "distances.csv"
        with open(distances_name, "wb") as file:
            file.write(response_distances.content)
        df_saved = pd.read_csv(distances_name)
        print("File downloaded and loaded with pandas (saved version):")

    else:
        print("Failed to download the file.")

    if response_stations.status_code == 200:
        stations_name = "stations.csv"
        with open(stations_name, "wb") as file:
            file.write(response_stations.content)
        df_saved = pd.read_csv(stations_name)
        print("File downloaded and loaded with pandas (saved version):")

    else:
        print("Failed to download the file.")

    return pd.read_csv(distances_name), pd.read_csv(stations_name)

def get_month(s):
    reg = '-([0-9][0-9])-'
    res = re.search(reg, s).group(1)
    return int(res)

def train_or_metro(s):
    reg_train1 = 'trein'
    reg_train2 = 'studenten'
    reg_metro = 'metro'
    reg_others = ''

    if re.search(reg_train1.lower(), s.lower()) or re.search(reg_train2.lower(), s.lower()):
        return 'train'
    elif re.search(reg_metro.lower(), s.lower()):
        return 'metro'
    else:
        return 'others'
    

def clean_data(df): #build function

    
    df = df[df['Product'] != 'OV Fiets'] #removing ov_fiets for now
    df = df[~df.apply(lambda row: row.astype(str).str.contains('Onbekend').any(), axis=1)] #removing rows with unknown (=Onbekend) status

    df = df[df['Check in'].notnull()]
    df = df[df['Check uit'].notnull()]
    df = df.reset_index()
    
    same_check=np.where(df['Vertrek']==df['Bestemming'])
    df = df.drop(same_check[0], axis=0) #dropping rows where the departure and destination are the same
    
    #removing euro sign from price and change , to .
    df['Af'] = df['Af'].astype('str')
    df['Af'] = df['Af'].str.replace('€', '')
    df['Af'] = df['Af'].str.replace(',', '.')
    df['Af'] = df['Af'].astype('float')

    

    df['Check in'] = df['Check in'].apply(del_letters)
    df['Check in'] = df['Check in'].str.replace(' ', '')
    df['Check in'] = df.apply(lambda x: time1(x['Datum'], x['Check in']), axis=1)

    df['Check uit'] = df['Check uit'].apply(del_letters)
    df['Check uit'] = df['Check uit'].str.replace(' ', '')
    df['Check uit'] = df.apply(lambda x: time1(x['Datum'], x['Check uit']), axis=1)



    #creating new columns

    df['time_diff'] = df.apply(lambda x: time_diff(x['Check in'], x['Check uit']), axis=1)
    
    df['month'] = df['Datum'].apply(get_month)
    df['day_of_week'] = df['Datum'].apply(get_day_of_week)
    df['is_weekend'] = df['day_of_week'].apply(is_weekend)

    df['transport_type'] = df['Product'].apply(train_or_metro)


    return df

def plot1(df, title='', ylabel=''):
    
    fig = px.bar(df, x=df.index, y=df.values)
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title=ylabel
        )
    fig.show()


def get_indices_train_metro(df): #build function

    train = np.array(df[df['transport_type'] == 'train'].index)
    metro = np.array(df[df['transport_type'] == 'metro'].index)

    return train, metro


def get_stations_distances_info(stations, distances):
    code_station = pd.read_csv(stations)
    distances_data = pd.read_csv(distances)

    return code_station, distances_data


##################

### TIME SPENT PART
def get_times(df):
    df = clean_data(df)
    df = df.reset_index()

    total_time = df['time_diff'].sum()

    train, metro = get_indices_train_metro(df)
    
    time_in_train = df.iloc[train, :]['time_diff'].sum()
    time_in_metro = df.iloc[metro, :]['time_diff'].sum()
    
    return round(time_in_train, 2), round(time_in_metro, 2), round(total_time, 2)


def get_time_by_month(df, plot=False): #must check 
    df = clean_data(df)
    df = df.reset_index()

    train, metro = get_indices_train_metro(df)


    time_months_overall = df.groupby('month')['time_diff'].sum() #pandas series
    for i in range(1,13):
        if i not in time_months_overall.index:
            time_months_overall.loc[i] = 0
    time_months_overall = time_months_overall.sort_index()
    time_months_overall = time_months_overall.rename(lambda x: datetime.date(1900, x, 1).strftime('%B'))

    time_months_train = df.iloc[train, :].groupby('month')['time_diff'].sum() #pandas series
    for i in range(1,13):
        if i not in time_months_train.index:
            time_months_train.loc[i] = 0

    time_months_train = time_months_train.sort_index()
    time_months_train = time_months_train.rename(lambda x: datetime.date(1900, x, 1).strftime('%B'))

    time_months_metro = df.iloc[metro, :].groupby('month')['time_diff'].sum() #pandas series
    for i in range(1,13):
        if i not in time_months_metro.index:
            time_months_metro.loc[i] = 0
    
    time_months_metro = time_months_metro.sort_index()
    time_months_metro = time_months_metro.rename(lambda x: datetime.date(1900, x, 1).strftime('%B'))
    

    if plot:
        plot1(time_months_overall, ylabel='time spent (minutes)')
        plot1(time_months_train, ylabel='time spent (minutes)')
        plot1(time_months_metro, ylabel='time spent (minutes)')

    return time_months_overall, time_months_train, time_months_metro

def time_day_of_week(df):
    df = clean_data(df)
    df = df.reset_index()

    train, metro = get_indices_train_metro(df)

    time_train = df.iloc[train, :].groupby('day_of_week')['time_diff'].sum()
    time_metro = df.iloc[metro, :].groupby('day_of_week')['time_diff'].sum()
    time_total = df.groupby('day_of_week')['time_diff'].sum()

    for i in range(7):
        if i not in time_train.index:
            time_train.loc[i] = 0

    time_train = time_train.sort_index()
    time_train = time_train.rename(lambda x: datetime.date(1900, 1, x+1).strftime('%A'))
    
    for i in range(7):
        if i not in time_metro.index:
            time_metro.loc[i] = 0

    time_metro = time_metro.sort_index()

    time_metro = time_metro.rename(lambda x: datetime.date(1900, 1, x+1).strftime('%A'))
    
    for i in range(7):
        if i not in time_total.index:
            time_total.loc[i] = 0
    time_total = time_total.sort_index()
    time_total = time_total.rename(lambda x: datetime.date(1900, 1, x+1).strftime('%A'))

    return time_total, time_train, time_metro


### END TIME SPENT PART

#################


### PRICE PART
def get_price_overall(df):
    df = clean_data(df)
    df = df.reset_index()

    train, metro = get_indices_train_metro(df)

    expenses_train = df.iloc[train, :]['Af'].sum()
    expenses_metro = df.iloc[metro, :]['Af'].sum()
    expense_total = df['Af'].sum()

    months_active = unique_months(df['Datum'].values)

    return round(expenses_train, 2), round(expenses_metro, 2), round(expense_total, 2), months_active
def get_price_by_month(df, plot=False):

    df = clean_data(df)
    df = df.reset_index()

    train, metro = get_indices_train_metro(df)


    price_months_overall = df.groupby('month')['Af'].sum() #pandas series
    for i in range(1,13):
        if i not in price_months_overall.index:
            price_months_overall.loc[i] = 0
    price_months_overall = price_months_overall.sort_index()
    price_months_overall = price_months_overall.rename(lambda x: datetime.date(1900, x, 1).strftime('%B'))

    price_months_train = df.iloc[train, :].groupby('month')['Af'].sum() #pandas series
    for i in range(1,13):
        if i not in price_months_train.index:
            price_months_train.loc[i] = 0

    price_months_train = price_months_train.sort_index()
    price_months_train = price_months_train.rename(lambda x: datetime.date(1900, x, 1).strftime('%B'))

    price_months_metro = df.iloc[metro, :].groupby('month')['Af'].sum() #pandas series
    for i in range(1,13):
        if i not in price_months_metro.index:
            price_months_metro.loc[i] = 0
    
    price_months_metro = price_months_metro.sort_index()
    price_months_metro = price_months_metro.rename(lambda x: datetime.date(1900, x, 1).strftime('%B'))



    if plot:
        plot1(price_months_overall, ylabel='price (€)')
        plot1(price_months_train, ylabel='price (€)')
        plot1(price_months_metro, ylabel='price (€)')

    return price_months_overall, price_months_train, price_months_metro

def price_day_of_week(df):
    df = clean_data(df)
    df = df.reset_index()

    train, metro = get_indices_train_metro(df)

    price_train = df.iloc[train, :].groupby('day_of_week')['Af'].sum()
    price_metro = df.iloc[metro, :].groupby('day_of_week')['Af'].sum()
    price_total = df.groupby('day_of_week')['Af'].sum()

    for i in range(7):
        if i not in price_train.index:
            price_train.loc[i] = 0
    
    price_train = price_train.sort_index()
    price_train = price_train.rename(lambda x: datetime.date(1900, 1, x+1).strftime('%A'))
    
    for i in range(7):
        if i not in price_metro.index:
            price_metro.loc[i] = 0

    price_metro = price_metro.sort_index()
    price_metro = price_metro.rename(lambda x: datetime.date(1900, 1, x+1).strftime('%A'))
    
    for i in range(7):
        if i not in price_total.index:
            price_total.loc[i] = 0
    
    price_total = price_total.sort_index()
    price_total = price_total.rename(lambda x: datetime.date(1900, 1, x+1).strftime('%A'))

    return price_train, price_metro, price_total

### END PRICE PART

###################

#DISTANCES PART

def get_distances_df(df, stations_csv="stations.csv", distances_csv='distances.csv', plot=False): #build function
    df = clean_data(df)
    df = df.reset_index()

    train, _ = get_indices_train_metro(df)

    if stations_csv is not None and distances_csv is not None:
        code_station, distances_data = get_stations_distances_info(stations_csv, distances_csv)
    elif stations_csv is None and distances_csv is None:
        distances_data, code_station = download_data()
    else:
        raise ValueError("You need to provide both stations and distances csv files or none of them")
    

    trip = []

    for i in df[['Vertrek', 'Bestemming']].iloc[train].values:
        trip.append(tuple(sorted(i)))

    trip_unique = np.unique(trip, axis=0)


    list_stations = code_station[code_station['name_long'].isin(list(trip_unique.flatten()))]
    list_stations = list_stations[['code', 'name_long']]
    list_stations = list_stations.reset_index(inplace=False)
    list_stations.loc[list_stations.shape[0]] = ['302', 'LAA', 'Den Haag Laan van NOI'] #this station is name bugged in the csv file

    def get_code_station(df_stations, s):
        #print(df_stations[df_stations['name_long'] == s]['code'].values[0])
        #print('--------------', '\n')
        return df_stations[df_stations['name_long'] == s]['code'].values[0]


    trip_unique_df = pd.DataFrame(data=trip_unique, columns=['departure', 'arrival'])
    trip_unique_df['departure_code'] = trip_unique_df['departure'].apply(lambda x: get_code_station(list_stations, x))
    trip_unique_df['arrival_code'] = trip_unique_df['arrival'].apply(lambda x: get_code_station(list_stations, x))

    distances_data_clean = pd.DataFrame(data=distances_data.iloc[:,1:].values, index=distances_data.iloc[:,0].values, columns=distances_data.iloc[:,0].values)
    distances_data_clean = distances_data_clean.replace('XXX', np.nan)
    distances_data_clean = distances_data_clean.replace('?', np.nan)

    distances_data_clean = distances_data_clean.astype('float')

    trip_unique_df['distances'] = trip_unique_df.apply(lambda x: distances_data_clean.loc[x['departure_code'], x['arrival_code']], axis=1)

    df_train_temp = df.iloc[train,:]
    df_train = df_train_temp.copy()
    
    #trip_df = pd.DataFrame(data =trip , columns=['departure', 'arrival'])
    df_train['departure_code'] = df_train['Vertrek'].apply(lambda x: get_code_station(list_stations, x))
    df_train['arrival_code'] = df_train['Bestemming'].apply(lambda x: get_code_station(list_stations, x))
    
    
    df_train['trip'] = trip

    trip_unique2 = [tuple(sorted(i)) for i in trip_unique]
    trip_unique_df['trip'] = trip_unique2

    merge_df = pd.merge(df_train, trip_unique_df[['distances', 'trip']], how= 'inner',on='trip')
    distances_months = merge_df.groupby('month')['distances'].sum() #pandas series
    for i in range(1,13):
        if i not in distances_months.index:
            distances_months.loc[i] = 0
    distances_months = distances_months.sort_index()

    if plot:
        plot1(distances_months, ylabel='distance (km)')
        
    

    df_train['distances'] = df_train.apply(lambda x: distances_data_clean.loc[x['departure_code'], x['arrival_code']], axis=1)


    return df_train

def get_distances(df):

    total_distance = df['distances'].sum()

    km_by_months = df.groupby('month')['distances'].sum()

    for i in range(1,13):
        if i not in km_by_months.index:
            km_by_months.loc[i] = 0
    
    km_by_months = km_by_months.sort_index()
    km_by_months = km_by_months.rename(lambda x: datetime.date(1900, x, 1).strftime('%B'))

    km_day_of_week = df.groupby('day_of_week')['distances'].sum()

    for i in range(7):
        if i not in km_day_of_week.index:
            km_day_of_week.loc[i] = 0

    km_day_of_week = km_day_of_week.sort_index()
    km_day_of_week = km_day_of_week.rename(lambda x: datetime.date(1900, 1, x+1).strftime('%A'))

    return total_distance, km_by_months, km_day_of_week



#END DISTANCES PART


# OTHER

def most_traveled_trips(df):

    df = clean_data(df)
    df = df.reset_index()

    df_1 = df[['Vertrek', 'Bestemming']]
    df_2 = df[['Vertrek', 'Bestemming']]
    df1 = df_1.copy()
    df2 = df_2.copy()
    df1.loc[:,'trip'] = df1.apply(lambda row: ' to '.join([row['Vertrek'], row['Bestemming']]), axis=1)
    df2.loc[:,'trip'] = df2.apply(lambda row: ' - '.join(sorted([row['Vertrek'], row['Bestemming']])), axis=1)

    top_trip1 = df1.groupby('trip').size().reset_index(name='count').sort_values(by='count', ascending=False).values[:10][:]
    top_trip2 = df2.groupby('trip').size().reset_index(name='count').sort_values(by='count', ascending=False).values[:5][:]
    #top 10 and top 5 for now (could be changed)

    one_way = ''.join([f"you traveled from {trip} {count} times \n" for trip, count in top_trip1])
    two_ways = ''.join([f"you have done {trip}'s trip {count} times \n" for trip, count in top_trip2])
    
    final = 'one way count: (top10) \n' + one_way + '\nboth ways count (top 5) : \n' + two_ways
    
    return final 

#END OTHER