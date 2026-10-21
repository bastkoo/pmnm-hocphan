from math import ceil
import datetime

from flask import Flask, abort, render_template, request

# 1. Khởi tạo ứng dụng Flask
app = Flask(__name__)

SHOP = {
    "name": "Cà phê Sông Hương",
    "address": "123 Đường ABC, TP. Huế",
    "open": 7, 
    "close": 22
}

PROMOTIONS = [
    "Giảm giá cho sinh viên", 
    "Mua 1 tặng 1 vào thứ 3", 
    "Miễn phí giao hàng cho đơn hàng trên 200k"
]

MENU = [
    {"name": "cà phê sữa", "price": 25000, "available": True},
    {"name": "cà phê đen", "price": 20000, "available": True},
    {"name": "trà sữa", "price": 30000, "available": False},
    {"name": "bánh ngọt", "price": 15000, "available": True},
    {"name": "sinh tố", "price": 35000, "available": True}
]

# 2. Khai báo các Custom Filters
@app.template_filter('vnd')
def format_vnd(value):
    try:
        # Định dạng tiền VND: 25.000 đ
        return f"{int(value):,}".replace(",", ".") + " đ"
    except (ValueError, TypeError):
        return value

@app.template_filter('average_price')
def average_price_filter(list_items):
    if not list_items:
        return 0
    total = sum(item.get('price', 0) for item in list_items)
    return total / len(list_items)

@app.template_filter('dang_co')
def dang_co_filter(list_items):
    # Đếm số món có sẵn (available = True) từ danh sách được truyền vào
    available_items = [item for item in list_items if item.get('available', False)]
    return len(available_items)

# 3. Khai báo các Routes
@app.route("/")
def index():
    hour = request.args.get("gio", type=int)
    if hour is None:
        hour = datetime.datetime.now().hour  # Đã sửa lỗi gọi .now().now()
    
    is_open = SHOP['open'] <= hour < SHOP['close']
    return render_template("index1.html", hour=hour, is_open=is_open, shop=SHOP, promotions=PROMOTIONS)  

@app.route("/menu")
def menu_route():
    # Phân trang: mỗi trang 3 món
    page = request.args.get("page", 1, type=int)
    per_page = 3  
    
    total_items = len(MENU)
    total_pages = ceil(total_items / per_page) if total_items > 0 else 1
    
    # Nếu người dùng nhập số trang không hợp lệ -> Báo lỗi 404
    if page < 1 or (page > total_pages and total_items > 0):
        abort(404)
        
    # Cắt danh sách món cho trang hiện tại
    start = (page - 1) * per_page
    end = start + per_page
    items_on_page = MENU[start:end]
    
    return render_template(
        "menu2.html", 
        menu=MENU,  # Dùng cho các filter tính toán toàn bộ menu (giá trung bình, số món đang có)
        items_on_page=items_on_page,  # Dùng để hiển thị danh sách món theo trang
        current_page=page, 
        total_pages=total_pages
    )

@app.route("/contact")
def contact():
    return render_template("contact.html", shop=SHOP)

# Xử lý trang lỗi 404 toàn cục
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# 4. Chạy ứng dụng khi thực thi file
if __name__ == "__main__":
    app.run(debug=True)