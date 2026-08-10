"""CP4 — Stateless: state sống ngoài process.

Nếu lịch sử hội thoại nằm trong một dict trong RAM, thì khi scale lên 3
instance, user hỏi câu 1 vào instance A và câu 2 vào instance B sẽ thấy agent
"mất trí nhớ". Container còn bị restart bất cứ lúc nào. Vì vậy state phải
nằm ở nơi mọi instance cùng nhìn thấy: Redis.
"""

from __future__ import annotations

import json

import redis

from .config import get_settings

HISTORY_MAX_MESSAGES = 20
HISTORY_TTL_SECONDS = 7 * 24 * 3600


def get_redis_client(url: str | None = None):
    """CHO SẴN — tạo client Redis từ URL.

    ``fake://`` trả về Redis giả chạy trong RAM, dùng khi máy bạn chưa có
    Docker. Tiện cho lúc học, nhưng KHÔNG dùng khi deploy: nó vẫn là state
    trong process, đúng cái mà CP4 đang tìm cách loại bỏ.
    """
    url = url or get_settings().redis_url
    if url.startswith("fake://"):
        import fakeredis

        return fakeredis.FakeRedis(decode_responses=True)
    return redis.from_url(url, decode_responses=True)


class ConversationStore:
    """Lưu lịch sử hội thoại của từng user trong Redis List."""

    def __init__(self, client) -> None:
        self.client = client

    @staticmethod
    def _key(user_id: str) -> str:
        """CHO SẴN."""
        return f"history:{user_id}"


    def ping(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            return False


    def append(self, user_id: str, role: str, content: str) -> None:
        key = self._key(user_id)
        # Lưu tin nhắn mới vào đuôi danh sách
        self.client.rpush(key, json.dumps({"role": role, "content": content}, ensure_ascii=False))
        # Chỉ giữ lại HISTORY_MAX_MESSAGES tin nhắn gần nhất
        self.client.ltrim(key, -HISTORY_MAX_MESSAGES, -1)
        # Tự động xoá lịch sử nếu sau 7 ngày không trò chuyện
        self.client.expire(key, HISTORY_TTL_SECONDS)


    def get_history(self, user_id: str) -> list[dict]:
        key = self._key(user_id)
        # Lấy toàn bộ danh sách
        raw_history = self.client.lrange(key, 0, -1)
        # Convert từ chuỗi JSON về Python dict
        return [json.loads(item) for item in raw_history]


    def clear(self, user_id: str) -> None:
        """CHO SẴN — xóa lịch sử của một user."""
        self.client.delete(self._key(user_id))
