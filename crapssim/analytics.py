import pandas as pd
import psycopg2
import uuid
from psycopg2 import sql 
from crapssim.db_utils import get_db_connection

def fetch_simulation_data(simulation_id: str = None) -> dict:
    """
    Fetches raw simulation data from the PostgreSQL database.

    Parameters
    ----------
    simulation_id : str, optional
        If provided, fetches data for a specific simulation.
        Otherwise, fetches all data.

    Returns
    -------
    dict
        A dictionary containing pandas DataFrames for 'simulations', 'sessions',
        'rolls', and 'bets' tables.
    """
    conn = None
    try:
        conn = get_db_connection()
        query_simulations = "SELECT * FROM simulations"
        query_sessions = "SELECT * FROM sessions"
        query_rolls = "SELECT * FROM rolls"
        query_bets = "SELECT * FROM bets"

        if simulation_id:
            query_simulations += f" WHERE simulation_id = '{simulation_id}'"
            query_sessions += f" WHERE simulation_id = '{simulation_id}'"
            query_rolls += f" WHERE simulation_id = '{simulation_id}'"
            query_bets += f" WHERE simulation_id = '{simulation_id}'"

        simulations_df = pd.read_sql(query_simulations, conn)
        sessions_df = pd.read_sql(query_sessions, conn)
        rolls_df = pd.read_sql(query_rolls, conn)
        bets_df = pd.read_sql(query_bets, conn)

        return {
            "simulations": simulations_df,
            "sessions": sessions_df,
            "rolls": rolls_df,
            "bets": bets_df
        }
    except Exception as e:
        print(f"Error fetching data from database: {e}")
        return {
            "simulations": pd.DataFrame(),
            "sessions": pd.DataFrame(),
            "rolls": pd.DataFrame(),
            "bets": pd.DataFrame()
        }
    finally:
        if conn:
            conn.close()

def calculate_avg_net_profit_loss_per_session(sessions_df: pd.DataFrame) -> float:
    """
    Calculates the average net profit/loss per session.
    """
    if sessions_df.empty:
        return 0.0
    return sessions_df['net_profit_loss_session'].mean()

def calculate_empirical_ev_per_dollar_risked(sessions_df: pd.DataFrame) -> float:
    """
    Calculates the empirical Expected Value (EV) per dollar risked.
    """
    if sessions_df.empty or sessions_df['total_dollars_risked_in_session'].sum() == 0:
        return 0.0
    total_profit_loss = sessions_df['net_profit_loss_session'].sum()
    total_dollars_risked = sessions_df['total_dollars_risked_in_session'].sum()
    return total_profit_loss / total_dollars_risked

def calculate_win_loss_push_rates(sessions_df: pd.DataFrame) -> dict:
    """
    Calculates the win, loss, and push rates of sessions.
    """
    if sessions_df.empty:
        return {"Win_Rate_Percentage": 0.0, "Loss_Rate_Percentage": 0.0, "Push_Rate_Percentage": 0.0}

    total_sessions = len(sessions_df)
    win_sessions = sessions_df[sessions_df['session_outcome'] == 'Win'].shape[0]
    loss_sessions = sessions_df[sessions_df['session_outcome'] == 'Loss'].shape[0]
    push_sessions = sessions_df[sessions_df['session_outcome'] == 'Push'].shape[0]

    return {
        "Win_Rate_Percentage": (win_sessions / total_sessions) * 100,
        "Loss_Rate_Percentage": (loss_sessions / total_sessions) * 100,
        "Push_Rate_Percentage": (push_sessions / total_sessions) * 100
    }

def calculate_risk_of_ruin_percentage(simulations_df: pd.DataFrame) -> float:
    """
    Calculates the percentage of simulations where ruin occurred.
    """
    if simulations_df.empty:
        return 0.0
    total_simulations = len(simulations_df)
    ruined_simulations = simulations_df[simulations_df['did_ruin_occur_in_simulation'] == True].shape[0]
    return (ruined_simulations / total_simulations) * 100

def calculate_standard_deviation_of_session_profit_loss(sessions_df: pd.DataFrame) -> float:
    """
    Calculates the standard deviation of net profit/loss per session.
    """
    if sessions_df.empty:
        return 0.0
    return sessions_df['net_profit_loss_session'].std()

def calculate_max_drawdown_percentage(rolls_df: pd.DataFrame, starting_bankroll: float) -> float:
    """
    Calculates the maximum drawdown percentage for a simulation.
    Assumes rolls_df contains cumulative bankroll data for a single simulation.
    """
    if rolls_df.empty or starting_bankroll <= 0:
        return 0.0

    # Ensure current_bankroll_after_roll is numeric
    rolls_df['current_bankroll_after_roll'] = pd.to_numeric(rolls_df['current_bankroll_after_roll'])

    # Calculate cumulative max bankroll
    rolls_df['peak_bankroll'] = rolls_df['current_bankroll_after_roll'].cummax()

    # Calculate drawdown
    rolls_df['drawdown'] = rolls_df['peak_bankroll'] - rolls_df['current_bankroll_after_roll']

    # Calculate drawdown percentage relative to peak
    # Avoid division by zero if peak_bankroll is 0
    rolls_df['drawdown_percentage'] = rolls_df.apply(
        lambda row: (row['drawdown'] / row['peak_bankroll']) * 100 if row['peak_bankroll'] > 0 else 0,
        axis=1
    )

    return rolls_df['drawdown_percentage'].max()

def calculate_percentage_sessions_target_reached(sessions_df: pd.DataFrame, target_column: str) -> float:
    """
    Calculates the percentage of sessions where a specific target was reached.
    """
    if sessions_df.empty:
        return 0.0
    total_sessions = len(sessions_df)
    reached_sessions = sessions_df[sessions_df[target_column] == True].shape[0]
    return (reached_sessions / total_sessions) * 100

def calculate_avg_sessions_to_ruin(simulations_df: pd.DataFrame) -> float:
    """
    Calculates the average number of sessions it took for ruin to occur in ruined simulations.
    """
    ruined_sims = simulations_df[simulations_df['did_ruin_occur_in_simulation'] == True]
    if ruined_sims.empty:
        return 0.0
    return ruined_sims['session_number_of_ruin'].mean()

def calculate_ev_per_unit_risk(empirical_ev: float, std_dev_profit_loss: float) -> float:
    """
    Calculates Expected Value (EV) per unit of risk (standard deviation).
    """
    if std_dev_profit_loss == 0:
        return 0.0
    return empirical_ev / std_dev_profit_loss

def calculate_total_hedging_dollars_placed(bets_df: pd.DataFrame) -> float:
    """
    Calculates the total amount of money placed on hedging bets.
    """
    if bets_df.empty:
        return 0.0
    return bets_df[bets_df['is_hedging_bet'] == True]['bet_amount'].sum()

def calculate_percentage_of_total_bets_as_hedging(bets_df: pd.DataFrame) -> float:
    """
    Calculates the percentage of total bet amount that was placed as hedging bets.
    """
    if bets_df.empty or bets_df['bet_amount'].sum() == 0:
        return 0.0
    total_hedging = calculate_total_hedging_dollars_placed(bets_df)
    total_bets = bets_df['bet_amount'].sum()
    return (total_hedging / total_bets) * 100

def calculate_avg_rolls_per_session(sessions_df: pd.DataFrame) -> float:
    """
    Calculates the average number of rolls per session.
    """
    if sessions_df.empty:
        return 0.0
    return sessions_df['total_rolls_in_session'].mean()

def calculate_hourly_dollar_win_loss_rate(avg_net_profit_loss_per_session: float, avg_rolls_per_session: float, rolls_per_hour: int = 90) -> float:
    """
    Calculates the estimated hourly dollar win/loss rate.
    Assumes a typical craps table sees approximately 60-120 rolls per hour, default to 90.
    """
    if avg_rolls_per_session == 0:
        return 0.0
    sessions_per_hour = rolls_per_hour / avg_rolls_per_session
    return avg_net_profit_loss_per_session * sessions_per_hour

def calculate_effective_house_edge(total_profit_loss: float, total_dollars_risked: float) -> float:
    """
    Calculates the effective house edge for a strategy.
    """
    if total_dollars_risked == 0:
        return 0.0
    return (-total_profit_loss / total_dollars_risked) * 100

def generate_strategy_performance_summary(sim_data: dict) -> pd.DataFrame:
    """
    Generates the Strategy_Performance_Summary table.
    """
    simulations_df = sim_data['simulations']
    sessions_df = sim_data['sessions']

    if simulations_df.empty or sessions_df.empty:
        return pd.DataFrame(columns=[
            'Strategy_Name', 'Avg_Net_Profit_Loss_Per_Session', 'Empirical_EV_Per_Dollar_Risked',
            'Win_Rate_Percentage', 'Loss_Rate_Percentage', 'Push_Rate_Percentage',
            'Total_Sessions_Simulated', 'Total_Dollars_Risked'
        ])

    # Group by strategy name (assuming one strategy per simulation for simplicity here)
    # For more complex scenarios, you might need to join sessions_df with simulations_df on simulation_id
    # and then group by strategy_name from the simulations_df.
    # For now, we assume each simulation_id corresponds to a unique strategy_name.

    results = []
    for sim_id, sim_group in simulations_df.groupby('simulation_id'):
        strategy_name = sim_group['strategy_name'].iloc[0]
        current_sessions_df = sessions_df[sessions_df['simulation_id'] == sim_id]

        avg_profit_loss = calculate_avg_net_profit_loss_per_session(current_sessions_df)
        empirical_ev = calculate_empirical_ev_per_dollar_risked(current_sessions_df)
        win_loss_push_rates = calculate_win_loss_push_rates(current_sessions_df)
        total_sessions_simulated = len(current_sessions_df)
        total_dollars_risked = current_sessions_df['total_dollars_risked_in_session'].sum()

        results.append({
            'Strategy_Name': strategy_name,
            'Avg_Net_Profit_Loss_Per_Session': avg_profit_loss,
            'Empirical_EV_Per_Dollar_Risked': empirical_ev,
            'Win_Rate_Percentage': win_loss_push_rates['Win_Rate_Percentage'],
            'Loss_Rate_Percentage': win_loss_push_rates['Loss_Rate_Percentage'],
            'Push_Rate_Percentage': win_loss_push_rates['Push_Rate_Percentage'],
            'Total_Sessions_Simulated': total_sessions_simulated,
            'Total_Dollars_Risked': total_dollars_risked
        })

    return pd.DataFrame(results)

def generate_strategy_risk_profile(sim_data: dict) -> pd.DataFrame:
    """
    Generates the Strategy_Risk_Profile table.
    """
    simulations_df = sim_data['simulations']
    sessions_df = sim_data['sessions']
    rolls_df = sim_data['rolls']

    if simulations_df.empty or sessions_df.empty or rolls_df.empty:
        return pd.DataFrame(columns=[
            'Strategy_Name', 'Risk_Of_Ruin_Percentage', 'Standard_Deviation_Of_Session_ProfitLoss',
            'Max_Drawdown_Percentage', 'Percentage_Sessions_Target_Reached_130%',
            'Percentage_Sessions_Target_Reached_200%', 'Percentage_Sessions_Ending_In_Profit',
            'Avg_Sessions_To_Ruin', 'EV_Per_Unit_Risk'
        ])

    results = []
    for sim_id, sim_group in simulations_df.groupby('simulation_id'):
        strategy_name = sim_group['strategy_name'].iloc[0]
        current_sessions_df = sessions_df[sessions_df['simulation_id'] == sim_id]
        current_rolls_df = rolls_df[rolls_df['simulation_id'] == sim_id]

        risk_of_ruin = calculate_risk_of_ruin_percentage(sim_group)
        std_dev_profit_loss = calculate_standard_deviation_of_session_profit_loss(current_sessions_df)
        
        # Max Drawdown needs the starting bankroll for the simulation
        starting_bankroll_sim = sim_group['starting_bankroll_for_simulation'].iloc[0]
        max_drawdown = calculate_max_drawdown_percentage(current_rolls_df, starting_bankroll_sim)

        target_130_reached = calculate_percentage_sessions_target_reached(current_sessions_df, 'did_target_130_reach')
        target_200_reached = calculate_percentage_sessions_target_reached(current_sessions_df, 'did_target_200_reach')
        
        percentage_ending_in_profit = calculate_percentage_sessions_target_reached(current_sessions_df, 'session_outcome') # Need to adjust this to count 'Win'
        percentage_ending_in_profit = (current_sessions_df['session_outcome'] == 'Win').sum() / len(current_sessions_df) * 100 if not current_sessions_df.empty else 0.0

        avg_sessions_to_ruin = calculate_avg_sessions_to_ruin(sim_group)
        
        empirical_ev = calculate_empirical_ev_per_dollar_risked(current_sessions_df)
        ev_per_unit_risk = calculate_ev_per_unit_risk(empirical_ev, std_dev_profit_loss)

        results.append({
            'Strategy_Name': strategy_name,
            'Risk_Of_Ruin_Percentage': risk_of_ruin,
            'Standard_Deviation_Of_Session_ProfitLoss': std_dev_profit_loss,
            'Max_Drawdown_Percentage': max_drawdown,
            'Percentage_Sessions_Target_Reached_130%': target_130_reached,
            'Percentage_Sessions_Target_Reached_200%': target_200_reached,
            'Percentage_Sessions_Ending_In_Profit': percentage_ending_in_profit,
            'Avg_Sessions_To_Ruin': avg_sessions_to_ruin,
            'EV_Per_Unit_Risk': ev_per_unit_risk
        })

    return pd.DataFrame(results)

def generate_hedging_impact_and_usage(sim_data: dict) -> pd.DataFrame:
    """
    Generates the Hedging_Impact_And_Usage table.
    """
    simulations_df = sim_data['simulations']
    sessions_df = sim_data['sessions']
    rolls_df = sim_data['rolls'] # Add rolls_df here
    bets_df = sim_data['bets']

    if simulations_df.empty or sessions_df.empty or bets_df.empty:
        return pd.DataFrame(columns=[
            'Strategy_Name', 'Hedging_Configuration', 'Total_Hedging_Dollars_Placed',
            'Percentage_Of_Total_Bets_As_Hedging', 'Avg_Net_Profit_Loss_Per_Session',
            'Empirical_EV_Per_Dollar_Risked', 'Win_Rate_Percentage',
            'Max_Drawdown_Percentage', 'Standard_Deviation_Of_Session_ProfitLoss',
            'Effective_House_Edge'
        ])

    results = []
    # Assuming 'Hedging_Configuration' would be part of strategy_name or a separate column in simulations
    # For now, we'll just group by strategy_name and assume a single hedging config per strategy
    for sim_id, sim_group in simulations_df.groupby('simulation_id'):
        strategy_name = sim_group['strategy_name'].iloc[0]
        current_sessions_df = sessions_df[sessions_df['simulation_id'] == sim_id]
        current_rolls_df = rolls_df[rolls_df['simulation_id'] == sim_id] # Add this line
        current_bets_df = bets_df[bets_df['simulation_id'] == sim_id]

        total_hedging_dollars_placed = calculate_total_hedging_dollars_placed(current_bets_df)
        percentage_of_total_bets_as_hedging = calculate_percentage_of_total_bets_as_hedging(current_bets_df)
        avg_net_profit_loss = calculate_avg_net_profit_loss_per_session(current_sessions_df)
        empirical_ev = calculate_empirical_ev_per_dollar_risked(current_sessions_df)
        win_rate = calculate_win_loss_push_rates(current_sessions_df)['Win_Rate_Percentage']
        std_dev_profit_loss = calculate_standard_deviation_of_session_profit_loss(current_sessions_df)
        
        # Max Drawdown and Effective House Edge require more data/logic
        starting_bankroll_sim = sim_group['starting_bankroll_for_simulation'].iloc[0]
        max_drawdown = calculate_max_drawdown_percentage(current_rolls_df, starting_bankroll_sim)
        total_profit_loss_sim = current_sessions_df['net_profit_loss_session'].sum()
        total_dollars_risked_sim = current_sessions_df['total_dollars_risked_in_session'].sum()
        effective_house_edge = calculate_effective_house_edge(total_profit_loss_sim, total_dollars_risked_sim)

        results.append({
            'Strategy_Name': strategy_name,
            'Hedging_Configuration': 'Default', # Placeholder
            'Total_Hedging_Dollars_Placed': total_hedging_dollars_placed,
            'Percentage_Of_Total_Bets_As_Hedging': percentage_of_total_bets_as_hedging,
            'Avg_Net_Profit_Loss_Per_Session': avg_net_profit_loss,
            'Empirical_EV_Per_Dollar_Risked': empirical_ev,
            'Win_Rate_Percentage': win_rate,
            'Max_Drawdown_Percentage': max_drawdown,
            'Standard_Deviation_Of_Session_ProfitLoss': std_dev_profit_loss,
            'Effective_House_Edge': effective_house_edge
        })

    return pd.DataFrame(results)

def generate_comprehensive_strategy_comparison(sim_data: dict) -> pd.DataFrame:
    """
    Generates the Comprehensive_Strategy_Comparison table.
    """
    simulations_df = sim_data['simulations']
    sessions_df = sim_data['sessions']
    rolls_df = sim_data['rolls']
    bets_df = sim_data['bets']

    if simulations_df.empty or sessions_df.empty or rolls_df.empty or bets_df.empty:
        return pd.DataFrame(columns=[
            'Strategy_Name', 'Avg_Net_Profit_Loss_Per_Session', 'Empirical_EV_Per_Dollar_Risked',
            'Win_Rate_Percentage', 'Risk_Of_Ruin_Percentage', 'Standard_Deviation_Of_Session_ProfitLoss',
            'Max_Drawdown_Percentage', 'Avg_Rolls_Per_Session', 'Hourly_Dollar_Win_Loss_Rate',
            'Percentage_Sessions_Target_Reached_200%', 'EV_Per_Unit_Risk'
        ])

    results = []
    for sim_id, sim_group in simulations_df.groupby('simulation_id'):
        strategy_name = sim_group['strategy_name'].iloc[0]
        current_sessions_df = sessions_df[sessions_df['simulation_id'] == sim_id]
        current_rolls_df = rolls_df[rolls_df['simulation_id'] == sim_id]
        current_bets_df = bets_df[bets_df['simulation_id'] == sim_id]

        avg_net_profit_loss = calculate_avg_net_profit_loss_per_session(current_sessions_df)
        empirical_ev = calculate_empirical_ev_per_dollar_risked(current_sessions_df)
        win_rate = calculate_win_loss_push_rates(current_sessions_df)['Win_Rate_Percentage']
        risk_of_ruin = calculate_risk_of_ruin_percentage(sim_group)
        std_dev_profit_loss = calculate_standard_deviation_of_session_profit_loss(current_sessions_df)
        
        starting_bankroll_sim = sim_group['starting_bankroll_for_simulation'].iloc[0]
        max_drawdown = calculate_max_drawdown_percentage(current_rolls_df, starting_bankroll_sim)

        avg_rolls_per_session = calculate_avg_rolls_per_session(current_sessions_df)
        hourly_dollar_win_loss_rate = calculate_hourly_dollar_win_loss_rate(avg_net_profit_loss, avg_rolls_per_session)
        
        target_200_reached = calculate_percentage_sessions_target_reached(current_sessions_df, 'did_target_200_reach')
        
        ev_per_unit_risk = calculate_ev_per_unit_risk(empirical_ev, std_dev_profit_loss)

        results.append({
            'Strategy_Name': strategy_name,
            'Avg_Net_Profit_Loss_Per_Session': avg_net_profit_loss,
            'Empirical_EV_Per_Dollar_Risked': empirical_ev,
            'Win_Rate_Percentage': win_rate,
            'Risk_Of_Ruin_Percentage': risk_of_ruin,
            'Standard_Deviation_Of_Session_ProfitLoss': std_dev_profit_loss,
            'Max_Drawdown_Percentage': max_drawdown,
            'Avg_Rolls_Per_Session': avg_rolls_per_session,
            'Hourly_Dollar_Win_Loss_Rate': hourly_dollar_win_loss_rate,
            'Percentage_Sessions_Target_Reached_200%': target_200_reached,
            'EV_Per_Unit_Risk': ev_per_unit_risk
        })

    return pd.DataFrame(results)

def save_analysis_to_database(performance_summary_df: pd.DataFrame,
                              risk_profile_df: pd.DataFrame,
                              hedging_impact_df: pd.DataFrame,
                              comprehensive_comparison_df: pd.DataFrame):
    """
    Saves the generated analytical summary DataFrames to their respective tables in the database.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Helper function to insert DataFrame into a table
        def insert_df_to_db(df: pd.DataFrame, table_name: str):
            if df.empty:
                return

            # Drop 'id' column if it exists, as it's auto-generated by the database
            df_to_insert = df.copy()
            if 'id' in df_to_insert.columns:
                df_to_insert = df_to_insert.drop(columns=['id'])

            # Convert UUID columns to string for psycopg2
            for col in df_to_insert.columns:
                if df_to_insert[col].dtype == 'object' and df_to_insert[col].apply(lambda x: isinstance(x, uuid.UUID)).any():
                    df_to_insert[col] = df_to_insert[col].astype(str)
            
            # No generic rounding for floats, let psycopg2 handle NUMERIC precision
            
            cols = df_to_insert.columns.tolist()
            insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, cols)),
                sql.SQL(', ').join(sql.Placeholder() * len(cols))
            )
            
            data_to_insert = [tuple(row) for row in df_to_insert.itertuples(index=False)]
            cursor.executemany(insert_query, data_to_insert)
            print(f"Data flushed to {table_name} successfully.")

        # Truncate tables before inserting new data to avoid primary key conflicts
        # and ensure fresh analysis results.
        cursor.execute("TRUNCATE TABLE Strategy_Performance_Summary, Strategy_Risk_Profile, Hedging_Impact_And_Usage, Comprehensive_Strategy_Comparison RESTART IDENTITY;")
        conn.commit()

        insert_df_to_db(performance_summary_df, 'Strategy_Performance_Summary')
        insert_df_to_db(risk_profile_df, 'Strategy_Risk_Profile')
        insert_df_to_db(hedging_impact_df, 'Hedging_Impact_And_Usage')
        insert_df_to_db(comprehensive_comparison_df, 'Comprehensive_Strategy_Comparison')

        conn.commit()
        print("All analysis results saved to database successfully.")

    except Exception as e:
        print(f"Error saving analysis to database: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Example usage:
    # This assumes you have run a simulation using crapssim/simulation.py
    # and data has been populated in the database.

    print("Fetching simulation data...")
    all_sim_data = fetch_simulation_data()

    if not all_sim_data['simulations'].empty:
        print("\nGenerating Strategy Performance Summary:")
        performance_summary = generate_strategy_performance_summary(all_sim_data)
        print(performance_summary)

        print("\nGenerating Strategy Risk Profile:")
        risk_profile = generate_strategy_risk_profile(all_sim_data)
        print(risk_profile)

        print("\nGenerating Hedging Impact and Usage:")
        hedging_impact = generate_hedging_impact_and_usage(all_sim_data)
        print(hedging_impact)

        print("\nGenerating Comprehensive Strategy Comparison:")
        comprehensive_comparison = generate_comprehensive_strategy_comparison(all_sim_data)
        print(comprehensive_comparison)

        print("\nSaving analysis results to database...")
        save_analysis_to_database(performance_summary, risk_profile, hedging_impact, comprehensive_comparison)
        print("Analysis saved.")
    else:
        print("No simulation data found in the database. Please run a simulation first.")