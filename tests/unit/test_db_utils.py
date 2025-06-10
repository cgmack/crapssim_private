import unittest
import os
import psycopg2
from psycopg2 import sql # Added this import
from crapssim.db_utils import get_db_connection, create_tables
from unittest.mock import patch, MagicMock

class TestDbUtils(unittest.TestCase):

    @patch('psycopg2.connect')
    def test_get_db_connection_success(self, mock_connect):
        """Test successful database connection."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Set environment variables for testing
        os.environ["DB_HOST"] = "test_host"
        os.environ["DB_NAME"] = "test_db"
        os.environ["DB_USER"] = "test_user"
        os.environ["DB_PASSWORD"] = "test_password"

        conn = get_db_connection()
        mock_connect.assert_called_once_with(
            host="test_host",
            database="test_db",
            user="test_user",
            password="test_password"
        )
        self.assertEqual(conn, mock_conn)

        # Clean up environment variables
        del os.environ["DB_HOST"]
        del os.environ["DB_NAME"]
        del os.environ["DB_USER"]
        del os.environ["DB_PASSWORD"]

    @patch('psycopg2.connect', side_effect=psycopg2.OperationalError("Connection failed"))
    def test_get_db_connection_failure(self, mock_connect):
        """Test database connection failure."""
        with self.assertRaises(psycopg2.OperationalError):
            get_db_connection()

    @patch.dict(os.environ, {"DB_HOST": "localhost", "DB_NAME": "test_crapssim_db", "DB_USER": "test_user", "DB_PASSWORD": "test_password"})
    @patch('crapssim.db_utils.get_db_connection')
    @patch('psycopg2.connect')
    def test_create_tables(self, mock_psycopg2_connect, mock_get_db_connection):
        """Test table creation."""
        # Mock for initial connection to 'postgres' database
        mock_temp_conn = MagicMock()
        mock_temp_cursor = MagicMock()
        mock_temp_conn.cursor.return_value = mock_temp_cursor
        mock_temp_cursor.fetchone.return_value = None  # Simulate database not existing
        mock_psycopg2_connect.return_value = mock_temp_conn

        # Mock for connection to 'test_crapssim_db'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        create_tables()

        # Assert initial connection to 'postgres' and database creation
        mock_psycopg2_connect.assert_any_call(
            host="localhost",
            database="postgres",
            user="test_user",
            password="test_password"
        )
        mock_temp_cursor.execute.assert_any_call(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier("test_crapssim_db"))
        )
        mock_temp_cursor.close.assert_called_once()
        mock_temp_conn.close.assert_called_once()

        # Assert connection to 'test_crapssim_db' and table creation
        mock_get_db_connection.assert_called_once()
        self.assertEqual(mock_cursor.execute.call_count, 8) # 8 tables created
        
        # Assert that commit was called
        mock_conn.commit.assert_called_once()
        
        # Assert that cursor was closed
        mock_cursor.close.assert_called_once()
        mock_temp_cursor.close.assert_called_once() # Ensure temp cursor is also closed

    @patch.dict(os.environ, {"DB_HOST": "localhost", "DB_NAME": "test_crapssim_db", "DB_USER": "test_user", "DB_PASSWORD": "test_password"})
    @patch('crapssim.db_utils.get_db_connection')
    @patch('psycopg2.connect')
    def test_create_tables_failure(self, mock_psycopg2_connect, mock_get_db_connection):
        """Test table creation failure and rollback."""
        # Mock for initial connection to 'postgres' database
        mock_temp_conn = MagicMock()
        mock_temp_cursor = MagicMock()
        mock_temp_conn.cursor.return_value = mock_temp_cursor
        mock_temp_cursor.fetchone.return_value = None  # Simulate database not existing
        mock_psycopg2_connect.return_value = mock_temp_conn

        # Mock for connection to 'test_crapssim_db'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        mock_cursor.execute.side_effect = psycopg2.ProgrammingError("Syntax error") # This should be on the second cursor

        with self.assertRaises(psycopg2.ProgrammingError):
            create_tables()

        # Assert that rollback was called
        mock_conn.rollback.assert_called_once()
        
        # Assert that cursors were closed
        mock_cursor.close.assert_called_once()
        mock_temp_cursor.close.assert_called_once() # Ensure temp cursor is also closed

if __name__ == '__main__':
    unittest.main()