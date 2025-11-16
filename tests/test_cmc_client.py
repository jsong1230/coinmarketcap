import pytest
from unittest.mock import Mock, patch
from app.cmc_client import CMCClient


def test_cmc_client_init():
    client = CMCClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert "X-CMC_PRO_API_KEY" in client.headers


@patch("app.cmc_client.requests.get")
def test_get_latest_quotes_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "BTC": [{
                "quote": {
                    "USD": {
                        "price": 50000,
                        "market_cap": 1000000000,
                        "percent_change_24h": 5.0
                    }
                }
            }]
        }
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    client = CMCClient(api_key="test_key")
    result = client.get_latest_quotes(["BTC"], "USD")
    
    assert "data" in result
    assert "BTC" in result["data"]


@patch("app.cmc_client.requests.get")
def test_get_latest_quotes_failure(mock_get):
    mock_get.side_effect = Exception("API Error")
    
    client = CMCClient(api_key="test_key")
    
    with pytest.raises(Exception) as exc_info:
        client.get_latest_quotes(["BTC"], "USD")
    
    assert "CMC API 요청 실패" in str(exc_info.value)


def test_parse_quote_data():
    response_data = {
        "data": {
            "BTC": [{
                "quote": {
                    "USD": {
                        "price": 50000,
                        "market_cap": 1000000000,
                        "volume_24h": 50000000,
                        "percent_change_1h": 1.0,
                        "percent_change_24h": 5.0,
                        "percent_change_7d": 10.0,
                        "last_updated": "2024-01-01T00:00:00Z"
                    }
                }
            }]
        }
    }
    
    client = CMCClient(api_key="test_key")
    result = client.parse_quote_data(response_data, "BTC", "USD")
    
    assert result is not None
    assert result["symbol"] == "BTC"
    assert result["price"] == 50000
    assert result["percent_change_24h"] == 5.0

