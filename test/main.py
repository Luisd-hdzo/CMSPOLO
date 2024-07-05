from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Tabla intermedia para la relación Many-to-Many entre Person y Event
attendees = db.Table('attendees',
    db.Column('person_id', db.Integer, db.ForeignKey('person.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

# Modelos de Base de Datos
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    job = db.Column(db.String(100))
    vehicle = db.Column(db.String(100))
    house_color = db.Column(db.String(50))
    favorite_food = db.Column(db.String(100))
    birthdate = db.Column(db.Date)
    purchase_history = db.Column(db.Text)
    gender = db.Column(db.String(20))
    facebook = db.Column(db.String(100))
    twitter = db.Column(db.String(100))
    instagram = db.Column(db.String(100))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    organizer_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    attendees = db.relationship('Person', secondary=attendees, lazy='subquery',
        backref=db.backref('events', lazy=True))

class Relation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person1_name = db.Column(db.String(100), nullable=False)
    person2_name = db.Column(db.String(100), nullable=False)

# Rutas y Controladores
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        job = request.form['job']
        vehicle = request.form['vehicle']
        house_color = request.form['house_color']
        favorite_food = request.form['favorite_food']
        birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date() if request.form['birthdate'] else None
        purchase_history = request.form['purchase_history']
        gender = request.form['gender']
        facebook = request.form['facebook']
        twitter = request.form['twitter']
        instagram = request.form['instagram']
        
        new_person = Person(
            name=name,
            address=address,
            phone=phone,
            job=job,
            vehicle=vehicle,
            house_color=house_color,
            favorite_food=favorite_food,
            birthdate=birthdate,
            purchase_history=purchase_history,
            gender=gender,
            facebook=facebook,
            twitter=twitter,
            instagram=instagram
        )
        try:
            db.session.add(new_person)
            db.session.commit()
            flash('Persona agregada exitosamente!', 'success')
            return redirect(url_for('index'))
        except:
            flash('Hubo un error al agregar la persona', 'danger')
    return render_template('add_person.html')

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        event_name = request.form['event_name']
        organizer_name = request.form['organizer_name']
        date = request.form['date']
        attendees_text = request.form['attendees']
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        new_event = Event(event_name=event_name, organizer_name=organizer_name, date=date_obj)
        try:
            db.session.add(new_event)
            db.session.commit()
            attendee_names = attendees_text.strip().split('\n')
            for attendee_name in attendee_names:
                attendee_name = attendee_name.strip()
                person = Person.query.filter_by(name=attendee_name).first()
                if not person:
                    person = Person(name=attendee_name)
                    db.session.add(person)
                    db.session.commit()
                new_event.attendees.append(person)
            db.session.commit()
            flash('Evento agregado exitosamente!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Hubo un error al agregar el evento: {e}', 'danger')
    return render_template('add_event.html')

@app.route('/add_relation', methods=['GET', 'POST'])
def add_relation():
    if request.method == 'POST':
        person1_name = request.form['person1_name']
        person2_name = request.form['person2_name']
        new_relation = Relation(person1_name=person1_name, person2_name=person2_name)
        try:
            db.session.add(new_relation)
            db.session.commit()
            flash('Relación agregada exitosamente!', 'success')
            return redirect(url_for('index'))
        except:
            flash('Hubo un error al agregar la relación', 'danger')
    return render_template('add_relation.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        try:
            date_obj = datetime.strptime(search_term, '%Y-%m-%d').date()
            events = Event.query.filter_by(date=date_obj).all()
        except ValueError:
            events = Event.query.filter(
                Event.event_name.ilike(f'%{search_term}%') |
                Event.organizer_name.ilike(f'%{search_term}%')
            ).all()
            persons = Person.query.filter(Person.name.ilike(f'%{search_term}%')).all()
            events += [event for person in persons for event in person.events]

        return render_template('search.html', events=events)
    return render_template('search.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0')
