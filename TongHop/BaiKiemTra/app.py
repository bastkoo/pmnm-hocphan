from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config.update(SECRET_KEY='dev-change-this-secret', SQLALCHEMY_DATABASE_URI='sqlite:///library.db', SQLALCHEMY_TRACK_MODIFICATIONS=False)
db = SQLAlchemy(app)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    books = db.relationship('Book', back_populates='category')

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=True)
    price = db.Column(db.Float, nullable=False, default=0)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.Text, default='')
    description = db.Column(db.Text, default='')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.relationship('Category', back_populates='books')

@app.template_filter('money')
def money(value):
    return f'{value:,.0f}'.replace(',', '.') + ' ₫'

@app.route('/')
def dashboard():
    return render_template('dashboard.html', active='dashboard', categories=Category.query.count(), books=Book.query.count(), stock=db.session.query(func.coalesce(func.sum(Book.quantity), 0)).scalar(), value=db.session.query(func.coalesce(func.sum(Book.price * Book.quantity), 0)).scalar(), latest=Book.query.order_by(Book.created_at.desc()).limit(6).all(), by_category=db.session.query(Category.name, func.count(Book.id)).outerjoin(Book).group_by(Category.id).order_by(Category.name).all())

@app.route('/categories')
def categories():
    q=request.args.get('q','').strip()
    query=Category.query
    if q: query=query.filter(Category.name.ilike(f'%{q}%'))
    return render_template('categories.html', active='categories', items=query.order_by(Category.id.desc()).all(), q=q)

@app.route('/categories/save', methods=['POST'])
def save_category():
    ident=request.form.get('id',type=int)
    name=request.form.get('name','').strip()
    if not name:
        flash('Tên danh mục không được để trống.', 'error'); return redirect(url_for('categories'))
    duplicate=Category.query.filter(func.lower(Category.name)==name.lower())
    if ident: duplicate=duplicate.filter(Category.id!=ident)
    if duplicate.first():
        flash('Tên danh mục đã tồn tại.', 'error'); return redirect(url_for('categories'))
    item=db.session.get(Category,ident) if ident else Category()
    if item is None:
        flash('Không tìm thấy danh mục.', 'error'); return redirect(url_for('categories'))
    item.name=name; item.description=request.form.get('description','').strip()
    db.session.add(item); db.session.commit(); flash('Đã lưu danh mục thành công.', 'success')
    return redirect(url_for('categories'))

@app.route('/categories/<int:ident>/delete', methods=['POST'])
def delete_category(ident):
    item=db.get_or_404(Category,ident)
    if item.books: flash('Không thể xóa danh mục đang có sách.', 'error')
    else:
        db.session.delete(item); db.session.commit(); flash('Đã xóa danh mục.', 'success')
    return redirect(url_for('categories'))

@app.route('/books')
def books():
    q=request.args.get('q','').strip(); category=request.args.get('category',type=int)
    query=Book.query
    if q: query=query.filter(db.or_(Book.title.ilike(f'%{q}%'),Book.author.ilike(f'%{q}%'),Book.isbn.ilike(f'%{q}%')))
    if category: query=query.filter_by(category_id=category)
    return render_template('books.html',active='books',items=query.order_by(Book.id.desc()).all(),categories=Category.query.order_by(Category.name).all(),q=q,selected_category=category)

@app.route('/books/save',methods=['POST'])
def save_book():
    ident=request.form.get('id',type=int)
    item=db.session.get(Book,ident) if ident else Book()
    if item is None: flash('Không tìm thấy sách.', 'error'); return redirect(url_for('books'))
    title=request.form.get('title','').strip(); author=request.form.get('author','').strip()
    category_id=request.form.get('category_id',type=int)
    isbn=request.form.get('isbn','').strip() or None
    try: price=float(request.form.get('price','0')); quantity=int(request.form.get('quantity','0'))
    except ValueError: flash('Giá hoặc số lượng không hợp lệ.', 'error'); return redirect(url_for('books'))
    if not title or not author or not db.session.get(Category,category_id) or price<0 or quantity<0:
        flash('Vui lòng nhập đủ thông tin hợp lệ.', 'error'); return redirect(url_for('books'))
    if isbn:
        duplicate=Book.query.filter_by(isbn=isbn)
        if ident: duplicate=duplicate.filter(Book.id!=ident)
        if duplicate.first(): flash('ISBN đã tồn tại.', 'error'); return redirect(url_for('books'))
    item.title=title; item.author=author; item.category_id=category_id; item.isbn=isbn
    item.price=price; item.quantity=quantity; item.image_url=request.form.get('image_url','').strip(); item.description=request.form.get('description','').strip()
    db.session.add(item); db.session.commit(); flash('Đã lưu sách thành công.', 'success')
    return redirect(url_for('books'))

@app.route('/books/<int:ident>/delete',methods=['POST'])
def delete_book(ident):
    db.session.delete(db.get_or_404(Book,ident)); db.session.commit(); flash('Đã xóa sách.', 'success')
    return redirect(url_for('books'))

@app.route('/books/<int:ident>')
def book_detail(ident):
    return render_template('detail.html',active='books',book=db.get_or_404(Book,ident))

with app.app_context(): db.create_all()

if __name__=='__main__': app.run(debug=True, port=5001)
