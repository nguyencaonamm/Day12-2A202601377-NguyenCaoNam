"""CP1 — Structured logging.

`print("user abc hỏi gì đó")` là log cho người đọc. Cloud (Railway, Render,
Cloud Run, Datadog...) đọc log bằng máy: một dòng = một JSON object thì mới
lọc/đếm/cảnh báo được. Đây là khác biệt lớn giữa localhost và production.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """CHO SẴN — thời điểm hiện tại theo ISO-8601, múi giờ UTC."""
    return datetime.now(timezone.utc).isoformat()


def log_event(event: str, level: str = "info", **fields) -> str:
    """Ghi một dòng log JSON ra stdout.

    Tạo dict gồm tối thiểu 3 khóa:
        - "event": từ tham số ``event``
        - "level": ``level.lower()`` (bắt buộc viết thường)
        - "timestamp": ``utc_now_iso()``
    rồi thêm mọi thứ từ ``**fields``.

    In ra đúng **một dòng JSON** (``ensure_ascii=False``, không ``indent``)
    và trả về chính chuỗi đó.
    """
    base = {
        "event": event,
        "level": level.lower(),
        "timestamp": utc_now_iso(),
    }
    base.update(fields)  # ghi đè lên nếu trong fields có key trùng

    line = json.dumps(base, ensure_ascii=False)
    print(line, flush=True)
    return line

