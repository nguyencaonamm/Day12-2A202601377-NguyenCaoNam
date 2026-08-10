"""CP3 — Xác thực bằng API key.

Public URL = ai cũng gọi được. Không có lớp này, hóa đơn LLM của bạn do
người lạ quyết định.
"""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .config import get_settings

ANONYMOUS_USER = "anonymous"

def verify_api_key(
    x_api_key: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> str:
    # Lấy key thật từ môi trường (đã làm ở CP1)
    true_key = get_settings().agent_api_key
    
    # Bắt buộc có key và không được dùng toán tử == để so sánh
    if x_api_key is None or not secrets.compare_digest(x_api_key, true_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing API key")
        
    return x_user_id if x_user_id else ANONYMOUS_USER
