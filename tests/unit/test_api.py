import pytest
from unittest.mock import Mock, patch
from src.api.riot_api import RiotAPI

@pytest.fixture
def mock_api():
    with patch('src.api.riot_api.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "ahri": {
                    "id": "Ahri",
                    "name": "Ahri",
                    "title": "the Nine-Tailed Fox"
                }
            }
        }
        mock_get.return_value = mock_response
        api = RiotAPI()
        yield api

def test_api_initialization():
    api = RiotAPI()
    assert api.base_url.endswith("api.riotgames.com/lol")
    assert "X-Riot-Token" in api.headers

def test_get_champion_info(mock_api):
    champion_data = mock_api.get_champion_info("Ahri")
    assert champion_data is not None
    assert champion_data["name"] == "Ahri"
    assert champion_data["title"] == "the Nine-Tailed Fox"

def test_api_error_handling(mock_api):
    with patch('src.api.riot_api.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = mock_api.get_champion_info("NonExistentChampion")
        assert result is None

@pytest.mark.integration
def test_real_api_connection():
    pytest.skip("Skipping real API test - should be run manually with valid API key") 