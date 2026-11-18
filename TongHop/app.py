"""Chạy toàn bộ bài tập: python app.py."""

import importlib.util
import re
import sys
from pathlib import Path

from flask import Flask, render_template
from jinja2 import ChoiceLoader, FileSystemLoader
from werkzeug.middleware.dispatcher import DispatcherMiddleware

BASE_DIR = Path(__file__).resolve().parent
SECTIONS = [
    {"label": "Chương 3", "prefix": "/chuong3", "file": "Chuong3/app.py", "description": "Routing, tham số URL và các phép tính cơ bản."},
    {"label": "Chương 3 · Sổ điểm", "prefix": "/chuong_03", "file": "chuong_03/tonghop/sodiem.py", "description": "Danh sách sinh viên, tìm kiếm, API và xuất điểm CSV."},
    {"label": "Chương 4", "prefix": "/chuong4", "file": "Chuong4/cafe.py", "description": "Quán cà phê: Jinja2, bộ lọc, thực đơn và phân trang."},
    {"label": "Chương 5", "prefix": "/chuong5", "file": "Chuong5/main.py", "description": "Form máy tính, điểm học phần và chỉ số BMI."},
    {"label": "Chương 6", "prefix": "/chuong6", "file": "Chuong6/c6.py", "description": "SQLAlchemy: danh sách sinh viên và thực hành truy vấn."},
    {"label": "Bài kiểm tra", "prefix": "/bai-kiem-tra", "file": "BaiKiemTra/app.py", "description": "Quản lý thư viện: danh mục, sách và thống kê."},
]


def add_shared_navbar(child_app, active):
    """Thêm navbar vào HTML; giữ nguyên API, CSV và các phản hồi khác."""
    child_app.jinja_loader = ChoiceLoader([
        child_app.jinja_loader,
        FileSystemLoader(str(BASE_DIR / "templates")),
    ])

    @child_app.after_request
    def insert_navbar(response):
        if (response.mimetype != "text/html" or response.is_streamed
                or response.direct_passthrough or 300 <= response.status_code < 400):
            return response
        html = response.get_data(as_text=True)
        navbar = render_template("shared_navbar.html", sections=SECTIONS, active_section=active)
        body = re.search(r"<body\b[^>]*>", html, flags=re.IGNORECASE)
        if body:
            html = html[:body.end()] + navbar + html[body.end():]
        else:
            html = ('<!doctype html><html lang="vi"><head><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width, initial-scale=1">'
                    '<title>Bài tập Flask</title></head><body>' + navbar
                    + '<main class="course-simple">' + html + '</main></body></html>')
        response.set_data(html)
        return response


def load_app(relative_file, active):
    path = BASE_DIR / relative_file
    name = "tonghop_" + "_".join(path.relative_to(BASE_DIR).with_suffix("").parts)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    child_app = module.app
    # Đường dẫn tuyệt đối để chạy được từ IDE hoặc từ thư mục khác.
    child_app.template_folder = str(path.parent / "templates")
    child_app.static_folder = str(path.parent / "static")
    # Session bài kiểm tra không bị lẫn với các ứng dụng còn lại.
    child_app.config["SESSION_COOKIE_NAME"] = name + "_session"
    child_app.config["SESSION_COOKIE_PATH"] = active + "/"
    add_shared_navbar(child_app, active)
    return child_app


app = Flask(__name__)


@app.get("/")
def index():
    return render_template("home.html", sections=SECTIONS, active_section="/")


@app.errorhandler(404)
def not_found(error):
    return render_template("not_found.html", sections=SECTIONS, active_section=""), 404


mounted_apps = {section["prefix"]: load_app(section["file"], section["prefix"]) for section in SECTIONS}
# Chương 3 có hai ứng dụng riêng, giữ cả bài thư viện trong bản tổng hợp.
mounted_apps["/chuong3/thu-vien"] = load_app("Chuong3/book.py", "/chuong3")

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, mounted_apps)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
