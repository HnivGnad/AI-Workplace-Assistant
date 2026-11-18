# AGENTS.md — AI Task & Document Assistant

> **Mục đích:** Đây là tài liệu định hướng chính cho AI coding agent làm việc trong repository. Phải đọc tài liệu này trước khi tìm hiểu, chỉnh sửa, kiểm thử hoặc bổ sung mã nguồn.
>
> **Trạng thái dự án:** Đang ở giai đoạn lập kế hoạch cho sản phẩm mẫu (MVP) phục vụ portfolio. Công nghệ, cấu trúc thư mục và API dưới đây là **đề xuất ban đầu**, không có nghĩa chúng đã được triển khai. Luôn kiểm tra repository thực tế trước khi đưa ra kết luận.

## 1. Mục tiêu dự án

Xây dựng **AI Task & Document Assistant** — ứng dụng web cho phép người dùng tải tài liệu lên, đặt câu hỏi dựa trên nội dung tài liệu và trích xuất những công việc cần thực hiện. Người dùng có thể xem xét, xác nhận, lưu, chỉnh sửa và theo dõi các công việc được đề xuất.

Đây là dự án portfolio hướng đến vị trí **AI Engineer Intern**, tập trung thể hiện năng lực phát triển backend bằng Python, tích hợp mô hình ngôn ngữ lớn (LLM), xây dựng RAG, thiết kế cơ sở dữ liệu, phát triển API, kiểm thử, đánh giá chất lượng AI và triển khai ứng dụng có thể chạy lại được.

**Ưu tiên sản phẩm nhỏ nhưng hoạt động trọn vẹn hơn một hệ thống nhiều tính năng nhưng chưa hoàn thiện.**

### Luồng sử dụng chính

1. Người dùng tải lên tài liệu thuộc định dạng được hỗ trợ.
2. Hệ thống trích xuất văn bản, chia thành các đoạn nhỏ (chunk), tạo embedding và lập chỉ mục tìm kiếm.
3. Người dùng đặt câu hỏi; hệ thống trả lời dựa trên các đoạn tài liệu tìm được, kèm nguồn tham chiếu.
4. Người dùng yêu cầu trích xuất công việc; AI đề xuất danh sách công việc theo cấu trúc dữ liệu xác định trước.
5. Người dùng kiểm tra, chỉnh sửa và xác nhận trước khi lưu công việc.
6. Người dùng theo dõi, thay đổi trạng thái, hạn hoàn thành và mức ưu tiên trên giao diện quản lý.

### Tiêu chí thành công

Một lập trình viên mới có thể chạy dự án theo tài liệu hướng dẫn. Người dùng có thể thực hiện đầy đủ luồng trên bằng tài liệu mẫu. Các chức năng quan trọng có kiểm thử tự động. Hệ thống có thể được trình diễn và giải thích rõ trong buổi phỏng vấn.

## 2. Phạm vi và mức độ ưu tiên

### P0 — Bắt buộc cho MVP

- Tải lên và kiểm tra tệp PDF, TXT. Chỉ bổ sung DOCX nếu không ảnh hưởng tiến độ MVP.
- Trích xuất văn bản; xử lý hợp lý khi tệp trống hoặc không đọc được.
- Chia văn bản thành chunk, tạo embedding và lưu vào chỉ mục có thể tìm kiếm.
- Hỏi đáp theo tài liệu bằng RAG; trả về tên tài liệu và số trang hoặc chunk nguồn nếu có.
- Dùng LLM trích xuất công việc thành dữ liệu có cấu trúc (ví dụ: tiêu đề, mô tả, hạn hoàn thành, mức ưu tiên).
- Yêu cầu người dùng xem xét và xác nhận trước khi lưu công việc do AI đề xuất.
- Thêm, xem, sửa, xóa (CRUD), lọc công việc và cập nhật trạng thái.
- Có giao diện web sử dụng được, REST API, lưu trữ dữ liệu, README, kiểm thử tự động và cách chạy cục bộ bằng Docker.

### P1 — Chỉ thực hiện sau khi P0 ổn định

- Hỗ trợ DOCX nếu chưa làm ở P0.
- Lọc theo nhiều tài liệu; xóa tài liệu và dữ liệu chỉ mục liên quan.
- Xử lý tài liệu lớn dưới nền, hiển thị tiến độ và hỗ trợ thử lại khi gặp lỗi.
- Xây dựng bộ dữ liệu đánh giá RAG và đo chất lượng tìm kiếm, trả lời.
- Xác thực người dùng và tách biệt dữ liệu giữa người dùng nếu mở rộng vượt phạm vi demo một người dùng.

### P2 — Mở rộng tùy chọn, không cản trở MVP

- Cho phép AI gọi công cụ (tool calling) để truy vấn hoặc cập nhật công việc.
- Tóm tắt tài liệu và chủ động gợi ý công việc.
- Kết nối lịch, email; gửi thông báo; OCR; phân quyền nâng cao; triển khai lên cloud.

**Không mở rộng phạm vi tùy tiện:** Tránh tích hợp dịch vụ, xây dựng hệ thống nhiều agent hoặc bổ sung hạ tầng phức tạp khi chưa phục vụ trực tiếp luồng sử dụng chính.

## 3. Kiến trúc đề xuất

```text
[Giao diện: React + TypeScript]
              |
              v
[Backend: FastAPI / Python]
    |              |                 |
    v              v                 v
[Tài liệu]   [Quản lý công việc]   [Dịch vụ AI]
    |              |              |          |
    v              v              v          v
[Đọc tệp]    [PostgreSQL]       [LLM API]  [Embedding]
    |                                         |
    v                                         v
[Chia chunk] ------------------------> [Chỉ mục vector]
                                               |
                                               v
                                         [Tìm kiếm RAG]
```

### Công nghệ ưu tiên (phải kiểm tra trước khi triển khai)

| Thành phần | Đề xuất | Lý do |
|---|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic | Phù hợp hệ sinh thái AI và xây dựng API có kiểu dữ liệu rõ ràng |
| Giao diện | React + TypeScript | Tách biệt giao diện với backend |
| Cơ sở dữ liệu | PostgreSQL | Lưu thông tin tài liệu và công việc |
| Lưu trữ vector | PostgreSQL + pgvector | Đơn giản hóa triển khai nhờ dùng chung cơ sở dữ liệu |
| LLM | Nhà cung cấp có thể thay đổi qua lớp kết nối | Tránh phụ thuộc vào một nhà cung cấp |
| Embedding | Mô hình/nhà cung cấp cấu hình được | Có thể tạo lại chỉ mục khi đổi mô hình |
| Xử lý PDF | PyMuPDF hoặc pypdf | Trích xuất văn bản từ PDF |
| Kiểm thử | pytest; bổ sung kiểm thử frontend khi phù hợp | Dễ chạy lại và kiểm chứng |
| Chạy cục bộ | Docker Compose | Thuận tiện cài đặt và demo |

**Không mặc định sử dụng** LangChain, LlamaIndex, Celery, Redis hoặc Kubernetes. Chỉ bổ sung khi chứng minh được lợi ích thực tế và ghi lại lý do lựa chọn.

## 4. Cấu trúc thư mục đề xuất

Đây là cấu trúc tham khảo. **Không sắp xếp lại mã nguồn đang hoạt động chỉ để giống ví dụ.**

```text
.
├── AGENTS.md
├── README.md
├── .env.example
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/                  # API và dữ liệu yêu cầu/phản hồi
│   │   ├── core/                 # Cấu hình và thành phần dùng chung
│   │   ├── models/               # Mô hình dữ liệu lưu trữ
│   │   ├── repositories/         # Truy cập cơ sở dữ liệu
│   │   ├── services/
│   │   │   ├── documents/        # Đọc tệp, chia chunk, xử lý tài liệu
│   │   │   ├── retrieval/        # Embedding, lập chỉ mục, tìm kiếm
│   │   │   ├── rag/              # Tạo prompt, dẫn nguồn, sinh câu trả lời
│   │   │   └── tasks/            # Trích xuất và quản lý công việc
│   │   └── schemas/              # Kiểu dữ liệu Pydantic và API
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   └── package.json
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── decisions/
│   └── evaluation.md
└── samples/                     # Dữ liệu demo giả lập, có thể chia sẻ
```

## 5. Đối tượng dữ liệu và quy ước API

Những trường dưới đây chỉ là **định hướng thiết kế**, chưa phải cấu trúc cơ sở dữ liệu đã chốt. Phải xác định mô hình dữ liệu, migration và hợp đồng API trước khi triển khai.

- **Document:** `id`, `filename`, `mime_type`, `status`, `created_at`, `error_message?`.
- **DocumentChunk:** `id`, `document_id`, `text`, `chunk_index`, `page_number?`, `embedding_model`, `embedding`.
- **Task:** `id`, `title`, `description?`, `status`, `priority?`, `due_date?`, `source_document_id?`, `source_chunk_ids?`, `created_at`, `updated_at`.
- **TaskProposal:** Công việc do AI đề xuất, đã được kiểm tra cấu trúc nhưng **chưa lưu thành Task** nếu người dùng chưa xác nhận.
- **Answer:** `answer`, `citations[]` và thông báo rõ ràng nếu không đủ bằng chứng để trả lời.

### API dự kiến

| Phương thức | Đường dẫn | Chức năng |
|---|---|---|
| `POST` | `/api/documents` | Tải lên và xử lý tài liệu |
| `GET` | `/api/documents` | Lấy danh sách tài liệu |
| `POST` | `/api/chat/query` | Hỏi đáp theo các tài liệu được chọn |
| `POST` | `/api/tasks/extract` | Trả về công việc AI đề xuất từ tài liệu |
| `GET` | `/api/tasks` | Liệt kê và lọc công việc |
| `POST` | `/api/tasks` | Lưu công việc đã được xác nhận |
| `PATCH` | `/api/tasks/{id}` | Chỉnh sửa thông tin/trạng thái |
| `DELETE` | `/api/tasks/{id}` | Xóa công việc |
| `GET` | `/api/health` | Kiểm tra dịch vụ hoạt động |

Dùng Pydantic để khai báo rõ dữ liệu đầu vào/đầu ra và thống nhất định dạng lỗi. Ghi mọi thay đổi so với đề xuất vào `docs/api.md`.

## 6. Yêu cầu đối với các chức năng AI

### 6.1. Xử lý tài liệu

- Chỉ chấp nhận định dạng tệp được hỗ trợ; giới hạn dung lượng qua cấu hình.
- Khi có thể, kiểm tra nội dung thực tế của tệp thay vì chỉ dựa vào phần mở rộng.
- Coi tài liệu tải lên là **dữ liệu không đáng tin cậy**; không thực thi chỉ dẫn hoặc mã nhúng trong tài liệu.
- Ghi nhận lỗi đọc tệp; không đánh dấu hoàn tất nếu quá trình xử lý chưa thành công.
- Giữ số trang và thông tin nguồn để phục vụ trích dẫn khi có thể.
- Xử lý lại tài liệu phải an toàn, không tạo chunk trùng lặp.

### 6.2. Quy trình RAG

1. Xác định phạm vi tài liệu người dùng được phép truy vấn.
2. Tìm `top-k` chunk liên quan bằng embedding và chỉ mục tìm kiếm.
3. Tạo prompt, phân biệt rõ **nội dung tài liệu** với chỉ dẫn hệ thống.
4. Yêu cầu LLM chỉ trả lời dựa trên bằng chứng được cung cấp đối với câu hỏi về tài liệu.
5. Trả về nguồn tham chiếu trỏ đến đúng chunk/trang thực tế.
6. Nếu không đủ thông tin, thông báo rõ thay vì tự suy đoán nội dung hoặc tạo nguồn giả.

Không tạo nguồn trích dẫn nếu nguồn đó không xuất hiện trong kết quả tìm kiếm. Theo dõi phiên bản mô hình embedding và tạo lại chỉ mục khi thay đổi làm mất tính tương thích.

### 6.3. Trích xuất công việc

- Yêu cầu LLM trả về dữ liệu có cấu trúc; kiểm tra lại bằng Pydantic.
- Phân biệt **công việc đề xuất** với **công việc đã lưu**.
- Không tự tạo hạn hoàn thành, người phụ trách hoặc mức ưu tiên khi tài liệu không có đủ căn cứ; dùng `null` hoặc giá trị chưa xác định.
- Đính kèm nguồn bằng chứng khi có thể (mã tài liệu, chunk hoặc trang).
- Nhận diện các đề xuất có khả năng trùng lặp; cho phép chỉnh sửa trước khi lưu.
- Không cho đầu ra của LLM trực tiếp thực hiện thao tác thay đổi cơ sở dữ liệu.

### 6.4. Quản lý prompt và mô hình

- Lưu prompt trong mã nguồn có quản lý phiên bản để dễ kiểm thử.
- Tách lời gọi LLM/embedding qua các lớp kết nối nhỏ, có thể thay thế.
- Đọc khóa API từ biến môi trường; không đưa khóa bí mật vào repository hoặc log.
- Đặt thời gian chờ, xử lý giới hạn tốc độ và lỗi từ nhà cung cấp; trả thông báo dễ hiểu.
- Cho phép cấu hình tên mô hình cùng các tham số quan trọng của việc sinh câu trả lời và tìm kiếm.

## 7. Quy tắc dành cho AI coding agent

### Trước khi chỉnh sửa

1. Đọc `AGENTS.md`, `README.md`, phần mã nguồn liên quan và các bài kiểm thử hiện có.
2. Kiểm tra cấu trúc thư mục, thư viện phụ thuộc và trạng thái Git thực tế.
3. Xác định yêu cầu cần thực hiện thuộc P0, P1 hay P2.
4. Với thay đổi đáng kể, lập kế hoạch ngắn gồm phạm vi, tệp dự kiến chỉnh sửa và kiểm thử cần chạy.
5. Không ghi đè công việc của người dùng hoặc chỉnh sửa các phần không liên quan.

### Trong khi triển khai

- Thực hiện thay đổi nhỏ nhất nhưng đủ để hoàn thành luồng chức năng từ đầu đến cuối.
- Giữ API gọn; đặt nghiệp vụ trong `services`, truy cập dữ liệu trong `repositories`.
- Dùng kiểu dữ liệu, tên rõ nghĩa và chú thích khi cần; tránh tạo nhiều lớp trừu tượng không mang lại giá trị.
- Khi thay đổi cấu trúc cơ sở dữ liệu, phải có migration; không dựa vào chỉnh sửa thủ công.
- Coi mọi đầu ra từ AI bên ngoài là dữ liệu không đáng tin cậy và phải kiểm tra trước khi sử dụng.
- Xử lý các trường hợp lỗi: tài liệu rỗng, không tìm được chunk liên quan, JSON từ LLM sai cấu trúc, hết thời gian chờ, tải tệp trùng, lỗi cơ sở dữ liệu.
- Ưu tiên kiểm thử có kết quả ổn định bằng cách mô phỏng (mock) lời gọi LLM; không bắt buộc có API key trả phí khi chạy kiểm thử tự động.
- Không báo một chức năng đã hoàn thành nếu chưa có luồng giao diện/API hoạt động hoặc kiểm thử chứng minh được.

### Sau khi triển khai

1. Chạy công cụ định dạng mã, kiểm tra mã và các bài kiểm thử liên quan đang có trong dự án.
2. Báo cáo nội dung đã thay đổi, kiểm thử đã chạy, lỗi còn tồn tại và phần chưa thể xác minh.
3. Cập nhật README, tài liệu API hoặc kiến trúc nếu cách hoạt động/cài đặt thay đổi.
4. Cung cấp cách kiểm tra thủ công khi phù hợp.
5. Nêu rõ giả định và những vấn đề kỹ thuật còn lại; không tự ý mở rộng phạm vi.

### Giới hạn bắt buộc

- Không đưa `.env`, khóa bí mật, thông tin xác thực hoặc tài liệu riêng tư vào Git.
- Không gửi nội dung tài liệu cho bên thứ ba chưa được cấu hình hoặc phê duyệt.
- Không thêm dịch vụ trả phí hay hạ tầng cloud khi chưa được người dùng đồng ý.
- Không tuyên bố hệ thống chính xác tuyệt đối, bảo mật tuyệt đối hoặc đã sẵn sàng cho môi trường production.
- Không dùng dữ liệu cá nhân hay tài liệu mật của tổ chức làm dữ liệu mẫu hoặc kiểm thử.
- Không xóa bài kiểm thử, nới lỏng kiểm tra dữ liệu hoặc bỏ qua lỗi chỉ để kiểm thử báo thành công.

## 8. Kiểm thử và đánh giá

### 8.1. Kiểm thử chức năng bắt buộc

- Tải PDF/TXT hợp lệ thành công; văn bản được lưu và lập chỉ mục.
- Tệp lỗi, tệp trống hoặc vượt dung lượng được thông báo rõ ràng.
- Câu trả lời dựa trên tài liệu được chọn và có nguồn tham chiếu hợp lệ.
- Với câu hỏi không có bằng chứng, hệ thống không bịa nội dung hoặc nguồn trích dẫn.
- Trích xuất công việc trả dữ liệu đúng cấu trúc; chưa lưu nếu chưa được xác nhận.
- Công việc đã xác nhận được lưu bền vững; các chức năng xem, sửa, xóa hoạt động.
- Có kiểm thử cho lỗi xác thực dữ liệu API và lỗi cơ sở dữ liệu.

### 8.2. Đánh giá chất lượng AI

Tạo bộ dữ liệu đánh giá nhỏ bằng **tài liệu giả lập**, kèm kết quả mong đợi. Theo dõi ít nhất:

- **Chất lượng tìm kiếm:** Chunk phù hợp có xuất hiện trong `top-k` hay không.
- **Độ bám sát nguồn:** Nội dung câu trả lời có được tài liệu trích dẫn hỗ trợ hay không.
- **Độ chính xác khi trích xuất:** Tỷ lệ công việc được đề xuất thực sự có căn cứ trong tài liệu.
- **Độ bao phủ:** Các công việc được nêu rõ trong tài liệu có được trích xuất đầy đủ hay không.
- **Thời gian và chi phí:** Thời gian phản hồi và chi phí token/API ước tính cho các luồng tiêu biểu.

Sử dụng cùng bộ dữ liệu đánh giá, ghi lại phiên bản mô hình, prompt và tham số tìm kiếm. Kết quả đo lường không phải cam kết về độ chính xác tuyệt đối.

## 9. Lộ trình phát triển

### Giai đoạn 1 — Nền tảng hoạt động

- Khởi tạo frontend, backend, cơ sở dữ liệu, biến môi trường và API kiểm tra tình trạng dịch vụ.
- Thiết lập migration và hướng dẫn chạy cục bộ.
- Định nghĩa mô hình dữ liệu, kiểu dữ liệu API và dữ liệu mẫu tối thiểu.

**Hoàn thành khi:** Người mới có thể khởi chạy hệ thống và gọi `/api/health` thành công.

### Giai đoạn 2 — Xử lý và tìm kiếm tài liệu

- Tải lên, đọc, chia chunk, tạo embedding và tìm kiếm trong tài liệu đã chọn.
- Lưu thông tin tài liệu/chunk và trả về kết quả tìm kiếm có thể kiểm tra.

**Hoàn thành khi:** Có thể tìm kiếm nội dung tệp mẫu sau khi tải lên; tệp không hợp lệ được xử lý đúng.

### Giai đoạn 3 — Hỏi đáp dựa trên tài liệu

- Xây dựng luồng sinh câu trả lời bằng RAG, dẫn nguồn và xử lý khi thiếu bằng chứng.
- Tạo giao diện hỏi đáp và các bài kiểm thử liên quan.

**Hoàn thành khi:** Câu hỏi có căn cứ được trả lời kèm nguồn thật; câu hỏi thiếu căn cứ được phản hồi phù hợp.

### Giai đoạn 4 — Trích xuất và quản lý công việc

- Tạo đề xuất công việc có cấu trúc, giao diện xem xét/xác nhận, lưu trữ và các chức năng CRUD.

**Hoàn thành khi:** Có thể trích xuất công việc từ tài liệu, kiểm tra, lưu, chỉnh sửa và xóa.

### Giai đoạn 5 — Hoàn thiện portfolio

- Bổ sung kiểm thử toàn luồng, đánh giá AI bằng dữ liệu giả lập, cấu hình Docker, README, sơ đồ kiến trúc và kịch bản demo.

**Hoàn thành khi:** Người khác có thể cài đặt, kiểm thử và trình diễn dự án theo tài liệu hướng dẫn.

## 10. Tài liệu cần duy trì

- `README.md`: Bài toán, chức năng MVP, kiến trúc, yêu cầu cài đặt, biến môi trường, cách chạy/kiểm thử, ảnh hoặc video demo, các giới hạn hiện tại.
- `docs/architecture.md`: Các thành phần hệ thống, luồng dữ liệu, cơ sở dữ liệu/chỉ mục vector và lý do lựa chọn kiến trúc.
- `docs/api.md`: Danh sách API và ví dụ yêu cầu/phản hồi.
- `docs/evaluation.md`: Bộ dữ liệu, phương pháp đo, kết quả tìm kiếm/trả lời/trích xuất và phân tích lỗi.
- `docs/decisions/`: Ghi chép ngắn về các quyết định kỹ thuật quan trọng.
- `samples/`: Tài liệu mẫu giả lập và tình huống demo.

Khi viết CV hoặc trình bày phỏng vấn, chỉ mô tả những gì **đã triển khai và có thể chứng minh**. Không trình bày tính năng mới nằm trong kế hoạch như thể đã hoàn thành.

## 11. Nguyên tắc ra quyết định

Khi phải lựa chọn giữa các phương án, ưu tiên theo thứ tự:

1. **Chức năng đúng và MVP chạy trọn vẹn.**
2. **Kết quả AI có thể đối chiếu với bằng chứng trong tài liệu.**
3. **Mã nguồn đơn giản, dễ hiểu, dễ kiểm thử.**
4. **Cài đặt lại dễ dàng và xử lý lỗi đáng tin cậy.**
5. **Tối ưu hiệu năng và tính năng nâng cao.**

Khi yêu cầu chưa rõ: kiểm tra quy ước hiện có của repository, chọn phương án đơn giản có thể thay đổi về sau và ghi lại giả định quan trọng. Nếu người dùng yêu cầu khác với tài liệu này, ưu tiên yêu cầu trực tiếp của người dùng và nêu rõ đánh đổi kỹ thuật.

---

**Quy trình bắt đầu của agent:** Đọc `AGENTS.md` → kiểm tra repository → xác định giai đoạn hiện tại → triển khai phần nhỏ nhất hoạt động hoàn chỉnh → kiểm thử → cập nhật tài liệu → báo cáo kết quả có bằng chứng.

## 12. Quy ước commit và push

- Khi người dùng yêu cầu push, tạo commit với nội dung ngắn gọn, mô tả rõ thay đổi.
- Tiêu đề commit phải nêu thành phần hoặc hành vi cụ thể đã thay đổi; tránh chỉ ghi tên nhiệm vụ hoặc mô tả chung như "initialize project foundation".
- Gộp các file liên quan vào cùng commit theo chức năng hoặc nhiệm vụ; chỉ tách commit theo file khi thay đổi độc lập.
- Kiểm tra nội dung được stage, không commit thông tin bí mật hoặc dữ liệu người dùng.
- Quy ước này áp dụng cho những lần yêu cầu push tiếp theo trong repository.
