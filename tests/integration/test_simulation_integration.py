import unittest
import os
import psycopg2
import uuid
from crapssim.simulation import run_full_simulation
from crapssim.db_utils import get_db_connection, create_tables
from crapssim.strategy import BetPassLine

class TestSimulationIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a test database and tables before all tests."""
        os.environ["DB_NAME"] = "test_crapssim_db_integration"
        os.environ["DB_USER"] = "crapssim_user"
        os.environ["DB_PASSWORD"] = "crapssim_password"
        os.environ["DB_HOST"] = "localhost"
        create_tables()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test database after all tests."""
        conn = None
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database="postgres", # Connect to default db to drop test db
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"DROP DATABASE IF EXISTS {os.getenv('DB_NAME')} WITH (FORCE);")
            cur.close()
            print(f"Database '{os.getenv('DB_NAME')}' dropped.")
        except Exception as e:
            print(f"Error dropping database: {e}")
        finally:
            if conn:
                conn.close()

    def setUp(self):
        """Clear tables before each test to ensure isolation."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE bets, rolls, sessions, simulations RESTART IDENTITY;")
        conn.commit()
        cur.close()
        conn.close()

    def test_run_full_simulation_data_integrity(self):
        """
        Test that run_full_simulation correctly populates all tables
        and maintains foreign key relationships.
        """
        num_sessions = 3
        player_bankroll = 100.0
        player_strategy = BetPassLine(5)
        player_name = "TestPlayer"

        run_full_simulation(
            num_sessions=num_sessions,
            player_bankroll=player_bankroll,
            player_strategy=player_strategy,
            player_name=player_name,
            max_rolls_per_session=10,
            verbose=False
        )

        conn = get_db_connection()
        cur = conn.cursor()

        # Verify simulations table
        cur.execute("SELECT * FROM simulations;")
        simulations = cur.fetchall()
        self.assertEqual(len(simulations), 1)
        sim_id = simulations[0][0]
        self.assertEqual(simulations[0][1], player_strategy.__class__.__name__)
        self.assertEqual(simulations[0][3], player_bankroll)
        self.assertEqual(simulations[0][4], num_sessions)

        # Verify sessions table
        cur.execute("SELECT * FROM sessions WHERE simulation_id = %s;", (sim_id,))
        sessions = cur.fetchall()
        self.assertEqual(len(sessions), num_sessions)
        for session in sessions:
            self.assertEqual(session[1], sim_id) # Check FK

        # Verify rolls table
        cur.execute("SELECT * FROM rolls WHERE simulation_id = %s;", (sim_id,))
        rolls = cur.fetchall()
        self.assertGreater(len(rolls), 0)
        for roll in rolls:
            self.assertEqual(roll[2], sim_id) # Check FK
            self.assertIn(roll[1], [s[0] for s in sessions]) # Check FK to session

        # Verify bets table
        cur.execute("SELECT * FROM bets WHERE simulation_id = %s;", (sim_id,))
        bets = cur.fetchall()
        self.assertGreater(len(bets), 0)
        for bet in bets:
            self.assertEqual(bet[3], sim_id) # Check FK
            self.assertIn(bet[2], [s[0] for s in sessions]) # Check FK to session

        cur.close()
        conn.close()

if __name__ == '__main__':
    unittest.main()