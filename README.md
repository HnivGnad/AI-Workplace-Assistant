# AI Task & Document Assistant

## Tổng quan

Dự án portfolio hướng đến trợ lý quản lý công việc và hỏi đáp tài liệu bằng AI.
**Đã triển khai trong Task 1.1:** bộ khung FastAPI, cấu hình môi trường,
endpoint `/health`, Swagger UI, kiểm thử pytest và kiểm tra mã bằng Ruff.

## Chức năng dự kiến

Chưa triển khai: tải tài liệu, tìm kiếm và hỏi đáp bằng RAG, trích xuất công việc,
xem xét/xác nhận đề xuất, quản lý công việc, AI Agent và đánh giá chất lượng AI.
Không có lời gọi LLM, kết nối database, Docker hoặc frontend ở giai đoạn này.

## Công nghệ

- Python 3.11+, FastAPI, Uvicorn, Pydantic và Pydantic Settings.
- Quản lý dependencies: `uv`; hỗ trợ phương án `venv` và `pip`.
- Phát triển: pytest, HTTPX (cho TestClient) và Ruff.
- Dự kiến cho các bước sau: LangGraph, API tương thích OpenAI, FAISS,
  SQLite và SQLAlchemy. Các thư viện này **chưa được cài đặt**.

Task 1.1 sử dụng cấu trúc `app/` tại thư mục gốc và `/health` theo yêu cầu riêng,
khác với cấu trúc `backend/` và `/api/health` trong đề xuất AGENTS.md.
SQLite/FAISS cũng chỉ là định hướng mới; chưa có quyết định triển khai lưu trữ.

## Cấu trúc dự án

```text
.
├── AGENTS.md
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/          # Settings
│   ├── api/           # Chưa có API nghiệp vụ
│   ├── agent/
│   ├── rag/
│   ├── services/
│   ├── db/
│   └── schemas/
├── tests/             # Health, Swagger và cấu hình
├── evals/
│   ├── datasets/
│   └── reports/
├── data/
│   ├── documents/
│   └── vector_store/
├── docs/api.md
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

Các package chưa sử dụng chỉ có `__init__.py`; thư mục dữ liệu trống có `.gitkeep`.

## Thiết lập môi trường

Chạy các lệnh từ thư mục gốc dự án. Cần Python 3.11 trở lên hoặc `uv`
(có thể tự cài Python nếu chưa có phiên bản phù hợp).

Tạo cấu hình cục bộ nếu cần thay đổi giá trị mặc định:

```powershell
# PowerShell — chỉ chạy nếu chưa có .env
Copy-Item .env.example .env
```

Trên Linux/macOS: `cp -n .env.example .env`.
Không cần `.env` hoặc API key để chạy ứng dụng. Không đưa `.env` vào Git.

| Biến | Ý nghĩa |
|---|---|
| `APP_NAME` | Tên hiển thị trong API và Swagger |
| `APP_ENV` | `development`, `test` hoặc `production` |
| `DEBUG` | Bật chế độ debug; mặc định `false`, tệp mẫu là `true` |
| `API_HOST`, `API_PORT` | Địa chỉ và cổng cho `python -m app.main`; mặc định `127.0.0.1:8000` |
| `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` | Dành cho bước sau; hiện để trống, không sử dụng |
| `DATABASE_URL` | Dành cho bước sau; chưa mở kết nối hoặc tạo database |
| `LOG_LEVEL` | `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG` hoặc `TRACE` |

Settings đọc biến môi trường trước `.env`, sau đó mới dùng giá trị mặc định.
`.env` được tìm theo thư mục chạy lệnh; biến không được khai báo trong Settings
sẽ bị từ chối nếu xuất hiện trong `.env`. Cổng phải nằm trong khoảng 1–65535.
Khóa LLM được khai báo bằng `SecretStr` để che giá trị khi hiển thị Settings.

## Cài đặt

Ưu tiên `uv`:

```shell
uv sync --extra dev --locked
```

Lệnh tạo `.venv` và cài phiên bản trong `uv.lock`. Nếu máy có Windows Store alias
`python` không hoạt động, dùng các lệnh `uv run` bên dưới thay cho `python` trực tiếp.
Có thể chọn Python cụ thể bằng `uv sync --extra dev --locked --python 3.11`.

Phương án tiêu chuẩn khi không có `uv`:

```shell
python -m venv .venv
```

Kích hoạt bằng `.venv\Scripts\Activate.ps1` trên PowerShell, hoặc
`source .venv/bin/activate` trên Linux/macOS, rồi chạy:

```shell
python -m pip install -e ".[dev]"
```

Phương án pip dùng khoảng phiên bản trong `pyproject.toml`, không đọc `uv.lock`.

## Chạy ứng dụng

```shell
uv run python -m app.main
```

Với venv đã kích hoạt: `python -m app.main`.
Lệnh này áp dụng `API_HOST`, `API_PORT` và `LOG_LEVEL` từ Settings.

Để tự tải lại khi sửa mã:

```shell
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Khi dùng Uvicorn CLI, truyền host/port qua tham số CLI; lệnh này không tự lấy
`API_HOST`/`API_PORT` của ứng dụng. Dừng server bằng Ctrl+C.

Với cấu hình mặc định, mở:

- Health: <http://127.0.0.1:8000/health>
- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI: <http://127.0.0.1:8000/openapi.json>

Kết quả `/health`:

```json
{"status": "ok", "service": "AI Task & Document Assistant"}
```

Swagger UI sử dụng tài nguyên CDN mặc định của FastAPI; trình duyệt cần truy cập
Internet để tải giao diện. Health và OpenAPI không cần dịch vụ bên ngoài.
Chi tiết hợp đồng API tại [docs/api.md](docs/api.md).

## Chạy kiểm thử

```shell
uv run pytest
```

Kiểm thử dùng TestClient, không cần API key hoặc dịch vụ ngoài.

Đã kiểm chứng trên Windows với Python 3.14.8: 7 kiểm thử đạt; `/health`, `/docs`
và `/openapi.json` trả HTTP 200 khi chạy server thực tế. Các phiên bản Python
khác trong phạm vi khai báo 3.11+ chưa được chạy kiểm thử trên máy này.
Phiên bản Starlette trong lockfile phát cảnh báo ngừng hỗ trợ HTTPX trong
TestClient ở tương lai; hiện kiểm thử vẫn đạt. Giữ HTTPX theo phạm vi Task 1.1,
chưa thêm thư viện thay thế hoặc ẩn cảnh báo.

## Kiểm tra chất lượng mã

```shell
uv run ruff check .
uv run ruff format --check .
```

Định dạng mã: `uv run ruff format .`. Khi đã kích hoạt venv, có thể dùng trực tiếp
`pytest`, `ruff check .` và `ruff format --check .`.
Ruff kiểm tra quy ước, import, lỗi phổ biến và cú pháp tương thích Python 3.11.

## Lộ trình phát triển

1. **Task 1.1:** nền tảng ứng dụng, cấu hình, health và công cụ phát triển.
2. Các nhiệm vụ sau: chốt mô hình dữ liệu/API và bổ sung lưu trữ.
3. Xử lý tài liệu, tìm kiếm và hỏi đáp RAG có nguồn tham chiếu.
4. Trích xuất công việc, xem xét/xác nhận và quản lý công việc.
5. Đánh giá AI, giao diện, Docker và hoàn thiện demo portfolio.

Task 1.1 không triển khai các bước tiếp theo. Dữ liệu người dùng trong `data/`,
database, chỉ mục vector, log và môi trường ảo được bỏ qua bởi `.gitignore`.
