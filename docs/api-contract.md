# Hợp đồng API cho frontend — Task 1.5–1.6

Base URL mặc định: `http://127.0.0.1:8000`. JSON dùng tên trường snake_case.
Chưa yêu cầu authentication. Khởi tạo database bằng `uv run python -m app.db.init_db`
trước khi gọi API task. OpenAPI thực tế: `/openapi.json`; Swagger UI: `/docs`.

| Method | Endpoint | Thành công | Lỗi |
|---|---|---|---|
| GET | `/health` | 200, `{status, service}` | 500 |
| POST | `/tasks` | 201, TaskResponse | 422, 500 |
| GET | `/tasks` | 200, TaskResponse[] | 422, 500 |
| PATCH | `/tasks/{id}` | 200, TaskResponse | 404, 422, 500 |

Chỉ các endpoint trên đã có. Không có DELETE, GET task theo ID, chat hoặc upload.

## Tạo task

`POST /tasks`, header `Content-Type: application/json`:

```json
{
  "title": "Implement authentication API",
  "description": "Develop backend authentication endpoints",
  "priority": "high",
  "due_date": "2026-12-01"
}
```

| Trường | Kiểu | Quy tắc |
|---|---|---|
| title | string | Bắt buộc; trim khoảng trắng; độ dài 1–255; không chứa NUL (U+0000) |
| description | string hoặc null | Tùy chọn, mặc định null |
| priority | low / medium / high | Tùy chọn, mặc định medium; không nhận null |
| due_date | date hoặc null | Tùy chọn; frontend gửi YYYY-MM-DD; mặc định null |

Status tạo mới luôn là pending. Không gửi id, status, created_at, updated_at hoặc
trường khác khi tạo; trường thừa bị từ chối với 422.

Ví dụ TaskResponse (ID và thời gian do server tạo):

```json
{
  "id": 1,
  "title": "Implement authentication API",
  "description": "Develop backend authentication endpoints",
  "status": "pending",
  "priority": "high",
  "due_date": "2026-12-01",
  "created_at": "2026-11-19T00:00:00Z",
  "updated_at": "2026-11-19T00:00:00Z"
}
```

TaskResponse luôn chứa đủ 8 trường trên. id là integer; timestamps là ISO 8601
UTC (Z hoặc +00:00). due_date là ngày không kèm timezone.

## Danh sách, lọc và phân trang

`GET /tasks?status=pending&priority=high&limit=20&offset=0`

| Query | Giá trị | Mặc định |
|---|---|---|
| status | pending / in_progress / completed | Không lọc |
| priority | low / medium / high | Không lọc |
| limit | integer, 1–100 | 20 |
| offset | integer, 0–9223372036854775807 | 0 |

Hai bộ lọc kết hợp bằng AND. Sắp xếp created_at DESC, sau đó id DESC.
Phản hồi là mảng trực tiếp, không bọc trong `items`, không có total count.
Không có kết quả hoặc offset vượt cuối danh sách trả `[]` và HTTP 200.
Giá trị query không hợp lệ trả 422. Bỏ query không dùng thay vì gửi chuỗi `null`.

## Cập nhật một phần

`PATCH /tasks/1` với `{"status":"completed"}`.

Cho phép title, description, status, priority, due_date. Tất cả đều có thể bỏ qua.
Trường bỏ qua được giữ nguyên. description/due_date nhận null để xóa giá trị;
title/status/priority không nhận null. Title áp dụng cùng quy tắc như khi tạo.
Không cho sửa id hoặc timestamps; mọi trường thừa đều trả 422.

`{}` được phép: trả 200 và bản ghi hiện tại, không thay đổi updated_at.
Nếu giá trị thực sự thay đổi, ORM cập nhật updated_at theo UTC.
ID phải là số nguyên dương trong phạm vi signed 64-bit; ID sai định dạng/phạm vi
trả 422, ID hợp lệ nhưng không tồn tại trả 404.

## Phản hồi lỗi

404: `{"detail":"Task not found"}`.

422 dùng cấu trúc validation mặc định FastAPI: `{"detail":[...]}`. Mỗi phần tử
có `loc`, `msg`, `type` và có thể thêm dữ liệu tùy lỗi. Frontend dùng loc để gắn
lỗi vào trường tương ứng; không phụ thuộc nguyên văn thông điệp tiếng Anh.

500: `{"detail":"Internal server error"}`; không trả SQL hoặc traceback.
Lỗi ghi trước commit được rollback. Nếu commit thành công nhưng refresh/phản hồi
thất bại, dữ liệu có thể đã lưu; kiểm tra danh sách trước khi tạo lại để tránh trùng.

## CORS và ví dụ frontend

Biến môi trường CORS_ORIGINS nhận mảng JSON:

```env
CORS_ORIGINS='["http://localhost:5173","http://127.0.0.1:5173"]'
```

Mặc định cho phép hai origin trên, methods GET/POST/PATCH và Content-Type.
Không bật credentials. Đổi cấu hình cần khởi động lại backend. Dùng `[]` để
không cho phép origin nào. CORS không thay thế authentication.

```javascript
const response = await fetch("http://127.0.0.1:8000/tasks", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title: "Review report" })
});
const body = await response.json();
if (!response.ok) throw new Error(JSON.stringify(body.detail));
console.log(body.id);
```

Integration tests đối chiếu paths/status codes OpenAPI và kiểm tra phản hồi
thực tế của POST/GET/PATCH, health, CORS và các trường hợp lỗi.
