# BÁO CÁO KIỂM THỬ VÀ TRẢ LỜI CÂU HỎI - BÀI TẬP TỔNG HỢP CHƯƠNG 3
## 1. Kết quả chạy lệnh `flask --app sodiem routes`
```text
Endpoint                  Methods  Rule
------------------------  -------  -----------------------------------------
api_student_course_score  DELETE, GET, POST, PUT  /api/students/<mssv>/scores/<course>
api_student_detail        GET      /api/students/<mssv>
api_students              GET      /api/students
export_csv                GET      /students/<mssv>/export
index                     GET      /
search_student            GET      /search
short_student             GET      /sv/<mssv>
static                    GET      /static/<filename>
student_detail            GET      /students/<mssv>
student_list              GET      /students
```

---

## 2. Kết quả kiểm thử bằng cURL

### Khai báo biến môi trường:
```bash
B=http://127.0.0.1:8000
S=$B/api/students/23T1020005/scores
```

---

### Lệnh 1: `curl -i $B/sv/23T1020001`
- **Dòng trạng thái:** `HTTP/1.1 301 MOVED PERMANENTLY`
- **Header quan trọng:** `Location: /students/23T1020001`

---

### Lệnh 2: `curl -i $B/students/23T1020001/export`
- **Dòng trạng thái:** `HTTP/1.1 200 OK`
- **Headers quan trọng:** 
  - `Content-Type: text/csv; charset=utf-8`
  - `Content-Disposition: attachment; filename=diem_23T1020001.csv`
- **Body:**
```csv
hoc_phan,diem
PMMNM,8.5
CSDL,7.0
MMT,9.0
```

---

### Lệnh 3: `curl "$B/api/students?lop=k47a&min_avg=7"`
- **Dòng trạng thái:** `HTTP/1.1 200 OK`
- **Body (JSON):**
```json
[
  {
    "average": 8.17,
    "lop": "K47A",
    "mssv": "23T1020001",
    "name": "Nguyễn Văn An",
    "rank": "Khá",
    "scores": {
      "CSDL": 7.0,
      "MMT": 9.0,
      "PMMNM": 8.5
    }
  }
]
```

---

### Lệnh 4: `curl -i "$B/api/students?min_avg=abc"`
- **Dòng trạng thái:** `HTTP/1.1 400 BAD REQUEST`
- **Body (JSON):**
```json
{
  "detail": "Tham số min_avg phải là một số thực hợp lệ.",
  "error": "Dữ liệu không hợp lệ"
}
```

---

### Lệnh 5: `curl -i $B/api/students/999`
- **Dòng trạng thái:** `HTTP/1.1 404 NOT FOUND`
- **Body (JSON):**
```json
{
  "detail": "Không tìm thấy sinh viên với MSSV = 999.",
  "error": "Không tìm thấy"
}
```

---

### Lệnh 6: `curl -i -X PUT "$S/web?score=9"`
- **Dòng trạng thái:** `HTTP/1.1 201 CREATED`
- **Header quan trọng:** `Location: /api/students/23T1020005/scores/WEB`
- **Body (JSON):**
```json
{
  "average": 9.0,
  "course": "WEB",
  "mssv": "23T1020005",
  "score": 9.0
}
```

---

### Lệnh 7: `curl -X PUT "$S/WEB?score=7.5"`
- **Dòng trạng thái:** `HTTP/1.1 200 OK`
- **Body (JSON):**
```json
{
  "average": 7.5,
  "course": "WEB",
  "mssv": "23T1020005",
  "score": 7.5
}
```

---

### Lệnh 8: `curl -i -X PUT "$S/WEB?score=11"`
- **Dòng trạng thái:** `HTTP/1.1 400 BAD REQUEST`
- **Body (JSON):**
```json
{
  "detail": "Điểm phải nằm trong khoảng [0, 10].",
  "error": "Dữ liệu không hợp lệ"
}
```

---

### Lệnh 9: `curl -i -X DELETE $S/WEB`
- **Dòng trạng thái:** `HTTP/1.1 204 NO CONTENT`
- **Body:** *(Rỗng)*

---

### Lệnh 10: `curl -i -X POST $S/WEB`
- **Dòng trạng thái:** `HTTP/1.1 405 METHOD NOT ALLOWED`
- **Body (JSON):**
```json
{
  "detail": "Phương thức POST không được hỗ trợ trên endpoint này.",
  "error": "Phương thức không được hỗ trợ"
}
```

---

### Lệnh 11: `curl -i -X POST $B/students`
- **Dòng trạng thái:** `HTTP/1.1 405 METHOD NOT ALLOWED`
- **Body (HTML):**
```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Lỗi 405 - Sổ điểm</title>
</head>
<body>
    <header>
        <nav>
            <a href="/">Trang chủ</a> | 
            <a href="/students">Sinh viên</a> | 
            <a href="/search">Tìm kiếm sinh viên</a>
        </nav>
    </header>
    <hr>
    <main>
        
    <h2>Lỗi 405: Phương thức không được hỗ trợ</h2>
    <p>The method is not allowed for the requested URL.</p>
    <p><a href="/">Quay lại Trang chủ</a></p>

    </main>
</body>
</html>
```

---

## 3. Trả lời câu hỏi ngắn

1. **Vì sao Câu 4 dùng mã `301` còn Câu 8 trả về mã `201` kèm header `Location`?**
   - **Mã `301 Moved Permanently` (Câu 4):** Là mã chuyển hướng cố định. URL `/sv/<mssv>` đóng vai trò là một liên kết rút gọn liên kết vĩnh viễn đến trang chi tiết `/students/<mssv>`. Khi trình duyệt nhận mã này, nó sẽ tự động điều hướng sang URL mới và có thể lưu vào cache cho các lần truy cập sau.
   - **Mã `201 Created` kèm header `Location` (Câu 8):** Theo chuẩn thiết kế RESTful API, mã `201` thông báo rằng một tài nguyên mới (điểm của môn học) đã được khởi tạo thành công trên server thông qua phương thức `PUT`. Header `Location` bắt buộc đi kèm để cung cấp URL truy cập trực tiếp đến tài nguyên vừa được tạo ra đó (`/api/students/<mssv>/scores/<course>`).

2. **Thêm điểm cho sinh viên `23T1020005` rồi khởi động lại server, điểm đó còn không? Vì sao?**
   - **Trả lời:** **Không còn điểm đó.**
   - **Lý do:** Dữ liệu sinh viên (`STUDENTS`) hiện tại chỉ được lưu tạm thời trên bộ nhớ RAM (biến trong RAM của tiến trình Python). Khi khởi động lại server, tiến trình Python cũ bị dừng và hủy bỏ toàn bộ bộ nhớ tạm. Server sẽ chạy lại ứng dụng từ đầu và nạp lại dictionary `STUDENTS` nguyên bản được định nghĩa cứng trong mã nguồn `sodiem.py`.