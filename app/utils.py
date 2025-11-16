"""
유틸리티 함수 모음
"""
from typing import Dict, List, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def aggregate_portfolio_items(portfolio_items: List) -> Tuple[Dict[str, float], Dict[str, int]]:
    """
    포트폴리오 항목을 심볼별로 집계
    
    Args:
        portfolio_items: PortfolioItem 객체 리스트
    
    Returns:
        (aggregated_items, item_ids) 튜플
        - aggregated_items: {symbol: total_quantity}
        - item_ids: {symbol: item_id}
    """
    aggregated_items = defaultdict(float)
    item_ids = {}
    
    for item in portfolio_items:
        aggregated_items[item.symbol] += item.quantity
        item_ids[item.symbol] = item.id
    
    return dict(aggregated_items), item_ids


def format_currency(value: float, currency: str = "USD") -> str:
    """
    통화 포맷팅
    
    Args:
        value: 금액
        currency: 통화 코드
    
    Returns:
        포맷팅된 문자열
    """
    if currency == "KRW":
        return f"{value:,.0f}"
    else:
        return f"{value:,.2f}"


def format_price(value: float, currency: str = "USD") -> str:
    """
    가격 포맷팅 (통화 심볼 포함)
    
    Args:
        value: 가격
        currency: 통화 코드
    
    Returns:
        포맷팅된 문자열
    """
    formatted = format_currency(value, currency)
    if currency == "USD":
        return f"${formatted}"
    elif currency == "KRW":
        return f"₩{formatted}"
    else:
        return f"{formatted} {currency}"


def format_portfolio_message(
    total_value: float,
    base_currency: str,
    items: List[Dict],
    price_data: Dict[str, Dict],
    timestamp: str = None
) -> str:
    """
    포트폴리오 요약 메시지 생성
    
    Args:
        total_value: 총 평가액
        base_currency: 기준 통화
        items: 포트폴리오 항목 리스트
        price_data: 가격 데이터
        timestamp: 타임스탬프 (선택)
    
    Returns:
        포맷팅된 메시지 문자열
    """
    from datetime import datetime
    
    message = f"📊 포트폴리오 요약 ({base_currency})\n"
    if timestamp:
        message += f"⏰ {timestamp}\n"
    else:
        message += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += f"\n💰 총 평가액: {format_currency(total_value, base_currency)} {base_currency}\n\n"
    
    for item in items:
        symbol = item['symbol']
        quantity = item['quantity']
        price_info = price_data.get(symbol, {})
        price = price_info.get('price', 0)
        value = quantity * price
        change_24h = price_info.get('percent_change_24h', 0)
        
        message += f"💵 {symbol}\n"
        message += f"   수량: {quantity:,.6f}\n"
        message += f"   현재가: {format_price(price, base_currency)}\n"
        message += f"   평가액: {format_price(value, base_currency)}\n"
        message += f"   24h 변동: {change_24h:+.2f}%\n\n"
    
    return message


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    변동률 계산
    
    Args:
        old_value: 이전 값
        new_value: 현재 값
    
    Returns:
        변동률 (%)
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100

