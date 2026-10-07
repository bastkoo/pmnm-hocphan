from flask import Flask, request, redirect, abort, make_response, jsonify, url_for
from markupsafe import escape
import csv
import io

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # JSON hiển thị tiếng Việt có dấu[cite: 3, 5]

# Dữ liệu mẫu (sao chép đúng từ đề bài)[cite: 5]
STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

# ----------------- HÀM PHỤ -----------------[cite: 6]

def average(scores):
    """Tính trung bình cộng điểm số, làm tròn 2 chữ số. Dict rỗng -> None."""[cite: 6]
    if not scores:
        return None
    vals = list(scores.values())
    return round(sum(vals) / len(vals), 2)

def rank(avg):
    """Xếp loại học lực dựa trên điểm trung bình."""[cite: 6]
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"

def student_summary(mssv):
    """Trả về dict tóm tắt thông tin sinh viên."""[cite: 6]
    if mssv not in STUDENTS:
        return None
    st = STUDENTS[mssv]
    avg = average(st["scores"])
    return {
        "mssv": mssv,
        "name": st["name"],
        "lop": st["lop"],
        "scores": st["scores"],
        "average": avg,
        "rank": rank(avg)
    }

def layout(title, body):
    """Khung HTML dùng chung cho giao diện web."""[cite: 6]
    title_escaped = escape(title)
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{title_escaped} - Sổ điểm</title>
</head>
<body>
    <header>
        <nav>
            <a href="{url_for('index')}">Trang chủ</a> | 
            <a href="{url_for('student_list')}">Sinh viên</a> | 
            <a href="{url_for('search_student')}">Tìm kiếm sinh viên</a>
        </nav>
    </header>
    <hr>
    <main>
        {body}
    </main>
</body>
</html>"""