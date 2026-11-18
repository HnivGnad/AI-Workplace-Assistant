# Tầng database — Task 1.3–1.4

SQLite với SQLAlchemy 2.x đồng bộ; engine và session factory được tạo khi gọi,
không kết nối hay tạo schema khi import. URL lấy từ Settings.
Chỉ hỗ trợ SQLite trong giai đoạn này. SQLite in-memory dùng StaticPool để
các session trong cùng engine thấy chung database.

## Bảng tasks

| Trường | Kiểu | Ràng buộc |
|---|---|---|
| id | Integer | Khóa chính |
| title | String(255) | NOT NULL; CHECK độ dài 1–255 sau kiểm tra trim |
| description | Text | Nullable |
| status | String enum | NOT NULL; pending (mặc định), in_progress, completed |
| priority | String enum | NOT NULL; medium (mặc định), low, high |
| due_date | Date | Nullable |
| created_at | DateTime | NOT NULL, UTC |
| updated_at | DateTime | NOT NULL, UTC; cập nhật khi ORM ghi thay đổi |

## Bảng documents

| Trường | Kiểu | Ràng buộc |
|---|---|---|
| id | String(36) | Khóa chính; UUID v4 được tạo ngay khi khởi tạo model |
| filename | String(255) | NOT NULL; CHECK không rỗng và độ dài |
| file_type | String(20) | NOT NULL; CHECK không rỗng và độ dài |
| chunk_count | Integer | NOT NULL; mặc định 0, CHECK >= 0 |
| status | String enum | NOT NULL; processing (mặc định), ready, failed |
| created_at | DateTime | NOT NULL, UTC |

Document chỉ lưu metadata. `id` là định danh ổn định để vector chunks dùng làm
`document_id` sau này; chưa có bảng chunk hoặc quan hệ với Task.

## Quy ước dữ liệu

- Enum lưu giá trị chữ thường, có CHECK constraint và validation SQLAlchemy.
- Timestamp do Python sinh lúc INSERT; SQLite lưu UTC không kèm timezone,
  kiểu UTCDateTime khôi phục timezone UTC khi đọc và từ chối datetime thiếu timezone.
- `updated_at` dùng SQLAlchemy onupdate, không phải trigger cho SQL viết trực tiếp.
- Các mặc định ORM (trừ UUID) được áp dụng khi flush/INSERT.
- TaskCreate mặc định priority medium theo yêu cầu nhiệm vụ; đây không phải
  quy tắc suy luận ưu tiên cho đề xuất AI trong tương lai.
- TaskUpdate dùng `model_dump(exclude_unset=True)` để lấy phần thay đổi.
  Cho phép null để xóa description/due_date; từ chối null cho title/status/priority.
- Schemas đầu vào từ chối trường thừa, bao gồm id và timestamps. Response dùng
  `from_attributes=True`. DocumentCreate chỉ nhận filename và file_type;
  trạng thái và chunk_count do xử lý nội bộ quản lý ở giai đoạn sau.
- Title/filename/file_type được trim và kiểm tra độ dài bằng Pydantic.

## Khởi tạo và thay đổi schema

`python -m app.db.init_db` gọi create_all, chỉ tạo bảng còn thiếu, không xóa dữ liệu.
Theo Task 1.3–1.4, chưa thêm Alembic (ngoại lệ so với hướng dẫn migration chung).
create_all không nâng cấp bảng cũ; phải bổ sung migration trước thay đổi schema
có dữ liệu. Chưa có API nghiệp vụ, service, RAG hay upload.
