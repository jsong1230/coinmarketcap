#!/usr/bin/env python3
"""
텔레그램 Chat ID 확인 스크립트
"""
import os
from telegram import Bot
import asyncio

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8362947773:AAGGAg4OhA25Dji78aFIkY3y_U0Xe9Okzw4")


async def get_updates():
    """봇으로 온 메시지 확인하여 chat_id 추출"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    print("🤖 봇 정보 확인 중...")
    try:
        bot_info = await bot.get_me()
        print(f"✅ 봇 이름: {bot_info.first_name}")
        print(f"✅ 봇 사용자명: @{bot_info.username}")
        print()
    except Exception as e:
        print(f"❌ 봇 정보 조회 실패: {e}")
        return
    
    print("📨 최근 메시지 확인 중...")
    print("💡 봇에게 메시지를 보내면 chat_id를 확인할 수 있습니다.")
    print()
    
    try:
        updates = await bot.get_updates()
        
        if not updates:
            print("❌ 아직 봇으로 온 메시지가 없습니다.")
            print()
            print("📝 다음 단계:")
            print("1. 텔레그램에서 봇 찾기: @" + bot_info.username)
            print("2. 봇에게 아무 메시지나 보내기 (예: /start)")
            print("3. 이 스크립트를 다시 실행")
            return
        
        print(f"✅ {len(updates)}개의 메시지 발견:")
        print()
        
        seen_chats = set()
        for update in updates:
            if update.message:
                chat = update.message.chat
                chat_id = str(chat.id)
                
                if chat_id not in seen_chats:
                    seen_chats.add(chat_id)
                    print(f"📱 Chat ID: {chat_id}")
                    print(f"   이름: {chat.first_name or ''} {chat.last_name or ''}")
                    print(f"   사용자명: @{chat.username or '없음'}")
                    print(f"   타입: {chat.type}")
                    print()
        
        if seen_chats:
            print("💡 위의 Chat ID 중 하나를 GitHub Secrets의 TELEGRAM_CHAT_ID에 설정하세요.")
    
    except Exception as e:
        print(f"❌ 메시지 조회 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(get_updates())

