import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "crapssim_db"),
            user=os.getenv("DB_USER", "crapssim_user"),
            password=os.getenv("DB_PASSWORD", "crapssim_password")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

def create_tables():
    """Creates the necessary tables in the PostgreSQL database if they don't exist."""
    conn = None
    try:
        # Connect to the default 'postgres' database to create the crapssim_db if it doesn't exist
        temp_conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database="postgres",
            user=os.getenv("DB_USER", "crapssim_user"),
            password=os.getenv("DB_PASSWORD", "crapssim_password")
        )
        temp_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = temp_conn.cursor()

        db_name = os.getenv("DB_NAME", "crapssim_db")
        cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s").format(sql.Identifier(db_name)), [db_name])
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"Database '{db_name}' created.")
        cursor.close()
        temp_conn.close()

        # Now connect to the crapssim_db
        conn = get_db_connection()
        cur = conn.cursor()

        # Create simulations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS simulations (
                simulation_id UUID PRIMARY KEY,
                strategy_name VARCHAR(255),
                player_id UUID,
                starting_bankroll_for_simulation NUMERIC(10, 2),
                total_sessions_simulated INTEGER,
                total_rolls_simulated INTEGER,
                simulation_end_bankroll NUMERIC(10, 2),
                did_ruin_occur_in_simulation BOOLEAN,
                session_number_of_ruin INTEGER
            );
        """)

        # Create sessions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id UUID PRIMARY KEY,
                simulation_id UUID REFERENCES simulations(simulation_id),
                session_number INTEGER,
                starting_bankroll_session NUMERIC(10, 2),
                ending_bankroll_session NUMERIC(10, 2),
                net_profit_loss_session NUMERIC(10, 2),
                session_outcome VARCHAR(50),
                total_rolls_in_session INTEGER,
                total_dollars_risked_in_session NUMERIC(10, 2),
                max_bankroll_during_session NUMERIC(10, 2),
                min_bankroll_during_session NUMERIC(10, 2),
                did_target_130_reach BOOLEAN,
                did_target_200_reach BOOLEAN,
                total_hedging_dollars_placed_in_session NUMERIC(10, 2),
                total_bets_placed_in_session NUMERIC(10, 2)
            );
        """)

        # Create rolls table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rolls (
                roll_id UUID PRIMARY KEY,
                session_id UUID REFERENCES sessions(session_id),
                simulation_id UUID REFERENCES simulations(simulation_id),
                player_id UUID,  -- Added player_id
                roll_number_in_session INTEGER,
                dice_roll_value INTEGER,
                current_bankroll_after_roll NUMERIC(10, 2),
                cumulative_net_profit_loss_session_to_roll NUMERIC(10, 2),
                cumulative_dollars_risked_session_to_roll NUMERIC(10, 2),
                point_status_after_roll VARCHAR(50)
            );
        """)

        # Create bets table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                bet_event_id UUID PRIMARY KEY,
                bet_id VARCHAR(255),
                session_id UUID REFERENCES sessions(session_id),
                simulation_id UUID REFERENCES simulations(simulation_id),
                player_id UUID,
                event_type VARCHAR(50),
                bet_type VARCHAR(255),
                bet_amount NUMERIC(10, 2),
                is_hedging_bet BOOLEAN,
                roll_number_when_event_occurred INTEGER,
                profit_loss_from_bet_resolution NUMERIC(10, 2)
            );
        """)

        # Create Strategy_Performance_Summary table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Strategy_Performance_Summary (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                Strategy_Name VARCHAR(255),
                Avg_Net_Profit_Loss_Per_Session NUMERIC(10, 2),
                Empirical_EV_Per_Dollar_Risked NUMERIC(10, 5),
                Win_Rate_Percentage NUMERIC(5, 2),
                Loss_Rate_Percentage NUMERIC(5, 2),
                Push_Rate_Percentage NUMERIC(5, 2),
                Total_Sessions_Simulated INTEGER,
                Total_Dollars_Risked NUMERIC(10, 2)
            );
        """)

        # Create Strategy_Risk_Profile table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Strategy_Risk_Profile (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                Strategy_Name VARCHAR(255),
                Risk_Of_Ruin_Percentage NUMERIC(5, 2),
                Standard_Deviation_Of_Session_ProfitLoss NUMERIC(10, 2),
                Max_Drawdown_Percentage NUMERIC(5, 2),
                Percentage_Sessions_Target_Reached_130_percent NUMERIC(5, 2),
                Percentage_Sessions_Target_Reached_200_percent NUMERIC(5, 2),
                Percentage_Sessions_Ending_In_Profit NUMERIC(5, 2),
                Avg_Sessions_To_Ruin NUMERIC(10, 2),
                EV_Per_Unit_Risk NUMERIC(10, 5)
            );
        """)

        # Create Hedging_Impact_And_Usage table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Hedging_Impact_And_Usage (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                Strategy_Name VARCHAR(255),
                Hedging_Configuration VARCHAR(255),
                Total_Hedging_Dollars_Placed NUMERIC(10, 2),
                Percentage_Of_Total_Bets_As_Hedging NUMERIC(5, 2),
                Avg_Net_Profit_Loss_Per_Session NUMERIC(10, 2),
                Empirical_EV_Per_Dollar_Risked NUMERIC(10, 5),
                Win_Rate_Percentage NUMERIC(5, 2),
                Max_Drawdown_Percentage NUMERIC(5, 2),
                Standard_Deviation_Of_Session_ProfitLoss NUMERIC(10, 2),
                Effective_House_Edge NUMERIC(5, 2)
            );
        """)

        # Create Comprehensive_Strategy_Comparison table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Comprehensive_Strategy_Comparison (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                Strategy_Name VARCHAR(255),
                Avg_Net_Profit_Loss_Per_Session NUMERIC(10, 2),
                Empirical_EV_Per_Dollar_Risked NUMERIC(10, 5),
                Win_Rate_Percentage NUMERIC(5, 2),
                Risk_Of_Ruin_Percentage NUMERIC(5, 2),
                Standard_Deviation_Of_Session_ProfitLoss NUMERIC(10, 2),
                Max_Drawdown_Percentage NUMERIC(5, 2),
                Avg_Rolls_Per_Session NUMERIC(10, 2),
                Hourly_Dollar_Win_Loss_Rate NUMERIC(10, 2),
                Percentage_Sessions_Target_Reached_200_percent NUMERIC(5, 2),
                EV_Per_Unit_Risk NUMERIC(10, 5)
            );
        """)

        conn.commit()
        print("Tables created successfully or already exist.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            if 'cur' in locals() and cur: # Ensure cur exists and is not None
                cur.close()
            conn.close()

if __name__ == "__main__":
    # Example usage:
    # To create tables, ensure your .env file has the correct PostgreSQL credentials
    # and then run this script directly: python crapssim/db_utils.py
    create_tables()