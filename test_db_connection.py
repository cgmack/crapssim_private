import unittest
import os
from unittest.mock import patch, MagicMock
import psycopg2
from psycopg2 import sql
from crapssim.db_utils import get_db_connection, create_tables

class TestDbUtils(unittest.TestCase):

    @patch.dict(os.environ, {"DB_HOST": "localhost", "DB_NAME": "test_crapssim_db", "DB_USER": "test_user", "DB_PASSWORD": "test_password"})
    @patch('psycopg2.connect')
    def test_get_db_connection_success(self, mock_connect):
        """Test successful database connection."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        conn = get_db_connection()
        self.assertEqual(conn, mock_conn)
        mock_connect.assert_called_once_with(
            host="localhost",
            database="test_crapssim_db",
            user="test_user",
            password="test_password"
        )

    @patch.dict(os.environ, {"DB_HOST": "localhost", "DB_NAME": "test_crapssim_db", "DB_USER": "test_user", "DB_PASSWORD": "wrong_password"})
    @patch('psycopg2.connect', side_effect=psycopg2.OperationalError("connection failed"))
    def test_get_db_connection_failure(self, mock_connect):
        """Test database connection failure."""
        with self.assertRaises(psycopg2.OperationalError):
            get_db_connection()
        mock_connect.assert_called_once()

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
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch.dict(os.environ, {"DB_HOST": "localhost", "DB_NAME": "test_crapssim_db", "DB_USER": "test_user", "DB_PASSWORD": "test_password"})
    @patch('crapssim.db_utils.get_db_connection', side_effect=psycopg2.OperationalError("connection failed"))
    @patch('psycopg2.connect')
    def test_create_tables_connection_failure(self, mock_psycopg2_connect, mock_get_db_connection):
        """Test table creation when connection to crapssim_db fails."""
        mock_temp_conn = MagicMock()
        mock_temp_cursor = MagicMock()
        mock_temp_conn.cursor.return_value = mock_temp_cursor
        mock_temp_cursor.fetchone.return_value = None  # Simulate database not existing
        mock_psycopg2_connect.return_value = mock_temp_conn

        with self.assertRaises(psycopg2.OperationalError):
            create_tables()

        mock_get_db_connection.assert_called_once()
        # No table creation attempts should be made if connection fails
        mock_temp_cursor.execute.assert_any_call(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier("test_crapssim_db"))
        )
        self.assertFalse(mock_get_db_connection.return_value.cursor.called)
        self.assertFalse(mock_get_db_connection.return_value.commit.called)

if __name__ == '__main__':
    unittest.main()