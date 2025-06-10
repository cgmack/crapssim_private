import React from 'react';
import Plot from 'react-plotly.js';

function App() {
  // Example data for a simple bar chart
  const data = [
    {
      x: ['Strategy A', 'Strategy B', 'Strategy C'],
      y: [10, 15, 7],
      type: 'bar',
      name: 'Avg. Net Profit/Loss'
    }
  ];

  const layout = {
    title: 'Strategy Performance Summary (Example)',
    xaxis: { title: 'Strategy' },
    yaxis: { title: 'Amount ($)' }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>CrapsSim Analytics Dashboard</h1>
      </header>
      <div className="dashboard-content">
        <Plot
          data={data}
          layout={layout}
        />
        {/* More components and plots will go here */}
      </div>
    </div>
  );
}

export default App;