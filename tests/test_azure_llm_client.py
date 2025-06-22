import unittest
from unittest.mock import patch, MagicMock
from main import get_llm_client


class TestGetLLMClient(unittest.TestCase):
    @patch('main.AzureChatOpenAI')
    def test_get_llm_client_defaults(self, mock_azure_chat_openai):
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
