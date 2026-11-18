# Chương 6 - Bài tập Nhà sách Sông Hương

Ứng dụng Flask độc lập, thực hiện cả phần A (bán hàng) và phần B (quản trị) trong đề. Dùng SQLite, SQLAlchemy, Flask-WTF, Flask-Migrate, Jinja2 và Bootstrap 5. Tiền được lưu bằng số nguyên VNĐ, thời gian theo UTC+7.

## Cài đặt và chạy (PowerShell)

Mở terminal tại thư mục `chuong6_btgiohang`:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app db upgrade
.\.venv\Scripts\python.exe -m flask --app app seed
.\.venv\Scripts\python.exe -m flask --app app run --debug
```

Nếu máy dùng lệnh `python` thay cho `py`, thay lệnh đầu bằng `python -m venv .venv`. Không cần kích hoạt môi trường ảo.

Truy cập **http://127.0.0.1:5000/books**, quản trị tại **http://127.0.0.1:5000/admin**. CSDL và khoá session được tạo trong `instance/`; ảnh tải lên ở `static/uploads/`. Lệnh `seed` không thêm trùng dữ liệu. Dữ liệu mẫu có 6 sách, 6 danh mục (1 danh mục rỗng), 1 đơn chờ xác nhận trị giá 460.000 đ; tồn kho đã trừ tương ứng.

Đây là bài thực hành chạy trên máy cá nhân; `/admin` truy cập trực tiếp theo phạm vi đề, chưa có tài khoản đăng nhập. Bootstrap được lưu cục bộ trong `static/bootstrap.min.css` (kèm thông tin bản quyền MIT ở đầu tệp), dùng được khi không có Internet; CSS riêng và tất cả xử lý nghiệp vụ nằm trong dự án. Không có cổng thanh toán thật: lựa chọn chuyển khoản được ghi nhận trên đơn để nhà sách liên hệ.

## Các chức năng đã thực hiện

| Màn hình | Đường dẫn | Nội dung |
|---|---|---|
| ① Danh sách | `/books` | Tìm tên/tác giả, lọc danh mục, bìa, giá, tồn kho; thêm 1 cuốn, giữ bộ lọc; badge tổng số cuốn |
| ② Chi tiết | `/books/<id>` | Thông tin đầy đủ; nút −/+; kiểm tra số lượng server theo tồn kho trừ số đã có trong giỏ; 404 |
| ③ Giỏ hàng | `/cart` | Session chỉ giữ id và số lượng; giá mới nhất; tăng/giảm/xoá; xác nhận xoá toàn bộ; giỏ rỗng |
| ④ Đặt hàng | `/checkout` | Flask-WTF, xác thực thông tin; phí 20.000 đ, miễn phí từ 200.000 đ; giao dịch tạo đơn/trừ kho/xoá giỏ |
| ⑤ Thành công | `/orders/<id>` | Chi tiết đơn vừa đặt và lịch sử; chỉ trình duyệt đã đặt đơn xem được |
| ⑥ Tổng quan | `/admin` | 4 truy vấn thống kê, doanh thu đơn hoàn tất theo tháng hoàn tất, 5 đơn mới nhất, sách ≤ 5 |
| ⑦ Sách | `/admin/books` | 5 sách/trang, mới trước; tìm/lọc/giữ bộ lọc; chặn xoá sách có trong đơn |
| ⑧ Thêm/sửa | `/admin/books/new`, `/admin/books/<id>/edit` | Chung form/template; tên duy nhất không phân biệt hoa thường; kiểm tra giá/tồn/năm; danh mục từ CSDL; ảnh ≤ 2 MB |
| ⑨ Danh mục | `/admin/categories` | Đếm sách bằng outer join + group_by; thêm/sửa/chặn trùng; chặn xoá danh mục còn sách; liên kết lọc sách |
| ⑩ Đơn hàng | `/admin/orders` | Tab kèm số lượng group_by, tìm mã/tên/SĐT, 10 đơn/trang, tổng giá trị theo bộ lọc |
| ⑪ Chi tiết quản trị | `/admin/orders/<id>` | Giá lúc đặt; chuyển trạng thái hợp lệ; huỷ hoàn kho đúng một lần; lịch sử thời điểm |

Các thao tác thay đổi dữ liệu dùng POST, CSRF, flash và chuyển hướng PRG. CSRF sai/hết hạn được báo riêng. Tên sách/danh mục có cột khoá `casefold()` để kiểm tra trùng cả tiếng Việt. Ảnh được kiểm tra nội dung, đổi tên UUID, mã hoá lại WEBP và xoá ảnh cũ sau khi lưu thành công. Tồn kho được cập nhật có điều kiện trong giao dịch; một cuốn thiếu hàng thì rollback cả đơn. Đơn hoàn tất/đã huỷ không cho đổi tiếp; cập nhật trạng thái có điều kiện tránh hoàn kho hai lần.

Trang tổng quan có biểu đồ cột doanh thu 7 ngày gần nhất (gồm hôm nay), theo giờ Việt Nam UTC+7. Doanh thu được nhóm bằng một truy vấn theo ngày hoàn tất đơn, chỉ tính đơn Hoàn tất và bao gồm phí giao hàng; ngày không có đơn hiển thị 0. Có tổng doanh thu, số đơn, mức doanh thu cao nhất trong ngày, tooltip khi di chuột/chọn bằng bàn phím và bảng số liệu chi tiết. Biểu đồ dùng HTML/CSS và icon SVG cục bộ, không cần CDN hay thư viện biểu đồ. Khi chưa có đơn hoàn tất, biểu đồ hiển thị trạng thái trống; không thêm doanh thu giả vào dữ liệu mẫu.

## Migration

Đã có migration khởi tạo trong `migrations/`. Sau khi sửa model:

```powershell
.\.venv\Scripts\python.exe -m flask --app app db migrate -m "Mo ta thay doi"
.\.venv\Scripts\python.exe -m flask --app app db upgrade
```

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Kiểm thử dùng SQLite tạm, không sửa dữ liệu đang chạy. Bao gồm session/CSRF, đặt hàng, thiếu tồn kho và rollback, giá tại thời điểm đặt, phí giao hàng, chuyển trạng thái/hoàn kho, quản trị và ảnh tải lên.

## Cấu trúc

```text
app.py          # app factory, route bán hàng/quản trị, giao dịch, upload
models.py       # Category, Book, Order, OrderItem, OrderHistory
forms.py        # Flask-WTF và xác thực
seed.py         # dữ liệu mẫu
templates/      # giao diện Jinja2, macro dùng chung
static/         # CSS, JavaScript, ảnh người dùng tải lên
migrations/     # Alembic / Flask-Migrate
tests/          # kiểm thử bằng unittest và Flask test client
```

