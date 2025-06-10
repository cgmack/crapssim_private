from flask import Flask, jsonify
from crapssim.analytics import generate_strategy_performance_summary, generate_strategy_risk_profile, fetch_simulation_data, generate_hedging_impact_and_usage, generate_comprehensive_strategy_comparison
from crapssim.db_utils import get_db_connection

app = Flask(__name__)

@app.route('/api/strategy-performance', methods=['GET'])
def strategy_performance():
    sim_data = fetch_simulation_data()
    df = generate_strategy_performance_summary(sim_data)
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/risk-profile', methods=['GET'])
def risk_profile():
    sim_data = fetch_simulation_data()
    df = generate_strategy_risk_profile(sim_data)
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/bankroll-trajectory', methods=['GET'])
def bankroll_trajectory():
    sim_data = fetch_simulation_data()
    # The 'rolls' DataFrame from fetch_simulation_data contains the necessary data for bankroll trajectory.
    # We can directly return this.
    df = sim_data['rolls']
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/hedging-impact', methods=['GET'])
def hedging_impact():
    sim_data = fetch_simulation_data()
    df = generate_hedging_impact_and_usage(sim_data)
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/comprehensive-comparison', methods=['GET'])
def comprehensive_comparison():
    sim_data = fetch_simulation_data()
    df = generate_comprehensive_strategy_comparison(sim_data)
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)