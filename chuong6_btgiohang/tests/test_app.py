import io
import re
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from flask import template_rendered

from PIL import Image

from app import create_app
from models import Book, Category, Order, OrderHistory, db
from seed import seed_data


class ShopTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({'TESTING': True, 'SECRET_KEY': 'test-key',
                               'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + str(Path(self.tmp.name) / 'test.db'),
                               'UPLOAD_FOLDER': str(Path(self.tmp.name) / 'uploads')})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        seed_data()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()
        self.tmp.cleanup()

    def token(self, path='/books'):
        response = self.client.get(path)
        match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', response.get_data(as_text=True))
        self.assertIsNotNone(match, path)
        return match.group(1)

    def post(self, path, data=None, token_path='/books', **kwargs):
        data = dict(data or {})
        data['csrf_token'] = self.token(token_path)
        return self.client.post(path, data=data, **kwargs)

    def add(self, book_id=1, quantity=1):
        return self.post(f'/cart/add/{book_id}', {'quantity': quantity})

    def checkout(self, **overrides):
        data = {'customer_name': 'Nguyễn Văn Test', 'phone': '0912345678',
                'email': 'test@example.com', 'address': '12 Lê Lợi, Huế', 'payment': 'cod'}
        data.update(overrides)
        return self.post('/checkout', data, token_path='/checkout')

    def test_pages_and_filters(self):
        for path in ['/books', '/books/1', '/cart', '/admin', '/admin/books',
                     '/admin/books?page=2', '/admin/books/new', '/admin/books/1/edit',
                     '/admin/categories', '/admin/categories/1/edit', '/admin/orders', '/admin/orders/1']:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)
        self.assertEqual(self.client.get('/books/999').status_code, 404)
        text = self.client.get('/books?q=PYTHON&category=1').get_data(as_text=True)
        self.assertIn('Lập trình Python cơ bản', text)
        self.assertNotIn('Clean Code', text)
        self.assertIn('page=2', self.client.get('/admin/books').get_data(as_text=True))

    def test_csrf_and_post_only(self):
        self.assertEqual(self.client.post('/cart/add/1').status_code, 400)
        self.assertEqual(self.client.get('/cart/clear').status_code, 405)
        self.assertEqual(self.client.post('/admin/orders/1', data={'status': 'cancelled'}).status_code, 400)

    def test_cart_accumulation_bounds_and_price(self):
        self.add(quantity=2)
        self.add(quantity=1)
        for bad in ['0', '-1', 'abc', '2.5', '999']:
            self.add(quantity=bad)
        with self.client.session_transaction() as session:
            self.assertEqual(session['cart'], {'1': 3})
        book = db.session.get(Book, 1)
        book.price = 99000
        db.session.commit()
        self.assertIn('297.000 đ', self.client.get('/cart').get_data(as_text=True))
        self.post('/cart/1/decrease')
        self.post('/cart/1/remove')
        self.assertIn('Giỏ hàng trống', self.client.get('/cart').get_data(as_text=True))
        self.add()
        self.post('/cart/1/decrease')
        with self.client.session_transaction() as session:
            self.assertEqual(session['cart'], {})

    def test_empty_checkout_and_invalid_customer(self):
        self.assertTrue(self.client.get('/checkout').location.endswith('/cart'))
        self.add()
        for override in [{'phone': '1912345678'}, {'phone': '09123'}, {'email': 'bad'}, {'address': '   '}, {'payment': 'fake'}]:
            self.assertEqual(self.checkout(**override).status_code, 200)
        self.assertEqual(db.session.scalar(db.select(db.func.count(Order.id))), 1)

    def test_checkout_snapshot_and_shipping(self):
        before = db.session.get(Book, 1).stock
        self.add(quantity=2)
        response = self.checkout()
        self.assertEqual(response.status_code, 302)
        order = db.session.get(Order, 2)
        self.assertEqual((order.total, order.shipping_fee, order.status), (210000, 20000, 'pending'))
        self.assertEqual(db.session.get(Book, 1).stock, before - 2)
        self.assertEqual(order.items[0].unit_price, 95000)
        self.assertEqual(len(order.history), 1)
        with self.client.session_transaction() as session:
            self.assertNotIn('cart', session)
        self.assertEqual(self.client.get('/orders/2').status_code, 200)
        self.assertEqual(self.app.test_client().get('/orders/2').status_code, 404)
        db.session.get(Book, 1).price = 150000
        db.session.commit()
        self.assertIn('95.000 đ', self.client.get('/orders/2').get_data(as_text=True))
        self.add(quantity=2)
        self.checkout()
        self.assertEqual(db.session.get(Order, 3).shipping_fee, 0)
        # Reposting an empty cart never creates a second order.
        self.post('/checkout')
        self.assertEqual(db.session.scalar(db.select(db.func.count(Order.id))), 3)

    def test_insufficient_stock_rolls_back_entire_order(self):
        self.add(1, 2)
        self.add(2, 2)
        db.session.get(Book, 2).stock = 1
        db.session.commit()
        before = db.session.get(Book, 1).stock
        response = self.checkout()
        self.assertTrue(response.location.endswith('/cart'))
        db.session.expire_all()
        self.assertEqual(db.session.get(Book, 1).stock, before)
        self.assertEqual(db.session.scalar(db.select(db.func.count(Order.id))), 1)
        with self.client.session_transaction() as session:
            self.assertEqual(session['cart'], {'1': 2, '2': 2})

    def test_order_transitions_and_cancel_once(self):
        before = db.session.get(Book, 1).stock
        self.post('/admin/orders/1', {'status': 'completed'})
        self.assertEqual(db.session.get(Order, 1).status, 'pending')
        self.post('/admin/orders/1', {'status': 'shipping'})
        self.post('/admin/orders/1', {'status': 'cancelled'})
        db.session.expire_all()
        self.assertEqual(db.session.get(Book, 1).stock, before + 2)
        self.assertEqual(len(db.session.get(Order, 1).history), 3)
        self.post('/admin/orders/1', {'status': 'cancelled'})
        self.post('/admin/orders/1', {'status': 'pending'})
        self.assertEqual(db.session.get(Book, 1).stock, before + 2)
        self.assertEqual(len(db.session.get(Order, 1).history), 3)
        self.assertNotIn('name="status"', self.client.get('/admin/orders/1').get_data(as_text=True))

    def test_completed_revenue_and_terminal_state(self):
        self.post('/admin/orders/1', {'status': 'shipping'})
        self.post('/admin/orders/1', {'status': 'completed'})
        self.assertIsNotNone(db.session.get(Order, 1).completed_at)
        self.assertIn('460.000 đ', self.client.get('/admin').get_data(as_text=True))
        before = db.session.get(Book, 1).stock
        self.post('/admin/orders/1', {'status': 'cancelled'})
        self.assertEqual(db.session.get(Order, 1).status, 'completed')
        self.assertEqual(db.session.get(Book, 1).stock, before)

    def dashboard_context(self):
        contexts = []
        def capture(sender, template, context, **extra):
            contexts.append(context)
        with template_rendered.connected_to(capture, self.app):
            with patch('app.now', return_value=datetime(2026, 1, 3, 10, 0)):
                response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        return contexts[-1], response.get_data(as_text=True)

    def test_revenue_chart_empty_has_seven_days(self):
        context, html = self.dashboard_context()
        self.assertEqual(len(context['revenue_days']), 7)
        self.assertEqual([day['amount'] for day in context['revenue_days']], [0] * 7)
        self.assertEqual(context['revenue_total'], 0)
        self.assertGreater(context['chart_ceiling'], 0)
        self.assertIn('Chưa có đơn hàng hoàn tất', html)

    def test_revenue_chart_groups_by_completion_date_and_crosses_year(self):
        def add_order(status, completed_at, total):
            db.session.add(Order(customer_name='Khách thử biểu đồ', phone='0900000000',
                                 address='Huế', payment='cod', status=status, total=total,
                                 shipping_fee=0, created_at=datetime(2025, 12, 1),
                                 completed_at=completed_at))
        add_order('completed', datetime(2025, 12, 27, 23, 59, 59), 900000)  # Outside.
        add_order('completed', datetime(2025, 12, 28, 0, 0), 120000)  # First day boundary.
        add_order('completed', datetime(2025, 12, 28, 19, 30), 80000)
        add_order('completed', datetime(2026, 1, 1, 9, 0), 300000)
        add_order('completed', datetime(2026, 1, 3, 8, 30), 150000)  # Today.
        add_order('completed', datetime(2026, 1, 4, 0, 0), 900000)  # Tomorrow excluded.
        add_order('cancelled', datetime(2026, 1, 1, 12, 0), 900000)
        add_order('pending', None, 900000)
        db.session.commit()
        context, html = self.dashboard_context()
        days = context['revenue_days']
        self.assertEqual([day['date'].strftime('%d/%m') for day in days],
                         ['28/12', '29/12', '30/12', '31/12', '01/01', '02/01', '03/01'])
        self.assertEqual([day['amount'] for day in days], [200000, 0, 0, 0, 300000, 0, 150000])
        self.assertEqual(context['revenue_total'], 650000)
        self.assertEqual(context['revenue_count'], 4)
        self.assertEqual(context['revenue_peak'], 300000)
        # The monthly card includes January 4; the seven-day chart excludes it.
        self.assertEqual(context['stats'][2], 1350000)
        self.assertNotIn('Chưa có đơn hàng hoàn tất', html)
        self.assertIn('650.000 đ', html)

    def book_data(self, **overrides):
        data = dict(title='Sách mới', author='Tác giả', publisher='NXB', category_id=1,
                    year=2024, price=1000, stock=0, description='Mô tả')
        data.update(overrides)
        return data

    def test_book_validation_and_delete_guards(self):
        for changes in [dict(price=999), dict(stock=-1), dict(year=1899), dict(year=9999),
                        dict(title='LẬP TRÌNH PYTHON CƠ BẢN'), dict(category_id=999), dict(author='   ')]:
            response = self.post('/admin/books/new', self.book_data(**changes))
            self.assertEqual(response.status_code, 200)
        self.assertEqual(db.session.scalar(db.select(db.func.count(Book.id))), 6)
        response = self.post('/admin/books/new', self.book_data())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(db.session.get(Book, 7).stock, 0)
        self.post('/admin/books/7/edit', self.book_data(title='SÁCH MỚI', stock=4))
        self.assertEqual(db.session.get(Book, 7).stock, 4)
        self.post('/admin/books/1/delete')
        self.assertIsNotNone(db.session.get(Book, 1))
        self.post('/admin/books/7/delete')
        self.assertIsNone(db.session.get(Book, 7))

    def test_categories_and_group_counts(self):
        self.post('/admin/categories', {'name': 'mẠnG'})
        self.assertEqual(db.session.scalar(db.select(db.func.count(Category.id))), 6)
        self.post('/admin/categories/1/delete')
        self.assertIsNotNone(db.session.get(Category, 1))
        self.post('/admin/categories/6/delete')
        self.assertIsNone(db.session.get(Category, 6))
        self.post('/admin/categories', {'name': 'Văn học', 'description': 'Sách văn học'})
        self.assertIsNotNone(db.session.scalar(db.select(Category).where(Category.name_key == 'văn học')))

    def test_upload_replace_and_invalid_content(self):
        def image_file():
            data = io.BytesIO()
            Image.new('RGB', (30, 40), 'blue').save(data, 'PNG')
            data.seek(0)
            return data, 'cover.png'
        response = self.post('/admin/books/6/edit', self.book_data(title='Clean Code', cover=image_file()))
        self.assertEqual(response.status_code, 302)
        old = db.session.get(Book, 6).cover
        self.assertTrue((Path(self.app.config['UPLOAD_FOLDER']) / old).exists())
        self.post('/admin/books/6/edit', self.book_data(title='Clean Code', cover=image_file()))
        new = db.session.get(Book, 6).cover
        self.assertNotEqual(old, new)
        self.assertFalse((Path(self.app.config['UPLOAD_FOLDER']) / old).exists())
        self.post('/admin/books/6/edit', self.book_data(title='Clean Code'))
        self.assertEqual(db.session.get(Book, 6).cover, new)
        response = self.post('/admin/books/6/edit', self.book_data(title='Clean Code', cover=(io.BytesIO(b'fake image'), 'bad.png')))
        self.assertIn('Tệp không phải ảnh', response.get_data(as_text=True))
        response = self.post('/admin/books/6/edit', self.book_data(title='Clean Code', cover=(io.BytesIO(b'x' * (2*1024*1024+1)), 'huge.png')))
        self.assertIn('Ảnh tối đa 2 MB', response.get_data(as_text=True))

    def test_order_filter_totals_pagination_and_seed_idempotence(self):
        seed_data()
        self.assertEqual(db.session.scalar(db.select(db.func.count(Book.id))), 6)
        for i in range(11):
            order = Order(customer_name='Khách thử', phone='0900000000', address='Huế',
                          payment='cod', status='completed', shipping_fee=0, total=100000)
            order.history.append(OrderHistory(status='completed'))
            db.session.add(order)
        db.session.commit()
        text = self.client.get('/admin/orders?status=completed&q=Khách').get_data(as_text=True)
        self.assertIn('11 đơn theo bộ lọc', text)
        self.assertIn('1.100.000 đ', text)
        self.assertIn('page=2', text)
        self.assertIn('status=completed', text)
        self.assertIn('Nguyễn Văn An', self.client.get('/admin/orders?q=%231').get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
