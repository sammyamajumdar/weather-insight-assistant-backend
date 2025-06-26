"""
Python script that contains unit tests for the Azure LLM client.
"""
import unittest
from unittest.mock import patch, MagicMock
from main import get_llm_client


class TestGetLLMClient(unittest.TestCase):
    """
    Unit tests for the get_llm_client function.

    This test class verifies that get_llm_client correctly initializes and returns
    an AzureChatOpenAI client instance with the expected parameters.
    """
    @patch('main.AzureChatOpenAI')
    def test_get_llm_client_defaults(self, mock_azure_chat_openai):
        """
        Tests that get_llm_client returns an AzureChatOpenAI instance with default parameters.

        This test verifies that:
        - get_llm_client initializes AzureChatOpenAI with the 
        default model_name and deployment_name ("gpt-4").
        - The returned object is the same as the mocked AzureChatOpenAI instance.
        """
        mock_instance = MagicMock()
        mock_azure_chat_openai.return_value = mock_instance

        result = get_llm_client()

        mock_azure_chat_openai.assert_called_once_with(
            model_name="gpt-4",
            deployment_name="gpt-4"
        )
        self.assertIs(result, mock_instance)

    @patch('main.AzureChatOpenAI')
    def test_get_llm_client_custom_args(self, mock_azure_chat_openai):
        """
        Tests that get_llm_client correctly passes custom model_name and deployment arguments.

        This test verifies that:
        - get_llm_client initializes AzureChatOpenAI with the 
        provided custom model_name and deployment_name.
        - The returned object is the same as the mocked AzureChatOpenAI instance.
        """
        mock_instance = MagicMock()
        mock_azure_chat_openai.return_value = mock_instance

        result = get_llm_client(model_name="custom-model", deployment="custom-deployment")

        mock_azure_chat_openai.assert_called_once_with(
            model_name="custom-model",
            deployment_name="custom-deployment"
        )
        self.assertIs(result, mock_instance)

if __name__ == "__main__":
    unittest.main()
