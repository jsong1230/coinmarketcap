import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CoinGeckoClient:
    """CoinGecko API 클라이언트"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # 주요 코인 심볼 -> CoinGecko ID 매핑
    SYMBOL_TO_ID = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "SOL": "solana",
        "XRP": "ripple",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "AVAX": "avalanche-2",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "ATOM": "cosmos",
        "ETC": "ethereum-classic",
        "LTC": "litecoin",
        "BCH": "bitcoin-cash",
        "XLM": "stellar",
        "ALGO": "algorand",
        "VET": "vechain",
        "ICP": "internet-computer",
        "FIL": "filecoin",
        "TRX": "tron",
        "EOS": "eos",
        "AAVE": "aave",
        "MKR": "maker",
        "COMP": "compound-governance-token",
        "SUSHI": "sushi",
        "SNX": "havven",
        "YFI": "yearn-finance",
        "CRV": "curve-dao-token",
    }
    
    # 통화 코드 변환 (CoinGecko는 소문자 사용)
    CURRENCY_MAP = {
        "USD": "usd",
        "KRW": "krw",
        "EUR": "eur",
        "GBP": "gbp",
        "JPY": "jpy",
        "CNY": "cny",
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        CoinGecko 클라이언트 초기화
        
        Args:
            api_key: CoinGecko API 키 (선택사항)
                - None: 무료 공개 API 사용 (API 키 불필요, rate limit 있음)
                - Pro API 키: Pro API 사용 (더 높은 rate limit)
        
        참고:
            - 무료 공개 API: https://api.coingecko.com/api/v3 (API 키 불필요)
            - Pro API: https://pro-api.coingecko.com/api/v3 (API 키 필요)
        """
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json"
        }
        # API 키가 있고 비어있지 않으며 'None' 문자열이 아니면 Pro API 사용
        if api_key and api_key.strip() and api_key.strip().lower() != 'none':
            self.headers["x-cg-pro-api-key"] = api_key
            # Pro API는 다른 베이스 URL 사용
            self.BASE_URL = "https://pro-api.coingecko.com/api/v3"
        else:
            # 무료 공개 API 사용 (API 키 불필요)
            self.BASE_URL = "https://api.coingecko.com/api/v3"
    
    def _symbol_to_id(self, symbol: str) -> Optional[str]:
        """심볼을 CoinGecko ID로 변환"""
        return self.SYMBOL_TO_ID.get(symbol.upper())
    
    def _get_coin_ids(self, symbols: List[str]) -> Dict[str, str]:
        """
        심볼 리스트를 CoinGecko ID로 변환
        
        Returns:
            {symbol: coin_id} 매핑 딕셔너리
        """
        symbol_to_id = {}
        for symbol in symbols:
            coin_id = self._symbol_to_id(symbol)
            if coin_id:
                symbol_to_id[symbol.upper()] = coin_id
            else:
                logger.warning(f"심볼 {symbol}에 대한 CoinGecko ID를 찾을 수 없습니다.")
        return symbol_to_id
    
    def get_latest_quotes(self, symbols: List[str], convert: str = "USD") -> Dict:
        """
        여러 코인의 최신 가격 정보 조회
        
        Args:
            symbols: 코인 심볼 리스트 (예: ["BTC", "ETH"])
            convert: 변환 통화 (USD, KRW 등)
        
        Returns:
            API 응답 데이터 (CMC 형식과 호환되도록 변환)
        """
        # 심볼을 CoinGecko ID로 변환
        symbol_to_id = self._get_coin_ids(symbols)
        if not symbol_to_id:
            raise Exception("유효한 코인 심볼을 찾을 수 없습니다.")
        
        coin_ids = list(symbol_to_id.values())
        coin_ids_str = ",".join(coin_ids)
        
        # 통화 코드 변환
        vs_currency = self.CURRENCY_MAP.get(convert.upper(), convert.lower())
        
        url = f"{self.BASE_URL}/simple/price"
        params = {
            "ids": coin_ids_str,
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_last_updated_at": "true"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # CMC 형식과 호환되도록 변환
            return self._convert_to_cmc_format(data, symbol_to_id, convert)
        except requests.exceptions.Timeout:
            logger.error("CoinGecko API 요청 타임아웃")
            raise Exception("CoinGecko API 요청 타임아웃: 서버 응답이 없습니다.")
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko API 요청 실패: {e}")
            raise Exception(f"CoinGecko API 요청 실패: {str(e)}")
    
    def _convert_to_cmc_format(self, cg_data: Dict, symbol_to_id: Dict[str, str], convert: str) -> Dict:
        """
        CoinGecko 응답을 CMC 형식으로 변환
        
        Args:
            cg_data: CoinGecko API 응답
            symbol_to_id: {symbol: coin_id} 매핑
            convert: 변환 통화
        
        Returns:
            CMC 형식과 호환되는 데이터 구조
        """
        vs_currency = self.CURRENCY_MAP.get(convert.upper(), convert.lower())
        result = {"data": {}}
        
        # ID -> Symbol 역매핑 생성
        id_to_symbol = {v: k for k, v in symbol_to_id.items()}
        
        for coin_id, coin_data in cg_data.items():
            symbol = id_to_symbol.get(coin_id)
            if not symbol:
                continue
            
            price = coin_data.get(vs_currency, 0)
            market_cap = coin_data.get(f"{vs_currency}_market_cap", 0)
            volume_24h = coin_data.get(f"{vs_currency}_24h_vol", 0)
            percent_change_24h = coin_data.get(f"{vs_currency}_24h_change", 0)
            last_updated = coin_data.get("last_updated_at")
            
            # CMC 형식으로 변환
            result["data"][symbol] = [{
                "quote": {
                    convert: {
                        "price": price,
                        "market_cap": market_cap,
                        "volume_24h": volume_24h,
                        "percent_change_24h": percent_change_24h,
                        "last_updated": last_updated
                    }
                }
            }]
        
        return result
    
    def parse_quote_data(self, response_data: Dict, symbol: str, convert: str = "USD") -> Optional[Dict]:
        """
        API 응답에서 특정 코인의 가격 데이터 추출
        (CMC 클라이언트와 동일한 인터페이스)
        
        Args:
            response_data: API 응답 데이터 (이미 CMC 형식으로 변환됨)
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
                "percent_change_1h": quote.get("percent_change_1h", 0),  # CoinGecko는 제공하지 않음
                "percent_change_24h": quote.get("percent_change_24h", 0),
                "percent_change_7d": quote.get("percent_change_7d", 0),  # CoinGecko는 제공하지 않음
                "last_updated": quote.get("last_updated")
            }
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"CoinGecko 응답 파싱 오류: {e}")
            return None

