import unittest
from unittest.mock import MagicMock, patch
import uuid
import psycopg2 # Added for error handling test
from psycopg2 import sql # Added for sql.SQL
from crapssim.logger import SimulationLogger

class TestSimulationLogger(unittest.TestCase):

    def setUp(self):
        self.logger = SimulationLogger()
        self.simulation_id = str(uuid.uuid4())
        self.session_id = str(uuid.uuid4())
        self.roll_id = str(uuid.uuid4())
        self.bet_event_id = str(uuid.uuid4())
        self.player_id = str(uuid.uuid4())

    def test_record_simulation_start(self):
        self.logger.record_simulation_start(self.simulation_id, "TestStrategy", self.player_id, 1000.0)
        self.assertEqual(len(self.logger.simulation_data), 1)
        self.assertEqual(self.logger.simulation_data[0]["simulation_id"], self.simulation_id)
        self.assertEqual(self.logger.simulation_data[0]["strategy_name"], "TestStrategy")
        self.assertEqual(self.logger.simulation_data[0]["starting_bankroll_for_simulation"], 1000.0)

    def test_record_session_start(self):
        self.logger.record_session_start(self.session_id, self.simulation_id, 1, 500.0)
        self.assertEqual(len(self.logger.session_data), 1)
        self.assertEqual(self.logger.session_data[0]["session_id"], self.session_id)
        self.assertEqual(self.logger.session_data[0]["simulation_id"], self.simulation_id)
        self.assertEqual(self.logger.session_data[0]["session_number"], 1)
        self.assertEqual(self.logger.session_data[0]["starting_bankroll_session"], 500.0)
        self.assertEqual(self.logger.session_data[0]["max_bankroll_during_session"], 500.0)
        self.assertEqual(self.logger.session_data[0]["min_bankroll_during_session"], 500.0)

    def test_record_roll(self):
        self.logger.record_roll(self.roll_id, self.session_id, self.simulation_id, self.player_id, 1, 7, 510.0, 10.0, 50.0, "On")
        self.assertEqual(len(self.logger.roll_data), 1)
        self.assertEqual(self.logger.roll_data[0]["roll_id"], self.roll_id)
        self.assertEqual(self.logger.roll_data[0]["player_id"], self.player_id)
        self.assertEqual(self.logger.roll_data[0]["dice_roll_value"], 7)
        self.assertEqual(self.logger.roll_data[0]["current_bankroll_after_roll"], 510.0)

    def test_update_roll(self):
        self.logger.record_roll(self.roll_id, self.session_id, self.simulation_id, self.player_id, 1, 0, 500.0, 0.0, 0.0, "Off")
        self.logger.update_roll(self.roll_id, 7, 510.0, 10.0, 50.0, "On")
        self.assertEqual(len(self.logger.roll_data), 1)
        self.assertEqual(self.logger.roll_data[0]["dice_roll_value"], 7)
        self.assertEqual(self.logger.roll_data[0]["current_bankroll_after_roll"], 510.0)
        self.assertEqual(self.logger.roll_data[0]["cumulative_net_profit_loss_session_to_roll"], 10.0)
        self.assertEqual(self.logger.roll_data[0]["cumulative_dollars_risked_session_to_roll"], 50.0)
        self.assertEqual(self.logger.roll_data[0]["point_status_after_roll"], "On")

        # Test updating a non-existent roll_id (should not change anything)
        non_existent_roll_id = str(uuid.uuid4())
        self.logger.update_roll(non_existent_roll_id, 11, 600.0, 100.0, 150.0, "Off")
        self.assertEqual(len(self.logger.roll_data), 1) # Still only one roll record
        self.assertEqual(self.logger.roll_data[0]["dice_roll_value"], 7) # Original data unchanged

    def test_record_bet_event(self):
        self.logger.record_bet_event(self.bet_event_id, "bet123", self.session_id, self.simulation_id,
                                     self.player_id, "Place", "Pass Line", 10.0, False, 1)
        self.assertEqual(len(self.logger.bet_data), 1)
        self.assertEqual(self.logger.bet_data[0]["bet_event_id"], self.bet_event_id)
        self.assertEqual(self.logger.bet_data[0]["event_type"], "Place")
        self.assertEqual(self.logger.bet_data[0]["bet_amount"], 10.0)

        self.logger.record_bet_event(str(uuid.uuid4()), "bet123", self.session_id, self.simulation_id,
                                     self.player_id, "Resolve", "Pass Line", 0.0, False, 5, profit_loss_from_bet_resolution=5.0)
        self.assertEqual(len(self.logger.bet_data), 2)
        self.assertEqual(self.logger.bet_data[1]["event_type"], "Resolve")
        self.assertEqual(self.logger.bet_data[1]["profit_loss_from_bet_resolution"], 5.0)

    def test_record_session_end(self):
        self.logger.record_session_start(self.session_id, self.simulation_id, 1, 500.0)
        self.logger.record_session_end(self.session_id, 550.0, 50.0, "Win", 10, 100.0, 550.0, 490.0, True, False, 10.0, 100.0)
        self.assertEqual(self.logger.session_data[0]["ending_bankroll_session"], 550.0)
        self.assertEqual(self.logger.session_data[0]["session_outcome"], "Win")
        self.assertEqual(self.logger.session_data[0]["total_rolls_in_session"], 10)

    def test_record_simulation_end(self):
        self.logger.record_simulation_start(self.simulation_id, "TestStrategy", self.player_id, 1000.0)
        self.logger.record_simulation_end(self.simulation_id, 5, 50, 1050.0, False)
        self.assertEqual(self.logger.simulation_data[0]["total_sessions_simulated"], 5)
        self.assertEqual(self.logger.simulation_data[0]["simulation_end_bankroll"], 1050.0)
        self.assertEqual(self.logger.simulation_data[0]["did_ruin_occur_in_simulation"], False)

    @patch('psycopg2.connect')
    def test_flush_to_database(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Populate some data
        self.logger.record_simulation_start(self.simulation_id, "TestStrategy", self.player_id, 1000.0)
        self.logger.record_session_start(self.session_id, self.simulation_id, 1, 500.0)
        self.logger.record_roll(self.roll_id, self.session_id, self.simulation_id, self.player_id, 1, 7, 510.0, 10.0, 50.0, "On")
        self.logger.record_bet_event(self.bet_event_id, "bet123", self.session_id, self.simulation_id,
                                     self.player_id, "Place", "Pass Line", 10.0, False, 1)
        self.logger.record_session_end(self.session_id, 550.0, 50.0, "Win", 10, 100.0, 550.0, 490.0, True, False, 10.0, 100.0)
        self.logger.record_simulation_end(self.simulation_id, 1, 10, 1050.0, False)

        self.logger.flush_to_database(mock_conn)

        # Assert that execute was called for simulation and session, and executemany for rolls and bets
        # Assert that execute was called for simulation and session, and executemany for rolls and bets
        self.assertEqual(mock_cursor.execute.call_count, 1) # For simulation
        self.assertEqual(mock_cursor.executemany.call_count, 3) # For sessions, rolls, and bets

        # Check the arguments for the execute calls (simulation and session)
        # We can't assert exact UUIDs, so we check the structure and types
        sim_call_args = mock_cursor.execute.call_args_list[0].args
        self.assertIsInstance(sim_call_args[0], sql.Composed) # Check SQL object
        # The values are embedded in the SQL string when using sql.Literal, so we can't check sim_call_args[1]

        # session_call_args = mock_cursor.execute.call_args_list[1].args # Removed this line
        # self.assertIsInstance(session_call_args[0], sql.Composed) # Removed this line

        # Check the arguments for the executemany calls (sessions, rolls, and bets)
        session_call_args = mock_cursor.executemany.call_args_list[0].args
        self.assertIsInstance(session_call_args[0], sql.Composed) # Check SQL object
        self.assertEqual(len(session_call_args[1]), 1) # One session record

        roll_call_args = mock_cursor.executemany.call_args_list[1].args
        self.assertIsInstance(roll_call_args[0], sql.Composed) # Check SQL object
        self.assertEqual(len(roll_call_args[1]), 1) # One roll record
        self.assertIsInstance(roll_call_args[1][0][0], str) # roll_id is UUID string
        self.assertIsInstance(roll_call_args[1][0][1], str) # session_id is UUID string
        self.assertIsInstance(roll_call_args[1][0][2], str) # simulation_id is UUID string
        self.assertIsInstance(roll_call_args[1][0][3], str) # player_id is UUID string
        self.assertEqual(roll_call_args[1][0][4], 1)
        self.assertEqual(roll_call_args[1][0][5], 7)

        bet_call_args = mock_cursor.executemany.call_args_list[2].args # Changed index to 2
        self.assertIsInstance(bet_call_args[0], sql.Composed) # Check SQL object
        self.assertEqual(len(bet_call_args[1]), 1) # One bet record
        self.assertIsInstance(bet_call_args[1][0][0], str) # bet_event_id is UUID string
        self.assertEqual(bet_call_args[1][0][1], 'bet123')
        self.assertIsInstance(bet_call_args[1][0][2], str) # session_id is UUID string
        self.assertIsInstance(bet_call_args[1][0][3], str) # simulation_id is UUID string
        self.assertIsInstance(bet_call_args[1][0][4], str) # player_id is UUID string
        self.assertEqual(bet_call_args[1][0][5], 'Place')
        self.assertEqual(bet_call_args[1][0][6], 'Pass Line')
        self.assertEqual(bet_call_args[1][0][7], 10.0)

        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

        # Assert buffers are cleared
        self.assertEqual(len(self.logger.simulation_data), 0)
        self.assertEqual(len(self.logger.session_data), 0)
        self.assertEqual(len(self.logger.roll_data), 0)
        self.assertEqual(len(self.logger.bet_data), 0)

    @patch('psycopg2.connect')
    def test_flush_to_database_error_handling(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Database error")

        self.logger.record_simulation_start(self.simulation_id, "TestStrategy", self.player_id, 1000.0)

        with self.assertRaises(psycopg2.Error):
            self.logger.flush_to_database(mock_conn)

        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        # Buffers should not be cleared on error
        self.assertEqual(len(self.logger.simulation_data), 1)

if __name__ == '__main__':
    unittest.main()