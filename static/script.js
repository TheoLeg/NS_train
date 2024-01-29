// Fetch the data from the server
fetch('/data')
  .then(response => response.json())
  .then(data => {
    // Access the data and generate the graphs
    const graph1Data = data.graph1Data;
    const graph2Data = data.graph2Data;
    const graph3Data = data.graph3Data;
    const graph4Data = data.graph4Data;
    const graph5Data = data.graph5Data;

    // Generate Plotly graphs
    Plotly.newPlot('graph1', graph1Data);
    Plotly.newPlot('graph2', graph2Data);
    Plotly.newPlot('graph3', graph3Data);
    Plotly.newPlot('graph4', graph4Data);
    Plotly.newPlot('graph5', graph5Data);


    // Access and display other information
    const info = data.info;
    document.getElementById('info').innerText = info;
  });