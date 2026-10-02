# DevOps Session 05 - Bài 4: Mô phỏng quy trình Hotfix và Gitflow thực tế

Bài tập môn DevOps. Thực hành mô hình phân nhánh Gitflow: tạo nhánh `hotfix/v1.0.1` từ `main` để vá lỗi lộ dữ liệu người dùng (`password_hash`), gộp vào `main` kèm tag `v1.0.1`, rồi gộp ngược về `develop`. Mọi lệnh Git đều được chạy thật và chép nguyên văn vào báo cáo.

Báo cáo chi tiết: [homework/session_05/ex4/README.md](homework/session_05/ex4/README.md)

## Danh sách file

| Đường dẫn | Nội dung |
|-----------|----------|
| `README.md` | File này |
| `homework/session_05/ex4/README.md` | Báo cáo: Gitflow, kịch bản sự cố, từng bước với output thật, sơ đồ merge, đối chiếu yêu cầu |
| `homework/session_05/ex4/terminal_log.txt` | Toàn bộ lệnh và output thật |
| `homework/session_05/ex4/gitflow_diagram.txt` | Sơ đồ ASCII: Gitflow tổng quát và sơ đồ merge của bài |
| `homework/session_05/ex4/source/` | Mã nguồn cuối cùng của nhánh `main`: `app/user_service.py`, `VERSION`, `CHANGELOG.md` |
