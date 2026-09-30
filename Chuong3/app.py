from flask import Flask, request

# 1. Khởi tạo ứng dụng Flask
app = Flask(__name__)
POSTS = [
    {
        "id": 1,
        "title": "Chào Flask",
        "author": "an",
        "content": "Flask là 1 micro-framework...",
        "created": "2026-09-01",
    },
    {
        "id": 2,
        "title": "Tìm hiểu về Routing trong Flask",
        "author": "binh",
        "content": "Routing giúp định tuyến các URL đến hàm xử lý tương ứng trong ứng dụng Web.",
        "created": "2026-09-05",
    },
    {
        "id": 3,
        "title": "Làm việc với Jinja2 Template",
        "author": "chi",
        "content": "Jinja2 cho phép bạn renders các file HTML động dễ dàng kết hợp với dữ liệu Python.",
        "created": "2026-09-12",
    },
    {
        "id": 4,
        "title": "Xử lý Form và Phương thức POST",
        "author": "an",
        "content": "Hướng dẫn cách nhận dữ liệu người dùng nhập vào từ Form trong Flask.",
        "created": "2026-09-20",
    },
    {
        "id": 5,
        "title": "Kết nối Cơ sở dữ liệu SQLite",
        "author": "dung",
        "content": "Sử dụng SQLAlchemy để quản lý và lưu trữ dữ liệu bền vững cho ứng dụng.",
        "created": "2026-09-28",
    }
]
def find_post(post_id):
    """Trar veef bai viet cos id tuong ung hoac bang none neu ko co"""
    for post in POSTS:
        if post.id == post_id:
            return post
# 2. Khai báo các Route
@app.route("/")
def index():
    return "Trang chủ"
@app.route("/index")
def index1():
    return f"<a href = '/'>Trang chủ</a>" \
    "<a href = '/about'> Giới thiệu </a> "
@app.route("/about")
def about():
    return "Giới thiệu"
@app.route("/user/<username>")
def user_profile(username):
    return f"Xin chào {username}!"

@app.route("/square/<x>")
def square(x):
    return f"{float(x) * float(x)}"

@app.route("/square2/<float:x>")
def square2(x):
    return f"{x**2}"

@app.route("/sum/<strs>")
def tong(strs):
    #1,2,3 = 6
    arr = strs.split(',')
    list_so = [float(num) for num in arr]
    return f"{sum(list_so)}"

@app.route("/tinhtoan")
def tinh_toan():
    a = request.args.get("a")
    b = request.args.get("b")
    op = request.args.get("op")
    if op == "add":
        return f"{a} + {b} = {int(a)+int(b)}"
    elif op == "sub":
        return f"{a} - {b} = {int(a)-int(b)}"
    else:
        return f"Truyền đủ tham số!"
    
# 3. Chạy ứng dụng khi thực thi file
if __name__ == "__main__":
    app.run(debug=True)