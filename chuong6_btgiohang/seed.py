from models import Book, Category, Order, OrderHistory, OrderItem, db, now


def seed_data():
    if db.session.scalar(db.select(db.func.count(Category.id))):
        return
    names = ['Lập trình', 'Cơ sở dữ liệu', 'Công cụ', 'Mạng', 'Kỹ năng lập trình', 'Thiết kế']
    categories = [Category(name=name, name_key=name.casefold(), description=f'Sách về {name.lower()}.') for name in names]
    db.session.add_all(categories)
    db.session.flush()
    records = [
        ('Lập trình Python cơ bản', 'Nguyễn Văn A', 95000, 30, 0, 2024),
        ('Giáo trình Flask', 'Miguel Grinberg', 120000, 20, 0, 2024),
        ('Cơ sở dữ liệu', 'Trần Văn B', 85000, 0, 1, 2023),
        ('Pro Git', 'Scott Chacon', 150000, 15, 2, 2024),
        ('Mạng máy tính', 'Lê Văn C', 110000, 12, 3, 2023),
        ('Clean Code', 'Robert C. Martin', 180000, 5, 4, 2008),
    ]
    books = []
    for title, author, price, stock, category, year in records:
        book = Book(title=title, title_key=title.casefold(), author=author, price=price, stock=stock,
                    category=categories[category], publisher='NXB Đại học Huế', year=year,
                    description=f'{title} giúp bạn củng cố kiến thức nền tảng, thực hành qua ví dụ và áp dụng vào dự án thực tế.')
        books.append(book)
    db.session.add_all(books)
    db.session.flush()
    # The sample order reserves stock, just like a real checkout.
    order = Order(customer_name='Nguyễn Văn An', phone='0912345678', email='an@example.com',
                  address='12 Lê Lợi, phường Thuận Hoá, Huế', note='Giao giờ hành chính',
                  payment='cod', status='pending', shipping_fee=0, total=460000)
    for index, quantity in [(0, 2), (1, 1), (3, 1)]:
        book = books[index]
        book.stock -= quantity
        order.items.append(OrderItem(book=book, book_title=book.title, unit_price=book.price, quantity=quantity))
    order.history.append(OrderHistory(status='pending'))
    db.session.add(order)
    db.session.commit()
