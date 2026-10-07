from flask import Flask, request, redirect, abort, make_response, jsonify, url_for
from markupsafe import escape
import csv
import io

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # JSON hiển thị tiếng Việt có dấu

# Dữ liệu mẫu
STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

# ----------------- HÀM PHỤ -----------------

def average(scores):
    """Tính trung bình cộng điểm số, làm tròn 2 chữ số. Dict rỗng -> None."""
    if not scores:
        return None
    vals = list(scores.values())
    return round(sum(vals) / len(vals), 2)

def rank(avg):
    """Xếp loại học lực dựa trên điểm trung bình."""
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
    """Trả về dict tóm tắt thông tin sinh viên."""
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

def get_rank_badge(rank_str):
    """Tạo badge màu sắc tùy theo xếp loại."""
    colors = {
        "Giỏi": "#10b981; background: #ecfdf5",
        "Khá": "#3b82f6; background: #eff6ff",
        "Trung bình": "#f59e0b; background: #fffbeb",
        "Yếu": "#ef4444; background: #fef2f2",
        "Chưa có điểm": "#6b7280; background: #f3f4f6"
    }
    style = colors.get(rank_str, "#6b7280; background: #f3f4f6")
    return f'<span style="padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 0.85rem; color: {style};">{escape(rank_str)}</span>'

def layout(title, body):
    """Khung HTML dùng chung với CSS styling hiện đại."""
    title_escaped = escape(title)
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_escaped} - Quản lý Sổ Điểm</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #334155;
            line-height: 1.6;
            padding-bottom: 40px;
        }}
        header {{
            background-color: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .nav-container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .brand {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #2563eb;
            text-decoration: none;
        }}
        nav a {{
            color: #64748b;
            text-decoration: none;
            margin-left: 20px;
            font-weight: 500;
            transition: color 0.2s;
        }}
        nav a:hover {{ color: #2563eb; }}
        main {{
            max-width: 1000px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        .card {{
            background: #ffffff;
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid #f1f5f9;
        }}
        h1, h2, h3 {{ color: #0f172a; margin-bottom: 16px; font-weight: 700; }}
        h1 {{ font-size: 1.75rem; }}
        h2 {{ font-size: 1.4rem; }}
        p {{ margin-bottom: 12px; color: #475569; }}
        
        /* Table Styles */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
            font-size: 0.95rem;
        }}
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background-color: #f1f5f9;
            color: #475569;
            font-weight: 600;
        }}
        tr:hover {{ background-color: #f8fafc; }}
        td a {{ color: #2563eb; font-weight: 600; text-decoration: none; }}
        td a:hover {{ text-decoration: underline; }}

        /* Filter & Buttons */
        .filter-bar {{
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 6px 14px;
            border-radius: 6px;
            background: #e2e8f0;
            color: #334155;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .filter-btn:hover {{
            background: #2563eb;
            color: white;
        }}
        
        /* Forms & Inputs */
        .search-box {{
            display: flex;
            gap: 10px;
            margin-bottom: 24px;
        }}
        input[type="text"] {{
            flex: 1;
            padding: 10px 14px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }}
        input[type="text"]:focus {{ border-color: #2563eb; }}
        button, .btn {{
            display: inline-block;
            padding: 10px 18px;
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            transition: background-color 0.2s;
        }}
        button:hover, .btn:hover {{ background-color: #1d4ed8; }}
        .btn-outline {{
            background-color: transparent;
            color: #2563eb;
            border: 1px solid #2563eb;
        }}
        .btn-outline:hover {{
            background-color: #eff6ff;
        }}
        
        /* Stat Cards */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: #f8fafc;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #2563eb;
        }}
        .stat-label {{
            font-size: 0.875rem;
            color: #64748b;
        }}
    </style>
</head>
<body>
    <header>
        <div class="nav-container">
            <a href="{url_for('index')}" class="brand">🎓 Sổ Điểm Điện Tử</a>
            <nav>
                <a href="{url_for('index')}">Trang chủ</a>
                <a href="{url_for('student_list')}">Danh sách sinh viên</a>
                <a href="{url_for('search_student')}">Tìm kiếm</a>
            </nav>
        </div>
    </header>
    <main>
        <div class="card">
            {body}
        </div>
    </main>
</body>
</html>"""

# ----------------- PHẦN 1: GIAO DIỆN WEB -----------------

# Câu 1. Trang chủ
@app.route("/")
def index():
    total_students = len(STUDENTS)
    lops = sorted(list(set(st["lop"] for st in STUDENTS.values())))
    total_classes = len(lops)
    
    body = f"""
    <h1>Trang Chủ Sổ Điểm</h1>
    <p>Hệ thống quản lý thông tin điểm thi và học phần của sinh viên.</p>
    
    <div class="stats-grid" style="margin-top: 20px;">
        <div class="stat-card">
            <div class="stat-value">{total_students}</div>
            <div class="stat-label">Tổng sinh viên</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{total_classes}</div>
            <div class="stat-label">Lớp học ({", ".join(lops)})</div>
        </div>
    </div>

    <div style="margin-top: 24px; display: flex; gap: 12px;">
        <a href="{url_for('student_list')}" class="btn">Xem danh sách sinh viên</a>
        <a href="{url_for('api_students')}" class="btn btn-outline" target="_blank">Khám phá API JSON</a>
    </div>
    """
    return layout("Trang chủ", body)

# Câu 2. Danh sách sinh viên & Lọc theo lớp
@app.route("/students")
def student_list():
    lop_filter = request.args.get("lop", "").strip()
    all_lops = sorted(list(set(st["lop"] for st in STUDENTS.values())))
    
    nav_links = [f'<a href="{url_for("student_list")}" class="filter-btn">Tất cả</a>']
    for l in all_lops:
        nav_links.append(f'<a href="{url_for("student_list", lop=l)}" class="filter-btn">{escape(l)}</a>')
    filter_bar = "".join(nav_links)
    
    filtered = []
    for mssv, st in STUDENTS.items():
        if not lop_filter or st["lop"].lower() == lop_filter.lower():
            filtered.append(student_summary(mssv))
            
    if not filtered:
        table_html = "<p style='margin-top: 20px;'>Không tìm thấy sinh viên phù hợp.</p>"
    else:
        rows = []
        for s in filtered:
            avg_str = f"{s['average']:.2f}" if s['average'] is not None else "-"
            detail_url = url_for("student_detail", mssv=s["mssv"])
            rows.append(f"""
            <tr>
                <td><a href="{detail_url}">{escape(s['mssv'])}</a></td>
                <td><strong>{escape(s['name'])}</strong></td>
                <td>{escape(s['lop'])}</td>
                <td><strong>{avg_str}</strong></td>
                <td>{get_rank_badge(s['rank'])}</td>
            </tr>
            """)
        table_html = f"""
        <table>
            <thead>
                <tr>
                    <th>MSSV</th>
                    <th>Họ và Tên</th>
                    <th>Lớp</th>
                    <th>Điểm TB</th>
                    <th>Xếp Loại</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
        
    body = f"""
    <h2>Danh Sách Sinh Viên</h2>
    <p>Lọc danh sách theo lớp:</p>
    <div class="filter-bar">{filter_bar}</div>
    {table_html}
    """
    return layout("Danh sách sinh viên", body)

# Câu 3. Trang chi tiết sinh viên
@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    s = student_summary(mssv)
    lop_url = url_for("student_list", lop=s["lop"])
    export_url = url_for("export_csv", mssv=mssv)
    short_url = url_for("short_student", mssv=mssv)
    
    scores_rows = []
    for hp, diem in s["scores"].items():
        scores_rows.append(f"<tr><td>{escape(hp)}</td><td><strong>{diem}</strong></td></tr>")
        
    scores_table = f"""
    <table>
        <thead><tr><th>Học phần</th><th>Điểm số</th></tr></thead>
        <tbody>{''.join(scores_rows) if scores_rows else '<tr><td colspan="2">Chưa có điểm học phần nào.</td></tr>'}</tbody>
    </table>
    """
    
    avg_str = f"{s['average']:.2f}" if s['average'] is not None else "Chưa có điểm"
    
    body = f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
        <div>
            <h2>{escape(s['name'])}</h2>
            <p>Mã sinh viên: <strong>{escape(s['mssv'])}</strong> | Lớp: <a href="{lop_url}"><strong>{escape(s['lop'])}</strong></a></p>
        </div>
        <div>
            {get_rank_badge(s['rank'])}
        </div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{avg_str}</div>
            <div class="stat-label">Điểm trung bình</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(s['scores'])}</div>
            <div class="stat-label">Số môn đã có điểm</div>
        </div>
    </div>

    <h3 style="margin-top: 24px;">Bảng Điểm Chi Tiết</h3>
    {scores_table}

    <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e2e8f0; display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
        <a href="{export_url}" class="btn">📥 Tải bảng điểm (CSV)</a>
        <span style="font-size: 0.9rem; color: #64748b;">
            Link rút gọn: <a href="{short_url}" target="_blank">{request.host_url[:-1]}{short_url}</a>
        </span>
    </div>
    """
    return layout(f"Sinh viên {s['name']}", body)

# Câu 4. Link rút gọn 301
@app.route("/sv/<mssv>")
def short_student(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)

# Câu 5. Xuất bảng điểm CSV
@app.route("/students/<mssv>/export")
def export_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    st = STUDENTS[mssv]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["hoc_phan", "diem"])
    for hp, diem in st["scores"].items():
        writer.writerow([hp, diem])
        
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return response

# Câu 6. Tìm kiếm an toàn (chống XSS)
@app.route("/search")
def search_student():
    q = request.args.get("q", "").strip()
    q_escaped = escape(q)
    
    results = []
    if q:
        q_lower = q.lower()
        for mssv, st in STUDENTS.items():
            if q_lower in mssv.lower() or q_lower in st["name"].lower():
                results.append(student_summary(mssv))
                
    if q:
        result_header = f"<p style='margin-bottom: 12px;'>Tìm thấy <strong>{len(results)}</strong> kết quả cho từ khóa “<strong>{q_escaped}</strong>”:</p>"
    else:
        result_header = ""
        
    rows = []
    for s in results:
        avg_str = f"{s['average']:.2f}" if s['average'] is not None else "-"
        detail_url = url_for("student_detail", mssv=s["mssv"])
        rows.append(f"""
        <tr>
            <td><a href="{detail_url}">{escape(s['mssv'])}</a></td>
            <td><strong>{escape(s['name'])}</strong></td>
            <td>{escape(s['lop'])}</td>
            <td>{avg_str}</td>
            <td>{get_rank_badge(s['rank'])}</td>
        </tr>
        """)
        
    table_html = f"""
    <table>
        <thead>
            <tr>
                <th>MSSV</th>
                <th>Họ và Tên</th>
                <th>Lớp</th>
                <th>Điểm TB</th>
                <th>Xếp Loại</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """ if rows else ""
        
    body = f"""
    <h2>Tìm Kiếm Sinh Viên</h2>
    <form action="{url_for('search_student')}" method="GET" class="search-box">
        <input type="text" name="q" value="{q_escaped}" placeholder="Nhập tên hoặc mã sinh viên cần tìm...">
        <button type="submit">Tìm kiếm</button>
    </form>
    {result_header}
    {table_html}
    """
    return layout("Tìm kiếm", body)

# ----------------- PHẦN 2: API JSON -----------------

# Câu 7. API đọc dữ liệu sinh viên
@app.route("/api/students", methods=["GET"])
def api_students():
    lop_filter = request.args.get("lop", None)
    min_avg_raw = request.args.get("min_avg", None)
    
    min_avg = None
    if min_avg_raw is not None:
        try:
            min_avg = float(min_avg_raw)
        except ValueError:
            abort(400, description="Tham số min_avg phải là một số thực hợp lệ.")
            
    res = []
    for mssv in STUDENTS:
        s = student_summary(mssv)
        
        if lop_filter and s["lop"].lower() != lop_filter.lower():
            continue
            
        if min_avg is not None:
            if s["average"] is None or s["average"] < min_avg:
                continue
                
        res.append(s)
        
    return jsonify(res)

@app.route("/api/students/<mssv>", methods=["GET"])
def api_student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không tìm thấy sinh viên với MSSV = {mssv}.")
    return jsonify(student_summary(mssv))

# Câu 8. API Quản lý điểm học phần
@app.route("/api/students/<mssv>/scores/<course>", methods=["GET", "PUT", "DELETE", "POST"])
def api_student_course_score(mssv, course):
    if request.method == "POST":
        abort(405, description="Phương thức POST không được hỗ trợ trên endpoint này.")
        
    if mssv not in STUDENTS:
        abort(404, description=f"Không tìm thấy sinh viên với MSSV = {mssv}.")
        
    st = STUDENTS[mssv]
    course_upper = course.upper()
    
    if request.method == "GET":
        if course_upper not in st["scores"]:
            abort(404, description=f"Chưa có điểm cho học phần {course_upper}.")
        return jsonify({
            "mssv": mssv,
            "course": course_upper,
            "score": st["scores"][course_upper]
        })
        
    elif request.method == "PUT":
        score_raw = request.args.get("score", None)
        if score_raw is None:
            abort(400, description="Thiếu tham số score.")
            
        try:
            score_val = float(score_raw)
        except ValueError:
            abort(400, description="Giá trị score phải là một số.")
            
        if score_val < 0 or score_val > 10:
            abort(400, description="Điểm phải nằm trong khoảng [0, 10].")
            
        is_new = course_upper not in st["scores"]
        st["scores"][course_upper] = score_val
        
        avg = average(st["scores"])
        resp_data = {
            "mssv": mssv,
            "course": course_upper,
            "score": score_val,
            "average": avg
        }
        
        if is_new:
            resp = make_response(jsonify(resp_data), 201)
            resp.headers["Location"] = url_for("api_student_course_score", mssv=mssv, course=course_upper)
            return resp
        else:
            return jsonify(resp_data), 200
            
    elif request.method == "DELETE":
        if course_upper not in st["scores"]:
            abort(404, description=f"Không thể xoá. Học phần {course_upper} chưa có điểm.")
            
        del st["scores"][course_upper]
        return "", 204

# ----------------- PHẦN 3: XỬ LÝ LỖI -----------------

# Câu 9. Trang lỗi thống nhất
@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    status_code = error.code if hasattr(error, 'code') else 500
    
    titles = {
        400: "Dữ liệu không hợp lệ",
        404: "Không tìm thấy nội dung",
        405: "Phương thức không được hỗ trợ"
    }
    title = titles.get(status_code, "Lỗi hệ thống")
    description = getattr(error, 'description', str(error))
    
    if request.path.startswith("/api/"):
        return jsonify({
            "error": title,
            "detail": description
        }), status_code
    
    body = f"""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 3rem; color: #ef4444;">{status_code}</h1>
        <h2>{escape(title)}</h2>
        <p style="margin-bottom: 20px;">{escape(description)}</p>
        <a href="{url_for('index')}" class="btn">Quay lại Trang chủ</a>
    </div>
    """
    return layout(f"Lỗi {status_code}", body), status_code

if __name__ == "__main__":
    app.run(port=8000, debug=True)