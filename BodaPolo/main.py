from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import openpyxl
import io
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    attendance = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    special_menu = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    full_name = request.form.get('fullName')
    attendance = request.form.get('attendance')
    contact = request.form.get('contact')
    special_menu = request.form.get('specialMenu')
    
    print(f"Received data - full_name: {full_name}, attendance: {attendance}, contact: {contact}, special_menu: {special_menu}")
    
    if not full_name or not attendance or not contact:
        flash('Please fill out all required fields')
        return redirect(url_for('index'))

    try:
        new_rsvp = RSVP(full_name=full_name, attendance=attendance, contact=contact, special_menu=special_menu)
        db.session.add(new_rsvp)
        db.session.commit()
        flash('Datos guardados exitosamente.')
    except Exception as e:
        db.session.rollback()
        flash('Error al guardar los datos: ' + str(e))
    
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('data'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/data')
@login_required
def data():
    rsvps = RSVP.query.all()
    return render_template('data.html', rsvps=rsvps)

@app.route('/download')
@login_required
def download():
    rsvps = RSVP.query.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "RSVPs"

    headers = ['Nombre Completo', 'Asistirás al evento?', 'Contacto', '¿Necesitas menú especial?']
    ws.append(headers)

    for rsvp in rsvps:
        ws.append([rsvp.full_name, rsvp.attendance, rsvp.contact, rsvp.special_menu])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='rsvps.xlsx', as_attachment=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
