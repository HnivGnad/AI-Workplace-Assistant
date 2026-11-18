# API hiện có — Task 1.1–1.6

Theo yêu cầu Task 1.1, endpoint kiểm tra hoạt động là `GET /health`, thay cho
`GET /api/health` trong đề xuất ban đầu của AGENTS.md. `/api/health` chưa tồn tại.

Phản hồi HTTP 200 mặc định:

```json
{"status": "ok", "service": "AI Task & Document Assistant"}
```

`service` lấy từ `APP_NAME`. Endpoint chỉ xác nhận ứng dụng đang phản hồi,
không kiểm tra database hoặc LLM.

Swagger UI: `/docs`; OpenAPI schema: `/openapi.json`.

Task 1.5–1.6 bổ sung `GET /tasks`, `POST /tasks`, `PATCH /tasks/{id}`.
Theo yêu cầu nhiệm vụ, các đường dẫn này không có tiền tố `/api` như đề xuất
ban đầu. Chưa có DELETE, API chat hoặc upload tài liệu.
Hợp đồng request/response cho frontend: [api-contract.md](api-contract.md).
