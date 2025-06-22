import unittest
from unittest.mock import patch, MagicMock
from main import database_connector


class TestDatabaseConnector(unittest.TestCase):
    @patch('main.create_engine')
    @patch('main.SQLDatabase')
    @patch('main.quote_plus')
    
    def test_successful_connection(self, mock_quote_plus, mock_SQLDatabase, mock_create_engine):
        
        mock_quote_plus.return_value = 'quoted_password'
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        mock_db = MagicMock()
        mock_db.dialect = 'mock_dialect'
        mock_db.get_usable_table_names.return_value = ['table1', 'table2']
        mock_SQLDatabase.return_value = mock_db

        
        db = database_connector('db_str_%s', 'password', schema='myschema')

        
        mock_quote_plus.assert_called_once_with('password')
        mock_create_engine.assert_called_once_with('db_str_quoted_password')
        mock_SQLDatabase.assert_called_once_with(mock_engine, view_support=True, schema='myschema')
        mock_db.get_usable_table_names.assert_called_once()
        mock_db.run.assert_called_once_with("select convert(varchar(25), getdate(), 120)")
        self.assertEqual(db, mock_db)

    @patch('main.create_engine')
    @patch('main.SQLDatabase')
    @patch('main.quote_plus')
    def test_connection_failure(self, mock_quote_plus, mock_SQLDatabase, mock_create_engine):
        
        mock_quote_plus.return_value = 'quoted_password'
        mock_create_engine.side_effect = Exception("DB error")

if __name__ == '__main__':
    unittest.main()