# API hiện có — Task 1.1

Theo yêu cầu Task 1.1, endpoint kiểm tra hoạt động là `GET /health`, thay cho
`GET /api/health` trong đề xuất ban đầu của AGENTS.md. `/api/health` chưa tồn tại.

Phản hồi HTTP 200 mặc định:

```json
{"status": "ok", "service": "AI Task & Document Assistant"}
```

`service` lấy từ `APP_NAME`. Endpoint chỉ xác nhận ứng dụng đang phản hồi,
không kiểm tra database hoặc LLM. Chưa có API nghiệp vụ.

Swagger UI: `/docs`; OpenAPI schema: `/openapi.json`.
