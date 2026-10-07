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
# ----------------- PHẦN 1: GIAO DIỆN WEB -----------------

# Câu 1. Trang chủ[cite: 8]
@app.route("/")
def index():
    total_students = len(STUDENTS)
    lops = sorted(list(set(st["lop"] for st in STUDENTS.values())))
    total_classes = len(lops)
    
    body = f"""
    <h1>Trang chủ Sổ điểm</h1>
    <p>Tổng số sinh viên: <strong>{total_students}</strong></p>
    <p>Số lớp: <strong>{total_classes}</strong> ({", ".join(lops)})</p>
    <ul>
        <li><a href="{url_for('student_list')}">Xem danh sách sinh viên (Web)</a></li>
        <li><a href="{url_for('api_students')}">Xem danh sách sinh viên (API JSON)</a></li>
    </ul>
    """
    return layout("Trang chủ", body)

# Câu 2. Danh sách sinh viên & Lọc theo lớp[cite: 8]
@app.route("/students")
def student_list():
    lop_filter = request.args.get("lop", "").strip()
    
    # Lấy danh sách tất cả các lớp để làm thanh lọc[cite: 8]
    all_lops = sorted(list(set(st["lop"] for st in STUDENTS.values())))
    
    # Thanh lọc Tất cả | K47A | K47B ...[cite: 8]
    nav_links = [f'<a href="{url_for("student_list")}">Tất cả</a>']
    for l in all_lops:
        nav_links.append(f'<a href="{url_for("student_list", lop=l)}">{escape(l)}</a>')
    filter_bar = " | ".join(nav_links)
    
    # Lọc danh sách sinh viên[cite: 8]
    filtered = []
    for mssv, st in STUDENTS.items():
        if not lop_filter or st["lop"].lower() == lop_filter.lower():
            summary = student_summary(mssv)
            filtered.append(summary)
            
    if not filtered:
        table_html = "<p>Không có sinh viên phù hợp.</p>"[cite: 8]
    else:
        rows = []
        for s in filtered:
            avg_str = f"{s['average']:.2f}" if s['average'] is not None else "-"[cite: 8]
            detail_url = url_for("student_detail", mssv=s["mssv"])
            rows.append(f"""
            <tr>
                <td><a href="{detail_url}">{escape(s['mssv'])}</a></td>
                <td>{escape(s['name'])}</td>
                <td>{escape(s['lop'])}</td>
                <td>{avg_str}</td>
                <td>{escape(s['rank'])}</td>
            </tr>
            """)
        table_html = f"""
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr>
                    <th>MSSV</th>
                    <th>Họ tên</th>
                    <th>Lớp</th>
                    <th>Điểm TB</th>
                    <th>Xếp loại</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
        
    body = f"""
    <h2>Danh sách sinh viên</h2>
    <p>Lọc lớp: {filter_bar}</p>
    {table_html}
    """
    return layout("Danh sách sinh viên", body)

# Câu 3. Trang chi tiết sinh viên[cite: 9]
@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")[cite: 9]
        
    s = student_summary(mssv)
    lop_url = url_for("student_list", lop=s["lop"])[cite: 9]
    export_url = url_for("export_csv", mssv=mssv)[cite: 10]
    short_url = url_for("short_student", mssv=mssv)[cite: 10]
    
    scores_rows = []
    for hp, diem in s["scores"].items():
        scores_rows.append(f"<tr><td>{escape(hp)}</td><td>{diem}</td></tr>")
        
    scores_table = f"""
    <table border="1" cellpadding="5" cellspacing="0">
        <thead><tr><th>Học phần</th><th>Điểm</th></tr></thead>
        <tbody>{''.join(scores_rows) if scores_rows else '<tr><td colspan="2">Chưa có điểm học phần nào</td></tr>'}</tbody>
    </table>
    """
    
    avg_str = f"{s['average']:.2f}" if s['average'] is not None else "Chưa có điểm"
    
    body = f"""
    <h2>Chi tiết sinh viên: {escape(s['name'])}</h2>
    <p><strong>MSSV:</strong> {escape(s['mssv'])}</p>
    <p><strong>Lớp:</strong> <a href="{lop_url}">{escape(s['lop'])}</a></p>
    <p><strong>Điểm TB:</strong> {avg_str}</p>
    <p><strong>Xếp loại:</strong> {escape(s['rank'])}</p>
    <p><strong>Link rút gọn:</strong> <a href="{short_url}">{request.host_url[:-1]}{short_url}</a></p>
    <p><a href="{export_url}">Tải bảng điểm (CSV)</a></p>
    <h3>Bảng điểm chi tiết</h3>
    {scores_table}
    """
    return layout(f"Sinh viên {s['name']}", body)

# Câu 4. Link rút gọn 301[cite: 9]
@app.route("/sv/<mssv>")
def short_student(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)[cite: 9]

# Câu 5. Xuất bảng điểm CSV[cite: 10]
@app.route("/students/<mssv>/export")
def export_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")[cite: 10]
        
    st = STUDENTS[mssv]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["hoc_phan", "diem"])[cite: 10]
    for hp, diem in st["scores"].items():
        writer.writerow([hp, diem])
        
    response = make_response(output.getvalue())[cite: 10]
    response.headers["Content-Type"] = "text/csv; charset=utf-8"[cite: 10]
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"[cite: 10]
    return response

# Câu 6. Tìm kiếm an toàn (chống XSS)[cite: 11]
@app.route("/search")
def search_student():
    q = request.args.get("q", "").strip()
    q_escaped = escape(q)  # Escape an toàn cho thuộc tính value và hiển thị[cite: 3, 11]
    
    results = []
    if q:
        q_lower = q.lower()
        for mssv, st in STUDENTS.items():
            if q_lower in mssv.lower() or q_lower in st["name"].lower():
                results.append(student_summary(mssv))
                
    if q:
        result_header = f"<h3>Tìm thấy {len(results)} kết quả cho “{q_escaped}”</h3>"[cite: 11]
    else:
        result_header = ""
        
    items = []
    for s in results:
        items.append(f'<li><a href="{url_for("student_detail", mssv=s["mssv"])}">{escape(s["mssv"])} - {escape(s["name"])}</a> ({escape(s["lop"])})</li>')
        
    body = f"""
    <h2>Tìm kiếm sinh viên</h2>
    <form action="{url_for('search_student')}" method="GET">
        <input type="text" name="q" value="{q_escaped}" placeholder="Nhập tên hoặc MSSV...">
        <button type="submit">Tìm kiếm</button>
    </form>
    {result_header}
    <ul>{''.join(items)}</ul>
    """
    return layout("Tìm kiếm", body)

# ----------------- PHẦN 1: GIAO DIỆN WEB -----------------

# Câu 1. Trang chủ[cite: 8]
@app.route("/")
def index():
    total_students = len(STUDENTS)
    lops = sorted(list(set(st["lop"] for st in STUDENTS.values())))
    total_classes = len(lops)
    
    body = f"""
    <h1>Trang chủ Sổ điểm</h1>
    <p>Tổng số sinh viên: <strong>{total_students}</strong></p>
    <p>Số lớp: <strong>{total_classes}</strong> ({", ".join(lops)})</p>
    <ul>
        <li><a href="{url_for('student_list')}">Xem danh sách sinh viên (Web)</a></li>
        <li><a href="{url_for('api_students')}">Xem danh sách sinh viên (API JSON)</a></li>
    </ul>
    """
    return layout("Trang chủ", body)

# Câu 2. Danh sách sinh viên & Lọc theo lớp[cite: 8]
@app.route("/students")
def student_list():
    lop_filter = request.args.get("lop", "").strip()
    
    # Lấy danh sách tất cả các lớp để làm thanh lọc[cite: 8]
    all_lops = sorted(list(set(st["lop"] for st in STUDENTS.values())))
    
    # Thanh lọc Tất cả | K47A | K47B ...[cite: 8]
    nav_links = [f'<a href="{url_for("student_list")}">Tất cả</a>']
    for l in all_lops:
        nav_links.append(f'<a href="{url_for("student_list", lop=l)}">{escape(l)}</a>')
    filter_bar = " | ".join(nav_links)
    
    # Lọc danh sách sinh viên[cite: 8]
    filtered = []
    for mssv, st in STUDENTS.items():
        if not lop_filter or st["lop"].lower() == lop_filter.lower():
            summary = student_summary(mssv)
            filtered.append(summary)
            
    if not filtered:
        table_html = "<p>Không có sinh viên phù hợp.</p>"[cite: 8]
    else:
        rows = []
        for s in filtered:
            avg_str = f"{s['average']:.2f}" if s['average'] is not None else "-"[cite: 8]
            detail_url = url_for("student_detail", mssv=s["mssv"])
            rows.append(f"""
            <tr>
                <td><a href="{detail_url}">{escape(s['mssv'])}</a></td>
                <td>{escape(s['name'])}</td>
                <td>{escape(s['lop'])}</td>
                <td>{avg_str}</td>
                <td>{escape(s['rank'])}</td>
            </tr>
            """)
        table_html = f"""
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr>
                    <th>MSSV</th>
                    <th>Họ tên</th>
                    <th>Lớp</th>
                    <th>Điểm TB</th>
                    <th>Xếp loại</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
        
    body = f"""
    <h2>Danh sách sinh viên</h2>
    <p>Lọc lớp: {filter_bar}</p>
    {table_html}
    """
    return layout("Danh sách sinh viên", body)

# Câu 3. Trang chi tiết sinh viên[cite: 9]
@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")[cite: 9]
        
    s = student_summary(mssv)
    lop_url = url_for("student_list", lop=s["lop"])[cite: 9]
    export_url = url_for("export_csv", mssv=mssv)[cite: 10]
    short_url = url_for("short_student", mssv=mssv)[cite: 10]
    
    scores_rows = []
    for hp, diem in s["scores"].items():
        scores_rows.append(f"<tr><td>{escape(hp)}</td><td>{diem}</td></tr>")
        
    scores_table = f"""
    <table border="1" cellpadding="5" cellspacing="0">
        <thead><tr><th>Học phần</th><th>Điểm</th></tr></thead>
        <tbody>{''.join(scores_rows) if scores_rows else '<tr><td colspan="2">Chưa có điểm học phần nào</td></tr>'}</tbody>
    </table>
    """
    
    avg_str = f"{s['average']:.2f}" if s['average'] is not None else "Chưa có điểm"
    
    body = f"""
    <h2>Chi tiết sinh viên: {escape(s['name'])}</h2>
    <p><strong>MSSV:</strong> {escape(s['mssv'])}</p>
    <p><strong>Lớp:</strong> <a href="{lop_url}">{escape(s['lop'])}</a></p>
    <p><strong>Điểm TB:</strong> {avg_str}</p>
    <p><strong>Xếp loại:</strong> {escape(s['rank'])}</p>
    <p><strong>Link rút gọn:</strong> <a href="{short_url}">{request.host_url[:-1]}{short_url}</a></p>
    <p><a href="{export_url}">Tải bảng điểm (CSV)</a></p>
    <h3>Bảng điểm chi tiết</h3>
    {scores_table}
    """
    return layout(f"Sinh viên {s['name']}", body)

# Câu 4. Link rút gọn 301[cite: 9]
@app.route("/sv/<mssv>")
def short_student(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)[cite: 9]

# Câu 5. Xuất bảng điểm CSV[cite: 10]
@app.route("/students/<mssv>/export")
def export_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")[cite: 10]
        
    st = STUDENTS[mssv]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["hoc_phan", "diem"])[cite: 10]
    for hp, diem in st["scores"].items():
        writer.writerow([hp, diem])
        
    response = make_response(output.getvalue())[cite: 10]
    response.headers["Content-Type"] = "text/csv; charset=utf-8"[cite: 10]
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"[cite: 10]
    return response

# Câu 6. Tìm kiếm an toàn (chống XSS)[cite: 11]
@app.route("/search")
def search_student():
    q = request.args.get("q", "").strip()
    q_escaped = escape(q)  # Escape an toàn cho thuộc tính value và hiển thị[cite: 3, 11]
    
    results = []
    if q:
        q_lower = q.lower()
        for mssv, st in STUDENTS.items():
            if q_lower in mssv.lower() or q_lower in st["name"].lower():
                results.append(student_summary(mssv))
                
    if q:
        result_header = f"<h3>Tìm thấy {len(results)} kết quả cho “{q_escaped}”</h3>"[cite: 11]
    else:
        result_header = ""
        
    items = []
    for s in results:
        items.append(f'<li><a href="{url_for("student_detail", mssv=s["mssv"])}">{escape(s["mssv"])} - {escape(s["name"])}</a> ({escape(s["lop"])})</li>')
        
    body = f"""
    <h2>Tìm kiếm sinh viên</h2>
    <form action="{url_for('search_student')}" method="GET">
        <input type="text" name="q" value="{q_escaped}" placeholder="Nhập tên hoặc MSSV...">
        <button type="submit">Tìm kiếm</button>
    </form>
    {result_header}
    <ul>{''.join(items)}</ul>
    """
    return layout("Tìm kiếm", body)

# ----------------- PHẦN 2: API JSON -----------------

# Câu 7. API đọc dữ liệu sinh viên[cite: 13]
@app.route("/api/students", methods=["GET"])
def api_students():
    lop_filter = request.args.get("lop", None)
    min_avg_raw = request.args.get("min_avg", None)
    
    min_avg = None
    if min_avg_raw is not None:
        try:
            min_avg = float(min_avg_raw)
        except ValueError:
            # Tham số sai kiểu -> Trả về lỗi 400[cite: 13]
            abort(400, description="Tham số min_avg phải là một số thực hợp lệ.")
            
    res = []
    for mssv in STUDENTS:
        s = student_summary(mssv)
        
        # Lọc theo lớp[cite: 13]
        if lop_filter and s["lop"].lower() != lop_filter.lower():
            continue
            
        # Lọc theo min_avg (bỏ qua sinh viên chưa có điểm)[cite: 13]
        if min_avg is not None:
            if s["average"] is None or s["average"] < min_avg:
                continue
                
        res.append(s)
        
    return jsonify(res)

@app.route("/api/students/<mssv>", methods=["GET"])
def api_student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không tìm thấy sinh viên với MSSV = {mssv}.")[cite: 13]
    return jsonify(student_summary(mssv))

# Câu 8. API Quản lý điểm học phần[cite: 14]
@app.route("/api/students/<mssv>/scores/<course>", methods=["GET", "PUT", "DELETE", "POST"])
def api_student_course_score(mssv, course):
    if request.method == "POST":
        abort(405, description="Phương thức POST không được hỗ trợ trên endpoint này.")[cite: 14]
        
    if mssv not in STUDENTS:
        abort(404, description=f"Không tìm thấy sinh viên với MSSV = {mssv}.")[cite: 14]
        
    st = STUDENTS[mssv]
    course_upper = course.upper()  # Luôn lưu & xử lý dạng chữ hoa[cite: 14]
    
    if request.method == "GET":
        if course_upper not in st["scores"]:
            abort(404, description=f"Chưa có điểm cho học phần {course_upper}.")[cite: 14]
        return jsonify({
            "mssv": mssv,
            "course": course_upper,
            "score": st["scores"][course_upper]
        })
        
    elif request.method == "PUT":
        score_raw = request.args.get("score", None)
        if score_raw is None:
            abort(400, description="Thiếu tham số score.")[cite: 14]
            
        try:
            score_val = float(score_raw)
        except ValueError:
            abort(400, description="Giá trị score phải là một số.")[cite: 14]
            
        if score_val < 0 or score_val > 10:
            abort(400, description="Điểm phải nằm trong khoảng [0, 10].")[cite: 14]
            
        is_new = course_upper not in st["scores"]
        st["scores"][course_upper] = score_val  # Cập nhật điểm
        
        avg = average(st["scores"])
        resp_data = {
            "mssv": mssv,
            "course": course_upper,
            "score": score_val,
            "average": avg
        }
        
        if is_new:
            # Thêm mới: trả mã 201 + Location header[cite: 14]
            resp = make_response(jsonify(resp_data), 201)
            resp.headers["Location"] = url_for("api_student_course_score", mssv=mssv, course=course_upper)
            return resp
        else:
            # Sửa điểm: trả mã 200[cite: 14]
            return jsonify(resp_data), 200
            
    elif request.method == "DELETE":
        if course_upper not in st["scores"]:
            abort(404, description=f"Không thể xoá. Học phần {course_upper} chưa có điểm.")[cite: 14]
            
        del st["scores"][course_upper]
        return "", 204  # Trả về 204 No Content[cite: 14]

# ----------------- PHẦN 3: XỬ LÝ LỖI -----------------

# Câu 9. Trang lỗi thống nhất[cite: 16]
@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    status_code = error.code if hasattr(error, 'code') else 500
    
    titles = {
        400: "Dữ liệu không hợp lệ",
        404: "Không tìm thấy",
        405: "Phương thức không được hỗ trợ"
    }
    title = titles.get(status_code, "Lỗi hệ thống")
    description = getattr(error, 'description', str(error))
    
    # Nếu đường dẫn bắt đầu bằng /api/ -> Trả về JSON[cite: 16]
    if request.path.startswith("/api/"):
        return jsonify({
            "error": title,
            "detail": description
        }), status_code
    
    # URL khác -> Trả về giao diện HTML sử dụng layout()[cite: 16]
    body = f"""
    <h2>Lỗi {status_code}: {escape(title)}</h2>
    <p>{escape(description)}</p>
    <p><a href="{url_for('index')}">Quay lại Trang chủ</a></p>
    """
    return layout(f"Lỗi {status_code}", body), status_code

if __name__ == "__main__":
    app.run(port=8000, debug=True)