import os
import secrets
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

import click
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFError, CSRFProtect
from PIL import Image, UnidentifiedImageError
from sqlalchemy import event, func, or_, update
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage

from forms import BookForm, CategoryForm, CheckoutForm
from models import Book, Category, Order, OrderHistory, OrderItem, STATUSES, TRANSITIONS, db, now


@event.listens_for(Engine, 'connect')
def sqlite_constraints(connection, record):
    if type(connection).__module__.startswith('sqlite3'):
        connection.execute('PRAGMA foreign_keys=ON')


def create_app(config=None):
    app = Flask(__name__)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    # Persist a local development key so sessions survive a restart.
    key_file = Path(app.instance_path) / 'secret.key'
    if not key_file.exists():
        try:
            with key_file.open('x', encoding='utf-8') as stream:
                stream.write(secrets.token_hex(32))
        except FileExistsError:
            pass
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or key_file.read_text(),
                      SQLALCHEMY_DATABASE_URI='sqlite:///bookshop.db',
                      SQLALCHEMY_TRACK_MODIFICATIONS=False,
                      MAX_CONTENT_LENGTH=3 * 1024 * 1024,
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                      UPLOAD_FOLDER=str(Path(app.static_folder) / 'uploads'))
    if config:
        app.config.update(config)
    db.init_app(app)
    Migrate(app, db, render_as_batch=True)
    CSRFProtect(app)
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    app.jinja_env.filters['money'] = lambda value: f'{value:,.0f}'.replace(',', '.') + ' đ'

    def cart_data():
        raw = session.get('cart', {})
        cart = {}
        if isinstance(raw, dict):
            for key, quantity in raw.items():
                if isinstance(key, str) and key.isascii() and key.isdigit() and type(quantity) is int and quantity > 0:
                    cart[key] = quantity
        return cart

    def cart_lines():
        cart = cart_data()
        books = db.session.scalars(db.select(Book).where(Book.id.in_([int(k) for k in cart]))).all() if cart else []
        lines = [{'book': b, 'quantity': cart[str(b.id)], 'subtotal': b.price * cart[str(b.id)]} for b in books]
        valid = {str(line['book'].id): line['quantity'] for line in lines}
        if valid != session.get('cart', {}):
            session['cart'] = valid
            flash('Một số sách không còn tồn tại đã được bỏ khỏi giỏ.', 'warning')
        return lines, sum(line['subtotal'] for line in lines)

    def back_to_shop():
        target = request.form.get('next', '')
        parsed = urlsplit(target)
        if not parsed.netloc and not parsed.scheme and parsed.path.startswith('/books') and not target.startswith('//') and '\\' not in target:
            return redirect(target)
        return redirect(url_for('books'))

    def filtered_books():
        stmt = db.select(Book)
        keyword = request.args.get('q', '').strip()
        # casefold handles Vietnamese Unicode consistently with duplicate checks.
        if keyword:
            ids = [b.id for b in db.session.scalars(db.select(Book))
                   if keyword.casefold() in b.title.casefold() or keyword.casefold() in b.author.casefold()]
            stmt = stmt.where(Book.id.in_(ids))
        category = request.args.get('category', type=int)
        if category:
            stmt = stmt.where(Book.category_id == category)
        stock = request.args.get('stock')
        if stock == 'available':
            stmt = stmt.where(Book.stock > 0)
        elif stock == 'low':
            stmt = stmt.where(Book.stock <= 5)
        elif stock == 'empty':
            stmt = stmt.where(Book.stock == 0)
        return stmt.order_by(Book.id.desc())

    @app.context_processor
    def common_context():
        pending = db.session.scalar(db.select(func.count(Order.id)).where(Order.status == 'pending'))
        return dict(cart_count=sum(cart_data().values()), statuses=STATUSES,
                    pending_count=pending, payments={'cod': 'Tiền mặt khi nhận hàng', 'bank': 'Chuyển khoản'},
                    page_url=lambda page: url_for(request.endpoint, **dict(request.args, page=page)))

    @app.get('/')
    def home():
        return redirect(url_for('books'))

    @app.get('/books')
    def books():
        return render_template('books.html', books=db.session.scalars(filtered_books()).all(),
                               categories=db.session.scalars(db.select(Category).order_by(Category.name)).all())

    @app.get('/books/<int:book_id>')
    def book_detail(book_id):
        book = db.get_or_404(Book, book_id)
        in_cart = cart_data().get(str(book_id), 0)
        return render_template('book_detail.html', book=book, in_cart=in_cart, available=max(0, book.stock - in_cart))

    @app.post('/cart/add/<int:book_id>')
    def cart_add(book_id):
        book = db.get_or_404(Book, book_id)
        cart = cart_data()
        try:
            quantity = int(request.form.get('quantity', '1'))
            if not 1 <= quantity <= book.stock - cart.get(str(book_id), 0):
                raise ValueError
        except (ValueError, TypeError):
            flash(f'Số lượng không hợp lệ hoặc vượt tồn kho của «{book.title}».', 'danger')
        else:
            cart[str(book_id)] = cart.get(str(book_id), 0) + quantity
            session['cart'] = cart
            flash(f'Đã thêm {quantity} × {book.title} vào giỏ hàng.', 'success')
        return back_to_shop()

    @app.get('/cart')
    def cart():
        lines, subtotal = cart_lines()
        return render_template('cart.html', lines=lines, subtotal=subtotal)

    @app.post('/cart/<int:book_id>/<action>')
    def cart_change(book_id, action):
        cart = cart_data()
        key = str(book_id)
        if action not in ('increase', 'decrease', 'remove'):
            abort(404)
        if key in cart:
            book = db.session.get(Book, book_id)
            if action == 'remove' or book is None:
                cart.pop(key)
            elif action == 'increase':
                if cart[key] < book.stock:
                    cart[key] += 1
                else:
                    flash(f'«{book.title}» không đủ tồn kho để tăng số lượng.', 'warning')
            else:
                cart[key] -= 1
                if cart[key] <= 0:
                    cart.pop(key)
            session['cart'] = cart
        return redirect(url_for('cart'))

    @app.post('/cart/clear')
    def cart_clear():
        session.pop('cart', None)
        flash('Đã xoá giỏ hàng.', 'success')
        return redirect(url_for('cart'))

    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        lines, subtotal = cart_lines()
        if not lines:
            flash('Giỏ hàng trống. Hãy chọn sách trước khi đặt hàng.', 'warning')
            return redirect(url_for('cart'))
        form = CheckoutForm()
        fee = 0 if subtotal >= 200000 else 20000
        if form.validate_on_submit():
            try:
                order = Order(customer_name=form.customer_name.data, phone=form.phone.data,
                              email=form.email.data or '', address=form.address.data,
                              note=form.note.data or '', payment=form.payment.data,
                              shipping_fee=fee, total=subtotal + fee)
                db.session.add(order)
                for line in lines:
                    book, quantity = line['book'], line['quantity']
                    # Conditional UPDATE prevents overselling between concurrent checkouts.
                    result = db.session.execute(update(Book).where(Book.id == book.id, Book.stock >= quantity)
                                                .values(stock=Book.stock - quantity), execution_options={'synchronize_session': False})
                    if result.rowcount != 1:
                        raise ValueError(f'«{book.title}» không đủ {quantity} cuốn. Vui lòng cập nhật giỏ hàng.')
                    order.items.append(OrderItem(book_id=book.id, book_title=book.title,
                                                 unit_price=book.price, quantity=quantity))
                order.history.append(OrderHistory(status='pending'))
                db.session.commit()
            except ValueError as error:
                db.session.rollback()
                flash(str(error), 'danger')
                return redirect(url_for('cart'))
            session.pop('cart', None)
            allowed = session.get('order_ids', [])
            session['order_ids'] = (allowed + [order.id])[-30:]
            flash('Đặt hàng thành công! Cảm ơn bạn đã chọn Nhà sách Sông Hương.', 'success')
            return redirect(url_for('order_detail', order_id=order.id))
        return render_template('checkout.html', form=form, lines=lines, subtotal=subtotal, fee=fee)

    @app.get('/orders/<int:order_id>')
    def order_detail(order_id):
        if order_id not in session.get('order_ids', []):
            abort(404)
        return render_template('order_detail.html', order=db.get_or_404(Order, order_id), admin=False)

    @app.get('/admin')
    def dashboard():
        today = now()
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(year=start.year + 1, month=1) if start.month == 12 else start.replace(month=start.month + 1)
        stats = [db.session.scalar(db.select(func.count(Book.id))),
                 db.session.scalar(db.select(func.count(Order.id)).where(Order.status == 'pending')),
                 db.session.scalar(db.select(func.coalesce(func.sum(Order.total), 0)).where(Order.status == 'completed', Order.completed_at >= start, Order.completed_at < end)),
                 db.session.scalar(db.select(func.count(Book.id)).where(Book.stock <= 5))]
        # Seven calendar days including today, on the same UTC+7 clock as orders.
        day_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = day_start - timedelta(days=6)
        daily_rows = db.session.execute(
            db.select(func.date(Order.completed_at), func.sum(Order.total), func.count(Order.id))
            .where(Order.status == 'completed', Order.completed_at >= week_start,
                   Order.completed_at < day_start + timedelta(days=1))
            .group_by(func.date(Order.completed_at))
        ).all()
        by_date = {str(date): (amount, count) for date, amount, count in daily_rows}
        revenue_days = []
        for offset in range(7):
            date = week_start + timedelta(days=offset)
            amount, count = by_date.get(date.strftime('%Y-%m-%d'), (0, 0))
            revenue_days.append(dict(date=date, amount=amount, count=count))
        revenue_total = sum(day['amount'] for day in revenue_days)
        revenue_count = sum(day['count'] for day in revenue_days)
        revenue_peak = max(day['amount'] for day in revenue_days)
        chart_ceiling = max(100000, ((revenue_peak + 99999) // 100000) * 100000)
        return render_template('admin/dashboard.html', stats=stats, month=today.month,
                               revenue_days=revenue_days, revenue_total=revenue_total,
                               revenue_count=revenue_count, revenue_peak=revenue_peak,
                               chart_ceiling=chart_ceiling, today=today,
                               orders=db.session.scalars(db.select(Order).order_by(Order.id.desc()).limit(5)).all(),
                               low_books=db.session.scalars(db.select(Book).where(Book.stock <= 5).order_by(Book.stock)).all())

    @app.get('/admin/books')
    def admin_books():
        pagination = db.paginate(filtered_books(), per_page=5, error_out=False)
        used = set(db.session.scalars(db.select(OrderItem.book_id).distinct()).all())
        return render_template('admin/books.html', pagination=pagination, used=used,
                               categories=db.session.scalars(db.select(Category).order_by(Category.name)).all())

    def delete_cover(filename):
        if filename and Path(filename).name == filename:
            (Path(app.config['UPLOAD_FOLDER']) / filename).unlink(missing_ok=True)

    @app.route('/admin/books/new', methods=['GET', 'POST'])
    @app.route('/admin/books/<int:book_id>/edit', methods=['GET', 'POST'])
    def book_edit(book_id=None):
        book = db.get_or_404(Book, book_id) if book_id is not None else None
        form = BookForm(obj=book)
        form.editing_id = book_id
        form.category_id.choices = [(c.id, c.name) for c in db.session.scalars(db.select(Category).order_by(Category.name))]
        if form.validate_on_submit():
            new_cover = None
            if isinstance(form.cover.data, FileStorage) and form.cover.data.filename:
                try:
                    data = form.cover.data.read()
                    with Image.open(BytesIO(data)) as image:
                        if image.format not in ('JPEG', 'PNG', 'WEBP'):
                            raise ValueError
                        image.verify()
                    # Re-encode uploaded data; filenames and contents are both checked.
                    with Image.open(BytesIO(data)) as image:
                        image.thumbnail((1200, 1600))
                        new_cover = uuid4().hex + '.webp'
                        image.convert('RGB').save(Path(app.config['UPLOAD_FOLDER']) / new_cover, 'WEBP')
                except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
                    form.cover.errors.append('Tệp không phải ảnh JPG, PNG hoặc WEBP hợp lệ.')
                    return render_template('admin/book_form.html', form=form, book=book)
            old_cover = book.cover if book else None
            if book is None:
                book = Book()
                db.session.add(book)
            for name in ('title', 'author', 'publisher', 'year', 'price', 'stock', 'category_id', 'description'):
                setattr(book, name, getattr(form, name).data)
            book.title_key = book.title.casefold()
            if new_cover:
                book.cover = new_cover
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                delete_cover(new_cover)
                form.title.errors.append('Tên sách đã tồn tại hoặc danh mục không còn tồn tại.')
            else:
                if new_cover:
                    delete_cover(old_cover)
                flash('Đã lưu sách.', 'success')
                return redirect(url_for('admin_books'))
        return render_template('admin/book_form.html', form=form, book=book)

    @app.post('/admin/books/<int:book_id>/delete')
    def book_delete(book_id):
        book = db.get_or_404(Book, book_id)
        if db.session.scalar(db.select(func.count(OrderItem.id)).where(OrderItem.book_id == book_id)):
            flash('Không thể xoá sách đã có trong đơn hàng.', 'danger')
        else:
            cover = book.cover
            db.session.delete(book)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash('Không thể xoá sách đã có trong đơn hàng.', 'danger')
            else:
                delete_cover(cover)
                flash('Đã xoá sách.', 'success')
        return redirect(url_for('admin_books'))

    @app.route('/admin/categories', methods=['GET', 'POST'])
    @app.route('/admin/categories/<int:category_id>/edit', methods=['GET', 'POST'])
    def categories(category_id=None):
        category = db.get_or_404(Category, category_id) if category_id is not None else None
        form = CategoryForm(obj=category)
        form.editing_id = category_id
        if form.validate_on_submit():
            if category is None:
                category = Category()
                db.session.add(category)
            category.name, category.description = form.name.data, form.description.data
            category.name_key = category.name.casefold()
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.name.errors.append('Danh mục đã tồn tại.')
            else:
                flash('Đã lưu danh mục.', 'success')
                return redirect(url_for('categories'))
        rows = db.session.execute(db.select(Category, func.count(Book.id)).outerjoin(Book).group_by(Category.id).order_by(Category.name)).all()
        return render_template('admin/categories.html', rows=rows, form=form, category=category)

    @app.post('/admin/categories/<int:category_id>/delete')
    def category_delete(category_id):
        category = db.get_or_404(Category, category_id)
        count = db.session.scalar(db.select(func.count(Book.id)).where(Book.category_id == category_id))
        if count:
            flash(f'Không thể xoá «{category.name}»: còn {count} sách.', 'danger')
        else:
            db.session.delete(category)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash('Không thể xoá: danh mục vừa được gán cho sách.', 'danger')
            else:
                flash('Đã xoá danh mục.', 'success')
        return redirect(url_for('categories'))

    @app.get('/admin/orders')
    def admin_orders():
        stmt = db.select(Order)
        status = request.args.get('status', '')
        keyword = request.args.get('q', '').strip()
        if status in STATUSES:
            stmt = stmt.where(Order.status == status)
        if keyword:
            ids = [o.id for o in db.session.scalars(db.select(Order))
                   if keyword.casefold() in o.customer_name.casefold() or keyword in o.phone or keyword.lstrip('#') == str(o.id)]
            stmt = stmt.where(Order.id.in_(ids))
        filtered = stmt.subquery()
        count, total = db.session.execute(db.select(func.count(), func.coalesce(func.sum(filtered.c.total), 0)).select_from(filtered)).one()
        counts = dict(db.session.execute(db.select(Order.status, func.count(Order.id)).group_by(Order.status)).all())
        return render_template('admin/orders.html', pagination=db.paginate(stmt.order_by(Order.id.desc()), per_page=10, error_out=False),
                               counts=counts, count=count, total=total)

    @app.route('/admin/orders/<int:order_id>', methods=['GET', 'POST'])
    def admin_order_detail(order_id):
        order = db.get_or_404(Order, order_id)
        if request.method == 'POST':
            target = request.form.get('status')
            if target not in TRANSITIONS[order.status]:
                flash('Chuyển trạng thái không hợp lệ.', 'danger')
            else:
                old_status = order.status
                result = db.session.execute(update(Order).where(Order.id == order_id, Order.status == old_status)
                                            .values(status=target, completed_at=now() if target == 'completed' else None),
                                            execution_options={'synchronize_session': False})
                if result.rowcount != 1:
                    db.session.rollback()
                    flash('Đơn hàng vừa thay đổi. Vui lòng kiểm tra lại.', 'warning')
                else:
                    if target == 'cancelled':
                        for item in order.items:
                            db.session.execute(update(Book).where(Book.id == item.book_id).values(stock=Book.stock + item.quantity))
                    db.session.add(OrderHistory(order_id=order.id, status=target))
                    db.session.commit()
                    flash('Đã cập nhật trạng thái đơn hàng.', 'success')
            return redirect(url_for('admin_order_detail', order_id=order_id))
        return render_template('order_detail.html', order=order, admin=True, transitions=TRANSITIONS[order.status])

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', message='Không tìm thấy trang hoặc dữ liệu bạn yêu cầu.'), 404

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template('error.html', message='Phiên biểu mẫu hết hạn hoặc thiếu CSRF token. Hãy tải lại trang rồi thử lại.'), 400

    @app.errorhandler(413)
    def upload_too_large(error):
        return render_template('error.html', message='Tệp tải lên quá lớn. Ảnh bìa tối đa 2 MB.'), 413

    @app.cli.command('seed')
    def seed_command():
        from seed import seed_data
        seed_data()
        click.echo('Đã chuẩn bị dữ liệu mẫu (không thêm trùng).')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
