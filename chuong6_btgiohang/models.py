from datetime import datetime, timedelta, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint

db = SQLAlchemy()


def now():
    return datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)


STATUSES = {
    'pending': 'Chờ xác nhận', 'shipping': 'Đang giao',
    'completed': 'Hoàn tất', 'cancelled': 'Đã huỷ',
}
TRANSITIONS = {'pending': ('shipping', 'cancelled'),
               'shipping': ('completed', 'cancelled'), 'completed': (), 'cancelled': ()}


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    name_key = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    books = db.relationship('Book', back_populates='category')


class Book(db.Model):
    __table_args__ = (CheckConstraint('price >= 1000'), CheckConstraint('stock >= 0'))
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    title_key = db.Column(db.String(200), unique=True, nullable=False)
    author = db.Column(db.String(150), nullable=False)
    publisher = db.Column(db.String(150), default='')
    year = db.Column(db.Integer)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, default='')
    cover = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', back_populates='books')
    order_items = db.relationship('OrderItem', back_populates='book')


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(254), default='')
    address = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text, default='')
    payment = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=now)
    completed_at = db.Column(db.DateTime)
    shipping_fee = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    items = db.relationship('OrderItem', cascade='all, delete-orphan', back_populates='order')
    history = db.relationship('OrderHistory', cascade='all, delete-orphan', order_by='OrderHistory.id')


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    book_title = db.Column(db.String(200), nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship('Order', back_populates='items')
    book = db.relationship('Book', back_populates='order_items')


class OrderHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, default=now)
