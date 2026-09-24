from flask import request, Flask, render_template
app = Flask(__name__)
@app.route("/", methods=['GET','POST'])
def home():
    a = None
    b = None
    cong = tru = nhan = chia = None
    if request.method == 'POST':
        try:
            a = float(request.form.get('a',0))
            b = float(request.form.get('b',0))
            cong = a + b
            tru = a - b
            nhan = a * b
            if b != 0:
                chia = round(a / b, 4) # Làm tròn 4 chữ số thập phân
            else:
                chia = "Không thể chia cho 0"
        except ValueError:
            pass

    #return "Xin chao"
    return render_template("math.html", a = a, b = b, cong= cong, tru = tru, nhan=nhan, chia = chia)
if __name__== "__main__":
    app.run(debug=True)