import unittest
from unittest.mock import patch, MagicMock
from main import get_sql_agent


class TestGetSQLAgent(unittest.TestCase):
    @patch('main.create_sql_agent')
    @patch('main.SQLDatabaseToolkit')
    @patch('main.AgentType')
    def test_get_sql_agent(self, mock_agent_type, mock_sql_toolkit, mock_create_sql_agent):
        
        mock_azurellm = MagicMock()
        mock_database = MagicMock()
        mock_toolkit_instance = MagicMock()
        mock_sql_toolkit.return_value = mock_toolkit_instance

        mock_agent_type.ZERO_SHOT_REACT_DESCRIPTION = "mock_agent_type"
        mock_agent_executor = MagicMock()
        mock_create_sql_agent.return_value = mock_agent_executor

        
        result = get_sql_agent(mock_azurellm, mock_database)

        
        mock_sql_toolkit.assert_called_once_with(db=mock_database, llm=mock_azurellm)
        mock_create_sql_agent.assert_called_once_with(
            llm=mock_azurellm,
            toolkit=mock_toolkit_instance,
            verbose=True,
            agent_type="mock_agent_type",
            handle_parsing_errors=True
        )
        self.assertIs(result, mock_agent_executor)

if __name__ == "__main__":
    unittest.main()
