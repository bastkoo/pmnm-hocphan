# Tổng hợp bài tập Flask

Thư mục này chạy độc lập, chứa bản sao của `Chuong3`, `chuong_03`,
`Chuong4`, `Chuong5`, `Chuong6` và `BaiKiemTra`.
`chuong_03` là tên thư mục thực tế của phần được gọi là `chuong_3`.
Các thư mục gốc bên ngoài `TongHop` được giữ nguyên.
Không sao chép môi trường ảo và bộ nhớ đệm Python.

## Cách chạy

Yêu cầu Python 3.10 trở lên. Từ thư mục `TongHop`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Nếu máy dùng lệnh `py`, thay `python -m venv .venv` bằng `py -m venv .venv`.

Hoặc dùng môi trường ảo đã có ở thư mục dự án, nếu đã cài đủ thư viện:

```powershell
# Chạy từ thư mục gốc pmnm-hocphan
.\.venv\Scripts\python.exe TongHop\app.py
```

Mở **http://127.0.0.1:5000/**. Nhấn `Ctrl+C` trong terminal để dừng.
Trong IDE có thể chọn Python interpreter đã cài requirements rồi chạy `TongHop/app.py`.

## Các phần

| Đường dẫn | Nội dung |
| --- | --- |
| `/` | Trang tổng hợp và navbar chuyển chương |
| `/chuong3/` | Routing và phép tính cơ bản |
| `/chuong3/thu-vien/` | Bài thư viện của Chương 3 |
| `/chuong_03/` | Sổ điểm, tìm kiếm, API JSON và CSV |
| `/chuong4/` | Quán cà phê và thực đơn phân trang |
| `/chuong5/` | Máy tính, điểm học phần và BMI |
| `/chuong6/` | Trang chọn bài SQLAlchemy |
| `/chuong6/ds-sinh-vien` | Danh sách sinh viên |
| `/chuong6/them-mau` | Thêm mẫu khi bảng sinh viên rỗng |
| `/chuong6/thu-truy-van` | Thực hành truy vấn (kết quả văn bản) |
| `/bai-kiem-tra/` | Quản lý sách và danh mục |

`app.py` dùng `DispatcherMiddleware` để mỗi ứng dụng có đường dẫn riêng,
tránh trùng tên route, template và static. Navbar được thêm vào các phản hồi
HTML; API JSON, file CSV và phản hồi văn bản giữ nguyên định dạng.

Dữ liệu SQLite đã được sao chép cùng thư mục `instance` của từng bài.
Các thay đổi dữ liệu trong bản tổng hợp chỉ lưu vào bản sao bên trong `TongHop`.
Nếu chưa có cơ sở dữ liệu, ứng dụng tự tạo bảng khi khởi động.
Giao diện một số chương dùng Bootstrap, Font Awesome hoặc Google Fonts qua CDN,
cần Internet để tải đầy đủ các thành phần giao diện đó.

## Kiểm tra

```powershell
# Từ thư mục gốc, dùng môi trường đã cài đủ requirements
.\.venv\Scripts\python.exe TongHop\test_app.py
```

Bộ kiểm tra chạy trên bản sao trong thư mục tạm: trang HTML và navbar,
liên kết, static, form, API, CSV, chuyển hướng, CRUD thư viện và cơ sở dữ liệu riêng.
