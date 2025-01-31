import pytest
from unittest.mock import Mock, patch
from src.api.huggingface_api import HuggingFaceAPI

@pytest.fixture
def mock_hf_api():
    with patch('src.api.huggingface_api.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"generated_text": "Test response"}]
        mock_post.return_value = mock_response
        api = HuggingFaceAPI()
        yield api, mock_post

def test_api_initialization():
    api = HuggingFaceAPI()
    assert api.api_url is not None
    assert "Bearer" in api.headers["Authorization"]

def test_successful_response(mock_hf_api):
    api, mock_post = mock_hf_api
    response = api.get_response("Test query")
    assert response == "Test response"
    mock_post.assert_called_once()
    assert mock_post.call_args[1]["json"]["inputs"] == "Test query"

def test_api_error_response(mock_hf_api):
    api, mock_post = mock_hf_api
    mock_post.return_value.status_code = 400
    response = api.get_response("Test query")
    assert response is None

def test_api_network_error(mock_hf_api):
    api, mock_post = mock_hf_api
    mock_post.side_effect = Exception("Network error")
    response = api.get_response("Test query")
    assert response is None

def test_api_invalid_response(mock_hf_api):
    api, mock_post = mock_hf_api
    mock_post.return_value.json.return_value = []
    response = api.get_response("Test query")
    assert response is None

@pytest.mark.parametrize("status_code,expected", [
    (200, "Test response"),
    (400, None),
    (500, None),
    (403, None)
])
def test_various_status_codes(mock_hf_api, status_code, expected):
    api, mock_post = mock_hf_api
    mock_post.return_value.status_code = status_code
    response = api.get_response("Test query")
    assert response == expected

def test_empty_query(mock_hf_api):
    api, _ = mock_hf_api
    response = api.get_response("")
    assert response is not None  # Même une requête vide devrait retourner une réponse

@pytest.mark.integration
def test_real_api_connection():
    pytest.skip("Skipping real API test - should be run manually with valid API key") 