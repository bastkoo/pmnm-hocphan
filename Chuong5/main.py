from flask import Flask, render_template, request

app = Flask(__name__)

def validate_score(val_str):
    if not val_str:
        raise ValueError("Không được để trống điểm.")
    normalized = val_str.replace(',', '.')
    score = float(normalized)
    if not (0 <= score <= 10):
        raise ValueError("Điểm phải nằm trong khoảng từ 0 đến 10.")
    return score

@app.route('/', methods=['GET', 'POST'])
@app.route('/bai1', methods=['GET', 'POST'])
def bai1():
    num_a = ''
    num_b = ''
    op = '+'
    result = None
    error = None

    if request.method == 'POST':
        num_a = request.form.get('num_a', '').strip()
        num_b = request.form.get('num_b', '').strip()
        op = request.form.get('op', '+')

        val_a_str = num_a.replace(',', '.')
        val_b_str = num_b.replace(',', '.')

        try:
            a = float(val_a_str)
            b = float(val_b_str)

            if op == '+':
                res = a + b
            elif op == '-':
                res = a - b
            elif op == '*':
                res = a * b
            elif op == '/':
                if b == 0:
                    error = "Lỗi: Không thể chia cho 0!"
                else:
                    res = a / b
            else:
                error = "Phép toán không hợp lệ!"

            if error is None:
                if res.is_integer():
                    result = int(res)
                else:
                    result = str(round(res, 6)).replace('.', ',')

        except ValueError:
            error = "Lỗi: Vui lòng nhập số hợp lệ!"

    return render_template(
        'bai1.html',
        num_a=num_a,
        num_b=num_b,
        op=op,
        result=result,
        error=error,
        active_page='bai1'
    )

@app.route('/bai2', methods=['GET', 'POST'])
def bai2():
    cc_str = ''
    gk_str = ''
    ck_str = ''
    diem_hp = None
    diem_chu = None
    error = None

    if request.method == 'POST':
        cc_str = request.form.get('cc', '').strip()
        gk_str = request.form.get('gk', '').strip()
        ck_str = request.form.get('ck', '').strip()

        try:
            cc = validate_score(cc_str)
            gk = validate_score(gk_str)
            ck = validate_score(ck_str)

            raw_hp = (cc * 0.1) + (gk * 0.3) + (ck * 0.6)
            diem_hp = round(raw_hp, 1)

            if ck < 1:
                diem_chu = 'F'
            else:
                if diem_hp >= 8.5:
                    diem_chu = 'A'
                elif diem_hp >= 7.0:
                    diem_chu = 'B'
                elif diem_hp >= 5.5:
                    diem_chu = 'C'
                elif diem_hp >= 4.0:
                    diem_chu = 'D'
                else:
                    diem_chu = 'F'

        except ValueError as e:
            error = f"Lỗi: {str(e)}"

    return render_template(
        'bai2.html',
        cc=cc_str,
        gk=gk_str,
        ck=ck_str,
        diem_hp=str(diem_hp).replace('.', ',') if diem_hp is not None else None,
        diem_chu=diem_chu,
        error=error,
        active_page='bai2'
    )

# --- ROUTE BÀI 3 (TÍNH CHỈ SỐ BMI) ---
@app.route('/bai3', methods=['GET', 'POST'])
def bai3():
    chieu_cao_str = ''
    can_nang_str = ''
    bmi = None
    phan_loai = ''
    mau_sac = '' # Bootstrap alert color: success, warning, danger
    can_nang_ly_tuong = ''
    error_cc = None
    error_cn = None

    if request.method == 'POST':
        chieu_cao_str = request.form.get('chieu_cao', '').strip()
        can_nang_str = request.form.get('can_nang', '').strip()

        # Kiểm tra chiều cao (50 - 250 cm)
        try:
            if not chieu_cao_str:
                error_cc = "Vui lòng nhập chiều cao."
            else:
                cc_val = float(chieu_cao_str.replace(',', '.'))
                if not (50 <= cc_val <= 250):
                    error_cc = "Chiều cao phải từ 50cm đến 250cm."
        except ValueError:
            error_cc = "Chiều cao không hợp lệ."

        # Kiểm tra cân nặng (10 - 300 kg)
        try:
            if not can_nang_str:
                error_cn = "Vui lòng nhập cân nặng."
            else:
                cn_val = float(can_nang_str.replace(',', '.'))
                if not (10 <= cn_val <= 300):
                    error_cn = "Cân nặng phải từ 10kg đến 300kg."
        except ValueError:
            error_cn = "Cân nặng không hợp lệ."

        # Nếu không có lỗi, tiến hành tính toán BMI chuẩn người châu Á
        if not error_cc and not error_cn:
            cc_m = cc_val / 100.0  # Đổi cm sang mét
            raw_bmi = cn_val / (cc_m ** 2)
            bmi = round(raw_bmi, 1)

            # Phân loại & màu sắc kết quả
            if bmi < 18.5:
                phan_loai = "Thiếu cân"
                mau_sac = "warning"  # Vàng
            elif bmi < 23.0:
                phan_loai = "Bình thường (Khỏe mạnh)"
                mau_sac = "success"  # Xanh lá
            elif bmi < 25.0:
                phan_loai = "Thừa cân"
                mau_sac = "warning"  # Vàng
            else:
                phan_loai = "Béo phì"
                mau_sac = "danger"   # Đỏ

            # Tính khoảng cân nặng lý tưởng ứng với BMI từ 18.5 đến 22.9
            min_lt = round(18.5 * (cc_m ** 2), 1)
            max_lt = round(22.9 * (cc_m ** 2), 1)
            can_nang_ly_tuong = f"{min_lt} kg - {max_lt} kg"

    return render_template(
        'bai3.html',
        chieu_cao=chieu_cao_str,
        can_nang=can_nang_str,
        bmi=str(bmi).replace('.', ',') if bmi is not None else None,
        phan_loai=phan_loai,
        mau_sac=mau_sac,
        can_nang_ly_tuong=can_nang_ly_tuong,
        error_cc=error_cc,
        error_cn=error_cn,
        active_page='bai3'
    )

if __name__ == '__main__':
    app.run(debug=True)