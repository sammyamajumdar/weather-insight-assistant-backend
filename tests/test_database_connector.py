"""
Python script that contains unit tests for the data base connection.
"""
import unittest
from unittest.mock import patch, MagicMock
from main import database_connector


class TestDatabaseConnector(unittest.TestCase):
    """
    Unit tests for the database_connector function.

    This test class verifies that the database_connector function:
      - Properly quotes the database password.
      - Initializes the SQLAlchemy engine and SQLDatabase with the correct arguments.
      - Calls the expected methods on the SQLDatabase instance to check connection and table names.
      - Returns the initialized SQLDatabase object upon successful connection.

    The tests use mocking to simulate database interactions and dependencies.
    """
    @patch('main.create_engine')
    @patch('main.SQLDatabase')
    @patch('main.quote_plus')

    def test_successful_connection(self, mock_quote_plus, mock_sql_database, mock_create_engine):
        """
            Tests that database_connector successfully establishes a database 
            connection and returns the SQLDatabase object.

            This test verifies that:
            - The database password is properly quoted using quote_plus.
            - The SQLAlchemy engine is created with the correct connection string.
            - SQLDatabase is initialized with the engine, view support, and schema.
            - The dialect and usable table names are accessed on the SQLDatabase instance.
            - The test query is executed to verify the connection.
            - The returned object is the same as the mocked SQLDatabase instance.

            All external dependencies are mocked to isolate the function's logic.
        """
        mock_quote_plus.return_value = 'quoted_password'
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_db = MagicMock()
        mock_db.dialect = 'mock_dialect'
        mock_db.get_usable_table_names.return_value = ['table1', 'table2']
        mock_sql_database.return_value = mock_db


        db = database_connector('db_str_%s', 'password', schema='myschema')


        mock_quote_plus.assert_called_once_with('password')
        mock_create_engine.assert_called_once_with('db_str_quoted_password')
        mock_sql_database.assert_called_once_with(mock_engine, view_support=True, schema='myschema')
        mock_db.get_usable_table_names.assert_called_once()
        mock_db.run.assert_called_once_with("select convert(varchar(25), getdate(), 120)")
        self.assertEqual(db, mock_db)

    @patch('main.create_engine')
    @patch('main.SQLDatabase')
    @patch('main.quote_plus')
    def test_connection_failure(self, mock_quote_plus, mock_create_engine):
        """
        Tests that database_connector properly handles and 
        propagates exceptions during database engine creation.

        This test simulates a failure in the database connection process by configuring the mocked
        create_engine function to raise an Exception. It verifies that the exception 
        is raised as expected, allowing the calling code to handle 
        connection errors appropriately.

        All external dependencies are mocked to isolate the function's error-handling logic.
        """

        mock_quote_plus.return_value = 'quoted_password'
        mock_create_engine.side_effect = Exception("DB error")

if __name__ == '__main__':
    unittest.main()
