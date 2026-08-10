# Phiếu Phản Ánh — K3 Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng `> [Câu trả lời của bạn]` bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Nguyen Cao Nam  Mã học viên: 2A202601377

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Nếu để mặc định là "changeme", khi đẩy lên Production mà quên cấu hình, ứng dụng vẫn chạy bình thường. Kẻ tấn công có thể dễ dàng đoán ra mật khẩu mặc định này để vượt qua lớp bảo mật và lạm dụng API của mình. Việc "Fail Fast" ép ứng dụng văng lỗi và tắt ngay lập tức, giúp mình phát hiện ra sự cố cấu hình ngay lúc khởi động chứ không phải lúc bị mất tiền.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> {"timestamp": "2026-08-10T05:00:00Z", "level": "INFO", "user_id": "sv-test", "cost": 0.05, "message": "ask_llm_success"}
> 
> Hai việc làm được: 1) Có thể dễ dàng dùng các tool như ELK, Datadog để parse, lọc và tìm kiếm tất cả các log của riêng user "sv-test". 2) Có thể thống kê và vẽ biểu đồ tổng chi phí (cost) theo thời gian dựa trên các trường dữ liệu JSON có cấu trúc.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | ~1000 MB |
| Multi-stage | ~140 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Dung lượng chênh lệch chủ yếu là bộ công cụ biên dịch (compiler), mã nguồn thư viện gốc, cache tải về của pip, và các thư viện hệ thống thừa thãi. Bản Multi-stage chỉ vứt những "thành phẩm" cuối cùng sang một hệ điều hành siêu nhỏ (slim), loại bỏ hoàn toàn các rác thải sinh ra trong quá trình build.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Nếu code chuẩn: Layer COPY requirements.txt và RUN pip install sẽ lấy từ cache. Chỉ có layer COPY . . và các lệnh phía sau phải chạy lại.
> Nếu đặt COPY . . lên trước pip install: Bất cứ thay đổi nào dù chỉ 1 ký tự trong main.py cũng làm hỏng toàn bộ cache của các dòng phía sau. Docker sẽ phải tải và cài lại toàn bộ thư viện pip mỗi lần mình sửa code, làm chậm quá trình build cực kỳ nhiều.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Chuỗi sự kiện: Ứng dụng Python có lỗ hổng thực thi mã từ xa (RCE) -> Kẻ tấn công gọi API để chạy bash script bên trong container -> Vì container chạy bằng root, script này có toàn quyền tải malware, sửa file hệ thống hoặc tìm cách leo thang đặc quyền ra máy chủ vật lý chứa container (container escape). 
> Lệnh USER tạo và ép ứng dụng chạy dưới quyền người dùng thường, cắt đứt ngay tại bước chạy script vì kẻ tấn công sẽ bị báo lỗi "Permission denied" khi cố tình can thiệp hệ thống.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Có thể gửi tối đa 20 request trong 2 giây. Ví dụ: gửi 10 request vào lúc 12:00:59. Sang 12:01:00 hệ thống đếm giờ bị reset lại, người đó ngay lập tức gửi thêm 10 request nữa. Kết quả là trong vòng 2 giây (từ 59 sang 00), API đã bị gọi 20 lần. Cửa sổ trượt (sliding window) triệt tiêu hoàn toàn lỗ hổng này.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate Limit chặn request gửi quá nhanh trong khoảng thời gian siêu ngắn (chống Spam, chống DDoS). Cost Guard chặn vượt hạn mức tiền bạc trong khoảng thời gian dài (chống cháy túi, phá sản).
> - Rate Limit qua, Cost Guard chặn: Mới 1 request đầu tiên trong ngày nhưng câu hỏi quá dài ngốn tới 11 USD (vượt ngân sách 10 USD). Rate limit không cản vì tần suất rất thấp, nhưng Cost Guard chặn lại vì hết tiền.
> - Rate Limit chặn, Cost Guard qua: Gửi liên tục 15 request trong 1 giây, mỗi request tốn 0.01 USD. Cost Guard thấy mới hết 0.15$ nên cho qua, nhưng Rate Limit sẽ block từ request thứ 11 vì quá nhanh.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> 1. Redis chết, endpoint gộp trả về lỗi 500/503.
> 2. Hệ thống điều phối (như Kubernetes/Docker Swarm) ping thấy /health trả lỗi liên tục.
> 3. Hệ thống nghĩ container đã bị treo, bèn ra lệnh "giết" (kill/restart) cả 3 container.
> 4. Toàn bộ API sập hoàn toàn. Nếu tách ra, /ready báo lỗi thì hệ thống chỉ dừng gửi traffic tới container, còn /health báo 200 giúp container vẫn "sống" chờ Redis khôi phục.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Con số history_length sẽ nhảy loạn xạ thay vì tăng đều. Khi có 3 container (3 tiến trình độc lập với RAM riêng biệt), request thứ 1 được điều hướng tới container A. Request thứ 2 lọt vào container B, lúc này B là cái "biển trắng" chưa hề có dữ liệu của request 1, nên history_length lại quay về 1. Việc lưu ra Redis giúp đồng bộ não bộ của cả 3 container.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Lỗi gặp phải: Vào thử đường dẫn Render (https://day12...) trên trình duyệt thì nhận được {"detail":"Method Not Allowed"} thay vì giao diện.
> Nguyên nhân: Trình duyệt mặc định gửi request GET, trong khi API /ask của ứng dụng cấu hình chỉ nhận POST.
> Cách sửa: API hoàn toàn bình thường, giải pháp là phải dùng lệnh "curl -X POST" ở dưới terminal hoặc gọi qua code để nhúng được API_KEY và JSON Body thay vì ấn link trình duyệt.
