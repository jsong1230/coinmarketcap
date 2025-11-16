import requests
from typing import Dict, List, Optional
from app.config import settings


class CMCClient:
    """CoinMarketCap API 클라이언트"""
    
    BASE_URL = "https://pro-api.coinmarketcap.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.cmc_api_key
        self.headers = {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json"
        }
    
    def get_latest_quotes(self, symbols: List[str], convert: str = "USD") -> Dict:
        """
        여러 코인의 최신 가격 정보 조회
        
        Args:
            symbols: 코인 심볼 리스트 (예: ["BTC", "ETH"])
            convert: 변환 통화 (USD, KRW 등)
        
        Returns:
            API 응답 데이터
        """
        symbols_str = ",".join(symbols)
        url = f"{self.BASE_URL}/cryptocurrency/quotes/latest"
        params = {
            "symbol": symbols_str,
            "convert": convert
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"CMC API 요청 실패: {str(e)}")
    
    def get_portfolio_data(self, portfolio_id: str, convert: str = "USD") -> Dict:
        """
        CMC 포트폴리오 데이터 조회
        
        Args:
            portfolio_id: CMC 포트폴리오 ID
            convert: 변환 통화
        
        Returns:
            포트폴리오 데이터
        """
        url = f"{self.BASE_URL}/key/v1/portfolios/{portfolio_id}"
        params = {"convert": convert}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"CMC 포트폴리오 조회 실패: {str(e)}")
    
    def parse_quote_data(self, response_data: Dict, symbol: str, convert: str = "USD") -> Optional[Dict]:
        """
        API 응답에서 특정 코인의 가격 데이터 추출
        
        Args:
            response_data: API 응답 데이터
            symbol: 코인 심볼
            convert: 변환 통화
        
        Returns:
            가격 데이터 딕셔너리 또는 None
        """
        try:
            data = response_data.get("data", {})
            coin_data = data.get(symbol)
            
            if not coin_data:
                return None
            
            # coin_data가 딕셔너리인 경우 (단일 심볼 조회)
            if isinstance(coin_data, dict):
                quote = coin_data.get("quote", {}).get(convert, {})
            # coin_data가 리스트인 경우 (다중 심볼 조회)
            elif isinstance(coin_data, list) and len(coin_data) > 0:
                quote = coin_data[0].get("quote", {}).get(convert, {})
            else:
                return None
            
            return {
                "symbol": symbol,
                "price": quote.get("price", 0),
                "market_cap": quote.get("market_cap", 0),
                "volume_24h": quote.get("volume_24h", 0),
                "percent_change_1h": quote.get("percent_change_1h", 0),
                "percent_change_24h": quote.get("percent_change_24h", 0),
                "percent_change_7d": quote.get("percent_change_7d", 0),
                "last_updated": quote.get("last_updated")
            }
        except (KeyError, IndexError, TypeError) as e:
            return None

