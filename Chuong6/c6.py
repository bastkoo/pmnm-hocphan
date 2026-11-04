
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship,Mapped, mapped_column
from sqlalchemy import TEXT, String
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key_here"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.get("/them-mau")
def add_sample():
    total = db.session.scalar(
        db.select(db.func.count(Student.id))
    )
    if total > 0:
        return f"Đã có {total} sinh viên trong cơ sở dữ liệu. Không thêm nữa."
    an = Student(mssv="23T1080004", name="Nguyen Van A", gpa=8.5)
    before = an.id
    db.session.add(an)

    db.session.add_all([
        Student(mssv="23T1080005", name="Nguyen Van B", gpa=7.2),
        Student(mssv="23T1080006", name="Nguyen Van C", gpa=9.1),
        Student(mssv="23T1080007", name="Nguyen Van D", gpa=6.8),
        Student(mssv="23T1080008", name="Nguyen Van E", gpa=5.4),
    ])
    db.session.commit()
    return f"Đã thêm 5 mẫu sinh viên. ID trước commit: {before}, ID sau commit: {an.id}"

@app.get("/thu-truy-van")
def try_queries():
    if db.session.scalar(db.select(db.func.count(Student.id))) == 0:
        return "Cơ sở dữ liệu rỗng. Vui lòng truy cập /them-mau trước."
    line = []
    lines = []
    lines.append(f"1. get(3): {db.session.get(Student, 3)}")
    lines.append(f"2. get(99): {db.session.get(Student, 99)}")
    everyone = db.session.scalars(db.select(Student)).all()
    lines.append(f"3. Tất cả {len(everyone)} sinh viên")
    stmt = (db.select(Student).where(Student.gpa >= 8.0)).order_by(Student.gpa.desc())
    good = db.session.scalars(stmt).all()
    lines.append(f"4. Sinh viên có GPA >= 8.0: {good}")
    binh = db.session.scalar(db.select(Student).filter_by(mssv="23T1080005"))
    lines.append(f"5. Sinh viên với MSSV 23T1080005: {binh}")
    count = db.session.scalar(db.select(db.func.count(Student.id)))
    avg = db.session.scalar(db.select(db.func.avg(Student.gpa)))
    lines.append(f"6. Tổng số sinh viên: {count}, GPA trung bình: {avg:.2f}")

   
    return "\n".join(lines), 200, {'Content-Type': 'text/plain; charset=utf-8'}
@app.get("/ds-sinh-vien")
def list_students():
    students = db.session.scalars(db.select(Student).order_by(Student.gpa.desc())).all()
    return render_template('students.html', students=students)
class Student(db.Model):
    __tablename__ = 'students'
    id: Mapped[int] = mapped_column(primary_key=True)
    mssv: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gpa: Mapped[float] = mapped_column(default=0.0)

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)