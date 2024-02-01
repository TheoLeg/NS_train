import pandas as pd
import os
import sys
import argparse

import dash
from dash import html
from dash import dash_table
from dash import dcc
import pandas as pd
import plotly.graph_objects as go

from NS_wrapper_v1 import *



def plot_series(series_list, info):

    for i, series in enumerate(series_list):
        table_id = f"series-table-{i}"
        plot_id = f"series-plot-{i}"
        color = 'green' if 'monthly' in series.name else 'red' if 'weekly' in series.name else 'blue'
        name_index_series = 'months' if 'monthly' in series.name else 'days of week' if 'daily' in series.name else ''
        name_value_series = 'amount in €' if 'money' in series.name else 'km' if 'km' in series.name else 'minutes' if 'time' in series.name else ''
        app.layout.children.append(html.Div([
            html.H2(f"Series {i+1}"),
            dash_table.DataTable(
                id=table_id,
                columns=[{"name": name_index_series, "id": "index"}, {"name": name_value_series, "id": "value"}],
                data=[{"index": index, "value": value} for index, value in series.items()],
                style_cell={'textAlign': 'center'}
            )
        ]))
        
        app.layout.children.append(html.Div([
            html.H2(f"Bar Plot of Series {i+1}"),
            dcc.Graph(
                id=plot_id,
                figure={
                    'data': [
                        go.Bar(x=series.index, y=series.values, marker_color=color)
                    ],
                    'layout': go.Layout(
                        title=f'{series.name}',
                        xaxis={'title': ''},
                        yaxis={'title': ''}
                    )
                }
            )
        ]))

    app.layout.children.append(html.Div([
    html.H3(info)    
]))



def main_():
    
    parser = argparse.ArgumentParser()

    parser.add_argument("-ns", "--data", help="your csv data path from NS website", required=True)


    args = parser.parse_args()

    path_df = args.data


    df = pd.read_csv(path_df)
    df = df.drop(['Bij', 'Transactie', 'Kl', 'Prive/ Zakelijk', 'Opmerking'], axis=1)




    pay1, pay2, pay3, months_active = get_price_overall(df)

    month1, month2, month3 = get_price_by_month(df)
    day1, day2, day3 = price_day_of_week(df)


    df_train = get_distances_df(df)
    distance1, distance2, distance3 = get_distances(df_train)

    
    most_trips = most_traveled_trips(df)
    

    time1, time2, time3 = get_times(df)
    
    time2_1, time2_2, time2_3 = get_time_by_month(df)
    time3_1, time3_2, time3_3 = time_day_of_week(df)

    series_list = [distance2, distance3, time2_1, time2_2, time2_3, time3_1, time3_2, time3_3, month1, month2, month3, day1, day2, day3]
    
    info_list = [pay1, pay2, pay3, distance1, time1, time2, time3, most_trips]
    info_list = [str(i) for i in info_list]
    info = "\n ----------- \n".join(info_list) #not ready yet so I don't display it
    info = ""

    plot_series(series_list, info)

    return None


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Tab and Graphs of your NS stats"),
])

if __name__ == "__main__":
    main_()
    app.run_server(debug=True, port=8051)

