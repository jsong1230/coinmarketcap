from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.models import User, PortfolioItem, AlertSettings, PriceSnapshot
from app.cmc_client import CMCClient
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PortfolioService:
    """포트폴리오 관련 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_portfolio_summary(self, user_id: int) -> Optional[Dict]:
        """포트폴리오 요약 조회"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        portfolio_items = self.db.query(PortfolioItem).filter(
            PortfolioItem.user_id == user_id
        ).all()
        
        if not portfolio_items:
            return None
        
        symbols = [item.symbol for item in portfolio_items]
        
        # CMC API로 가격 조회
        cmc_client = CMCClient(user.cmc_api_key)
        try:
            response = cmc_client.get_latest_quotes(symbols, user.base_currency)
            price_data = {}
            
            for symbol in symbols:
                price_info = cmc_client.parse_quote_data(response, symbol, user.base_currency)
                if price_info:
                    price_data[symbol] = price_info
            
            # 총 평가액 계산
            total_value = sum(
                item.quantity * price_data.get(item.symbol, {}).get("price", 0)
                for item in portfolio_items
            )
            
            return {
                "total_value": total_value,
                "base_currency": user.base_currency,
                "items": [
                    {
                        "id": item.id,
                        "symbol": item.symbol,
                        "quantity": item.quantity
                    }
                    for item in portfolio_items
                ],
                "price_data": price_data
            }
        except Exception as e:
            logger.error(f"포트폴리오 요약 조회 실패: {e}")
            return None
    
    def add_portfolio_item(self, user_id: int, symbol: str, quantity: float) -> PortfolioItem:
        """포트폴리오 항목 추가"""
        portfolio_item = PortfolioItem(
            user_id=user_id,
            symbol=symbol.upper(),
            quantity=quantity
        )
        self.db.add(portfolio_item)
        self.db.commit()
        self.db.refresh(portfolio_item)
        return portfolio_item


class AlertService:
    """알림 관련 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_alerts(self, user_id: int) -> List[Dict]:
        """알림 조건 확인 및 알림 메시지 생성"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        alert_settings = self.db.query(AlertSettings).filter(
            AlertSettings.user_id == user_id
        ).first()
        
        if not alert_settings:
            return []
        
        # 최근 스냅샷 조회
        recent_snapshot = self.db.query(PriceSnapshot).filter(
            PriceSnapshot.user_id == user_id
        ).order_by(PriceSnapshot.timestamp.desc()).first()
        
        if not recent_snapshot:
            return []
        
        # 최소 알림 간격 확인
        last_notification_time = recent_snapshot.timestamp
        min_interval = timedelta(minutes=alert_settings.min_notification_interval_minutes)
        
        if datetime.now(last_notification_time.tzinfo) - last_notification_time < min_interval:
            return []
        
        # 현재 포트폴리오 상태 조회
        portfolio_service = PortfolioService(self.db)
        current_summary = portfolio_service.get_portfolio_summary(user_id)
        
        if not current_summary:
            return []
        
        alerts = []
        old_data = recent_snapshot.snapshot_data
        old_total = recent_snapshot.total_portfolio_value
        new_total = current_summary["total_value"]
        
        # 포트폴리오 전체 변동 확인
        if old_total > 0:
            portfolio_change_pct = ((new_total - old_total) / old_total) * 100
            
            if abs(portfolio_change_pct) >= alert_settings.portfolio_percentage_threshold:
                alerts.append({
                    "type": "portfolio_percentage",
                    "message": f"📊 포트폴리오 변동: {portfolio_change_pct:+.2f}% ({old_total:,.2f} → {new_total:,.2f} {user.base_currency})"
                })
            
            if alert_settings.portfolio_absolute_threshold:
                absolute_change = abs(new_total - old_total)
                if absolute_change >= alert_settings.portfolio_absolute_threshold:
                    alerts.append({
                        "type": "portfolio_absolute",
                        "message": f"💰 포트폴리오 금액 변동: {absolute_change:,.2f} {user.base_currency}"
                    })
        
        # 개별 코인 변동 확인
        for item in current_summary["items"]:
            symbol = item["symbol"]
            new_price = current_summary["price_data"].get(symbol, {}).get("price", 0)
            old_price_data = old_data.get(symbol, {})
            old_price = old_price_data.get("price", 0)
            
            if old_price > 0:
                price_change_pct = ((new_price - old_price) / old_price) * 100
                
                if abs(price_change_pct) >= alert_settings.single_coin_percentage_threshold:
                    alerts.append({
                        "type": "coin_percentage",
                        "symbol": symbol,
                        "message": f"📈 {symbol} 변동: {price_change_pct:+.2f}% (${old_price:,.2f} → ${new_price:,.2f})"
                    })
                
                if alert_settings.single_coin_absolute_threshold:
                    absolute_change = abs(new_price - old_price)
                    if absolute_change >= alert_settings.single_coin_absolute_threshold:
                        alerts.append({
                            "type": "coin_absolute",
                            "symbol": symbol,
                            "message": f"💵 {symbol} 가격 변동: ${absolute_change:,.2f}"
                        })
        
        return alerts
    
    def save_snapshot(self, user_id: int, snapshot_data: Dict, total_value: float):
        """가격 스냅샷 저장"""
        snapshot = PriceSnapshot(
            user_id=user_id,
            snapshot_data=snapshot_data,
            total_portfolio_value=total_value
        )
        self.db.add(snapshot)
        self.db.commit()

