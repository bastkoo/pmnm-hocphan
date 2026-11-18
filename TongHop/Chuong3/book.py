from flask import Flask, request, jsonify, url_for, abort
from markupsafe import escape

app = Flask(__name__)

BOOKS = [
    {
        "id": 1,
        "title": "Đắc Nhân Tâm",
        "author": "Dale Carnegie",
        "year": 1936,
        "category": "Kỹ năng sống",
        "available": True,
    },
    {
        "id": 2,
        "title": "Nhà Giả Kim",
        "author": "Paulo Coelho",
        "year": 1988,
        "category": "Tiểu thuyết",
        "available": False,
    },
    {
        "id": 3,
        "title": "Lập Trình Python Căn Bản",
        "author": "Nguyễn Văn An",
        "year": 2023,
        "category": "Lập trình",  # Đã đổi thể loại thành "Lập trình"
        "available": True,
    },
    {
        "id": 4,
        "title": "Tuổi Trẻ Đáng Giá Bao Nhiêu",
        "author": "Rosie Nguyễn",
        "year": 2018,
        "category": "Kỹ năng sống",
        "available": True,
    },
    {
        "id": 5,
        "title": "Xây Dựng Web Với Flask",
        "author": "Trần Bình",
        "year": 2024,
        "category": "Lập trình",  # Đã đổi thêm 1 cuốn cho phong phú
        "available": False,
    }
]

# Menu chung cho các trang HTML
def get_menu():
    return f'''
    <nav>
        <a href="{url_for('index')}">Trang chủ</a> | 
        <a href="{url_for('listBook')}">Tất cả sách</a> | 
        <a href="{url_for('listBook', category='Lập trình')}">Sách Lập trình</a>
    </nav>
    <hr>
    '''

# 1. Route Trang chủ "/"
@app.route("/")
def index():
    tong_so_sach = len(BOOKS)
    so_sach_san_sang = sum(1 for b in BOOKS if b['available'])
    
    html = f'''
    {get_menu()}
    <h1>Trang Chủ Thư Viện</h1>
    <p>Tổng số đầu sách: <strong>{tong_so_sach}</strong></p>
    <p>Số sách sẵn sàng cho mượn: <strong>{so_sach_san_sang}</strong></p>
    '''
    return html

# 2. Route Danh sách sách "/books" (Lọc theo category)
@app.route("/books")
def listBook():
    selected_category = request.args.get('category', '').strip()
    
    # Lấy danh sách thể loại không trùng lặp để tạo thanh lọc
    categories = sorted(list(set(b['category'] for b in BOOKS)))
    
    # Tạo thanh liên kết theo thể loại
    cat_links = [f'<a href="{url_for("listBook")}">Tất cả</a>']
    for cat in categories:
        cat_links.append(f'<a href="{url_for("listBook", category=cat)}">{escape(cat)}</a>')
    filter_bar = " | ".join(cat_links)
    
    # Lọc sách nếu có tham số category
    filtered_books = BOOKS
    if selected_category:
        filtered_books = [b for b in BOOKS if b['category'].lower() == selected_category.lower()]
    
    # Dựng bảng hiển thị sách
    table_rows = ""
    for b in filtered_books:
        detail_url = url_for('bookDetail', book_id=b['id'])
        status = "Sẵn sàng" if b['available'] else "Đã mượn"
        table_rows += f'''
        <tr>
            <td>{b['id']}</td>
            <td><a href="{detail_url}">{escape(b['title'])}</a></td>
            <td>{escape(b['author'])}</td>
            <td>{b['year']}</td>
            <td>{escape(b['category'])}</td>
            <td>{status}</td>
        </tr>
        '''
        
    html = f'''
    {get_menu()}
    <h1>Danh Sách Sách</h1>
    <p><strong>Lọc theo thể loại:</strong> {filter_bar}</p>
    <table border="1" cellpadding="8" cellspacing="0">
        <thead>
            <tr>
                <th>ID</th>
                <th>Tên sách</th>
                <th>Tác giả</th>
                <th>Năm xuất bản</th>
                <th>Thể loại</th>
                <th>Trạng thái</th>
            </tr>
        </thead>
        <tbody>
            {table_rows if table_rows else '<tr><td colspan="6">Không tìm thấy sách phù hợp</td></tr>'}
        </tbody>
    </table>
    '''
    return html

# 3. Route Chi tiết sách "/books/<int:book_id>"
@app.route("/books/<int:book_id>")
def bookDetail(book_id):
    book = next((b for b in BOOKS if b['id'] == book_id), None)
    if not book:
        return f'''
        {get_menu()}
        <h2>Lỗi 404</h2>
        <p>Không có sách với ID = {book_id}</p>
        ''', 404
        
    status = "Sẵn sàng" if book['available'] else "Đã mượn"
    html = f'''
    {get_menu()}
    <h1>Chi Tiết Sách</h1>
    <ul>
        <li><strong>ID:</strong> {book['id']}</li>
        <li><strong>Tên sách:</strong> {escape(book['title'])}</li>
        <li><strong>Tác giả:</strong> {escape(book['author'])}</li>
        <li><strong>Năm xuất bản:</strong> {book['year']}</li>
        <li><strong>Thể loại:</strong> {escape(book['category'])}</li>
        <li><strong>Trạng thái:</strong> {status}</li>
    </ul>
    '''
    return html

# 4. API Danh sách sách "/api/books"
@app.route("/api/books")
def api_books():
    return jsonify(BOOKS)

# 5. API Chi tiết sách "/api/books/<int:book_id>"
@app.route("/api/books/<int:book_id>")
def api_book_detail(book_id):
    book = next((b for b in BOOKS if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": f"Không có sách với ID = {book_id}"}), 404
    return jsonify(book)

# 6. Trang 404 tùy biến chung
@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Trang hoặc tài nguyên không tồn tại"}), 404
    
    return f'''
    {get_menu()}
    <h1>404 - Trang không tồn tại</h1>
    <p>Đường dẫn bạn truy cập không hợp lệ.</p>
    ''', 404

if __name__ == "__main__":
    app.run(debug=True)