"""
Python script that contains unit tests for the LLM SQL agent.
"""
import unittest
from unittest.mock import patch, MagicMock
from main import get_sql_agent


class TestGetSQLAgent(unittest.TestCase):
    """
    Unit tests for the get_sql_agent function.

    This test class verifies that get_sql_agent:
      - Correctly initializes the SQLDatabaseToolkit with the provided language model and database.
      - Calls create_sql_agent with the expected arguments,
        including the agent type and parsing error handling.
      - Returns the agent executor instance as expected.

    All external dependencies are mocked to isolate and test the 
    function's logic and integration points.
    """
    @patch('main.create_sql_agent')
    @patch('main.SQLDatabaseToolkit')
    @patch('main.AgentType')
    def test_get_sql_agent(self, mock_agent_type, mock_sql_toolkit, mock_create_sql_agent):
        """
        Tests that get_sql_agent correctly initializes and returns a SQL agent executor.

        This test verifies that:
        - SQLDatabaseToolkit is initialized with the provided language model and database.
        - create_sql_agent is called with the correct arguments, including the toolkit instance,
            agent type, verbosity, and error handling options.
        - The function returns the agent executor instance produced by create_sql_agent.

        All external dependencies are mocked to isolate the logic of get_sql_agent.
        """

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
