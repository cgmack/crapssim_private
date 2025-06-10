import unittest
import os
import uuid
from unittest.mock import patch, MagicMock
from crapssim.simulation import run_full_simulation
from crapssim.strategy import BetPassLine
from crapssim.db_utils import get_db_connection, create_tables
import psycopg2

class TestSimulationIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up environment variables for a test database
        os.environ["DB_HOST"] = "localhost"
        os.environ["DB_NAME"] = "test_crapssim_db"
        os.environ["DB_USER"] = "test_crapssim_user"
        os.environ["DB_PASSWORD"] = "test_crapssim_password"

        # Attempt to connect and create tables for testing
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Drop tables if they exist to ensure a clean state for each test run
            cur.execute("""
                DROP TABLE IF EXISTS bets CASCADE;
                DROP TABLE IF EXISTS rolls CASCADE;
                DROP TABLE IF EXISTS sessions CASCADE;
                DROP TABLE IF EXISTS simulations CASCADE;
            """)
            conn.commit()
            create_tables(conn)
            conn.close()
        except psycopg2.OperationalError as e:
            print(f"Could not connect to test database. Please ensure PostgreSQL is running and credentials are correct. Error: {e}")
            # Skip tests if database is not available
            raise unittest.SkipTest("PostgreSQL test database not available.")
        except Exception as e:
            print(f"Error during test database setup: {e}")
            raise

    @classmethod
    def tearDownClass(cls):
        # Clean up environment variables
        del os.environ["DB_HOST"]
        del os.environ["DB_NAME"]
        del os.environ["DB_USER"]
        del os.environ["DB_PASSWORD"]

        # Clean up test database tables
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                DROP TABLE IF EXISTS bets CASCADE;
                DROP TABLE IF EXISTS rolls CASCADE;
                DROP TABLE IF EXISTS sessions CASCADE;
                DROP TABLE IF EXISTS simulations CASCADE;
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error during test database teardown: {e}")

    def test_run_full_simulation_data_persistence(self):
        """
        Test that run_full_simulation correctly logs data to the database
        and that data can be retrieved.
        """
        num_sessions = 2
        player_bankroll = 100.0
        player_strategy = BetPassLine(5)
        strategy_name = "TestPassLineStrategy"
        max_rolls_per_session = 5

        run_full_simulation(
            num_sessions=num_sessions,
            player_bankroll=player_bankroll,
            player_strategy=player_strategy,
            strategy_name=strategy_name,
            max_rolls_per_session=max_rolls_per_session,
            verbose=False
        )

        # Verify data in the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Check simulations table
        cur.execute("SELECT * FROM simulations;")
        simulations = cur.fetchall()
        self.assertEqual(len(simulations), 1)
        self.assertEqual(simulations[0][1], strategy_name) # strategy_name
        self.assertEqual(float(simulations[0][2]), player_bankroll) # starting_bankroll_for_simulation
        self.assertEqual(simulations[0][3], num_sessions) # total_sessions_to_run

        # Check sessions table
        cur.execute("SELECT * FROM sessions;")
        sessions = cur.fetchall()
        self.assertEqual(len(sessions), num_sessions)
        for session in sessions:
            self.assertEqual(float(session[3]), player_bankroll) # starting_bankroll_session
            self.assertIsNotNone(session[4]) # ending_bankroll_session
            self.assertIsNotNone(session[5]) # net_profit_loss_session
            self.assertIsNotNone(session[6]) # session_outcome
            self.assertGreater(session[7], 0) # total_rolls_in_session

        # Check rolls table
        cur.execute("SELECT * FROM rolls;")
        rolls = cur.fetchall()
        self.assertGreater(len(rolls), 0) # Should have rolls from all sessions
        for roll in rolls:
            self.assertIsNotNone(roll[4]) # dice_roll_value (should be non-zero after roll)
            self.assertIsNotNone(roll[5]) # current_bankroll_after_roll

        # Check bets table
        cur.execute("SELECT * FROM bets;")
        bets = cur.fetchall()
        self.assertGreater(len(bets), 0) # Should have bets placed and resolved
        for bet in bets:
            self.assertIsNotNone(bet[6]) # bet_type
            self.assertIsNotNone(bet[7]) # bet_amount
            self.assertIsNotNone(bet[9]) # roll_number_when_event_occurred

        cur.close()
        conn.close()

if __name__ == '__main__':
    unittest.main()