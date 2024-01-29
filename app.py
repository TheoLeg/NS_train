from flask import Flask, render_template, jsonify
import plotly.graph_objects as go
from main import main_
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Generate your graphs and retrieve information here
    list_main = main_()
    graph1_data = list_main[0]
    graph2_data = list_main[1]
    graph3_data = list_main[2]
    graph4_data = list_main[3]
    graph5_data = list_main[4]
    info = [str(i) for i in list_main[5:]]

    fig_json1 = graph1_data.to_json()
    fig_json2 = graph2_data.to_json()
    fig_json3 = graph3_data.to_json()
    fig_json4 = graph4_data.to_json()
    fig_json5 = graph5_data.to_json()


    return jsonify({'fig1': fig_json1, 'fig2': fig_json2, 'fig3': fig_json3, 
                    'fig4': fig_json4, 'fig5': fig_json5, 'info': info})

if __name__ == '__main__':
    app.run()