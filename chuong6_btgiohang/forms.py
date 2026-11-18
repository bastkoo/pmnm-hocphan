from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import IntegerField, RadioField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, Regexp, ValidationError

from models import Book, Category, db, now


def strip_text(value):
    return value.strip() if value else value


class CheckoutForm(FlaskForm):
    customer_name = StringField('Họ tên *', filters=[strip_text], validators=[DataRequired(), Length(max=150)])
    phone = StringField('Số điện thoại *', filters=[strip_text], validators=[DataRequired(), Regexp(r'^0[0-9]{9}$', message='Số điện thoại gồm 10 chữ số, bắt đầu bằng 0.')])
    email = StringField('Email', filters=[strip_text], validators=[Optional(), Email(message='Email không đúng định dạng.'), Length(max=254)])
    address = TextAreaField('Địa chỉ giao hàng *', filters=[strip_text], validators=[DataRequired(), Length(max=1000)])
    note = TextAreaField('Ghi chú', validators=[Length(max=1000)])
    payment = RadioField('Thanh toán *', choices=[('cod', 'Tiền mặt khi nhận hàng'), ('bank', 'Chuyển khoản')], default='cod', validators=[DataRequired()])


class BookForm(FlaskForm):
    title = StringField('Tên sách *', filters=[strip_text], validators=[DataRequired(), Length(max=200)])
    author = StringField('Tác giả *', filters=[strip_text], validators=[DataRequired(), Length(max=150)])
    publisher = StringField('Nhà xuất bản', filters=[strip_text], validators=[Length(max=150)])
    category_id = SelectField('Danh mục *', coerce=int, validators=[DataRequired()])
    year = IntegerField('Năm xuất bản', validators=[Optional()])
    price = IntegerField('Giá (đồng) *', validators=[DataRequired(), NumberRange(min=1000, message='Giá phải từ 1.000 đồng.')])
    stock = IntegerField('Tồn kho *', validators=[NumberRange(min=0, message='Tồn kho không âm.')])
    description = TextAreaField('Mô tả', validators=[Length(max=10000)])
    cover = FileField('Ảnh bìa', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Chỉ nhận JPG, PNG, WEBP.'), FileSize(max_size=2 * 1024 * 1024, message='Ảnh tối đa 2 MB.')])

    def validate_title(self, field):
        existing = db.session.scalar(db.select(Book).where(Book.title_key == field.data.casefold()))
        if existing and existing.id != getattr(self, 'editing_id', None):
            raise ValidationError('Tên sách đã tồn tại.')

    def validate_year(self, field):
        if field.data is not None and not 1900 <= field.data <= now().year:
            raise ValidationError(f'Năm phải từ 1900 đến {now().year}.')


class CategoryForm(FlaskForm):
    name = StringField('Tên danh mục *', filters=[strip_text], validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Mô tả', validators=[Length(max=2000)])

    def validate_name(self, field):
        existing = db.session.scalar(db.select(Category).where(Category.name_key == field.data.casefold()))
        if existing and existing.id != getattr(self, 'editing_id', None):
            raise ValidationError('Danh mục đã tồn tại.')
