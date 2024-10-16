from flask import *
from flask_sqlalchemy import SQLAlchemy
import MySQLdb
from datetime import datetime

app=Flask(__name__)
app.secret_key="xac"
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:@localhost/college'
app.config['SQLALCHEMY_MODIFICATIONS']=True

db = SQLAlchemy(app)
class Signup(db.Model):
   sno= db.Column(db.Integer, primary_key = True,unique=True,nullable=False)
   name = db.Column(db.String(50),unique=False,nullable=False)
   email = db.Column(db.String(50),unique=True,nullable=False)
   address = db.Column(db.String(100),unique=False,nullable=False)
   password = db.Column(db.String(50),unique=False,nullable=False)
   confirm_password = db.Column(db.String(50),unique=False,nullable=False)

class Contact(db.Model):
   sno= db.Column(db.Integer, primary_key = True,unique=True,nullable=False)
   name = db.Column(db.String(50),unique=False,nullable=False)
   email = db.Column(db.String(50),unique=True,nullable=False)
   phone_num = db.Column(db.String(50),unique=False,nullable=False)
   mes = db.Column(db.String(50), unique=False, nullable=False)

# class Calendar(db.Model):
#     sno = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
#     from_date = db.Column(db.String(50), unique=False, nullable=False)
#     to_date = db.Column(db.String(50), unique=False, nullable=False)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(50), unique=False, nullable=False)
    price = db.Column(db.Integer, unique=False, nullable=False)
    speed = db.Column(db.Integer, unique=False, nullable=False)
    seats = db.Column(db.Integer, unique=False, nullable=False)
    image_url = db.Column(db.String(100), unique=False, nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_email = db.Column(db.String(50), db.ForeignKey('signup.email'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    booking_date = db.Column(db.String(50), nullable=False)
    from_date = db.Column(db.String(50), nullable=False)  # New field for from_date
    to_date = db.Column(db.String(50), nullable=False)  # New field for to_date


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact",methods=["GET","POST"])
def contact():
    if request.method=="POST":
        Username = request.form['name']
        Email = request.form['email']
        Phone=request.form['phone']
        Message=request.form['message']

        entry = Contact(name=Username, email=Email,phone_num=Phone,mes=Message)
        db.session.add(entry)
        db.session.commit()

    return render_template("contact.html")



@app.route("/bookings")
def bookings():
    if 'email' in session:
        return render_template('bookings.html')
    else:
        return render_template("signup.html")


# //corrected 1
# @app.route('/book_car', methods=['POST'])
# def book_car():
#     if 'email' in session:
#         car_id = request.form['car_id']  # Get the car ID from the form
#         user_email = session['email']  # Get the email of the logged-in user
#
#         # Check if the car is already booked by any user
#         existing_booking = Booking.query.filter_by(car_id=car_id).first()
#
#         if existing_booking:
#             # If the car is already booked, show an error message
#             message = "This car is already booked by another user!"
#             return render_template('cars.html', cars=Car.query.all(), message=message)
#         else:
#             # If the car is not booked, proceed with the booking
#             booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             new_booking = Booking(user_email=user_email, car_id=car_id, booking_date=booking_date)
#             db.session.add(new_booking)
#             db.session.commit()
#
#             # Redirect to the calendar page after a successful booking
#             return redirect(url_for('calender'))
#     else:
#         return redirect(url_for('login'))  # Redirect to login if the user is not logged in
@app.route('/book', methods=['POST'])
def book_car():
    user_email = session.get('email')
    car_id = request.form.get('car_id')
    from_date = request.form.get('from_date')
    to_date = request.form.get('to_date')

    # Validate that from_date and to_date are provided
    if not from_date or not to_date:
        flash('Please select both from and to dates for booking.', 'error')
        return redirect(url_for('calender'))

    try:
        # Convert string dates to datetime format
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')
    except ValueError:
        # Handle invalid date format
        flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
        return redirect(url_for('calender'))

    # Check if the car is already booked by any user in the requested date range
    existing_booking = Booking.query.filter(
        Booking.car_id == car_id,
        Booking.to_date >= from_date,   # Ensure that the requested from_date doesn't overlap
        Booking.from_date <= to_date    # Ensure that the requested to_date doesn't overlap
    ).first()

    if existing_booking:
        flash('This car is already booked for the selected dates.', 'error')
        return redirect(url_for('cars'))  # Redirect to the cars page

    # If no existing booking conflicts, proceed with the new booking
    new_booking = Booking(
        user_email=user_email,
        car_id=car_id,
        booking_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_date=from_date.strftime('%Y-%m-%d'),  # Save as string
        to_date=to_date.strftime('%Y-%m-%d')       # Save as string
    )
    db.session.add(new_booking)
    db.session.commit()
    flash('Car booked successfully!', 'success')

    return redirect(url_for('bookings'))


@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    if 'email' in session:
        user_email = session['email']  # Get the user's email
        car_id = request.form['car_id']  # Get the car ID from the form

        # Find the booking to delete
        booking_to_delete = Booking.query.filter_by(user_email=user_email, car_id=car_id).first()

        if booking_to_delete:
            db.session.delete(booking_to_delete)
            db.session.commit()
            message = "Your booking has been successfully canceled."
        else:
            message = "No booking found for this car."

        # Render cars.html again with the message
        return render_template('cars.html', cars=Car.query.all(), message=message)
    else:
        return redirect(url_for('login'))  # Redirect to login if the user is not logged in


@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    from_date = request.form.get('from_date')
    to_date = request.form.get('to_date')
    car_id = request.form.get('car_id')
    user_email = session.get('email')  # Get the current logged-in user's email

    # Validate dates
    if not from_date or not to_date:
        flash('Please select valid dates!', 'error')
        return redirect(url_for('calendar_page'))

    # Convert string to date format
    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')

    # Check if the user already has a booking for this car
    booking = Booking.query.filter_by(car_id=car_id, user_email=user_email).first()

    if booking:
        # Update the existing booking for this user and car
        booking.from_date = from_date
        booking.to_date = to_date
        db.session.commit()
        flash('Booking dates successfully updated!', 'success')
    else:
        # Create a new booking if it doesn't exist
        new_booking = Booking(
            user_email=user_email,
            car_id=car_id,
            booking_date=datetime.now(),
            from_date=from_date,
            to_date=to_date
        )
        db.session.add(new_booking)
        db.session.commit()
        flash('Car booked successfully!', 'success')

    return redirect(url_for('bookings'))


@app.route('/cars')
def cars():
    car_list = [
        {
            'id': 1,
            'name': 'Maruti Suzuki',
            'price': 20000,
            'speed': 150,
            'seats':7,
            'image_url': 'assets/img/Maruti_Suzuki.jpeg'
        },
        {
            'id': 2,
            'name': 'Toyota XUV',
            'price': 22000,
            'speed': 160,
            'seats': 6,
            'image_url': 'assets/img/Toyota_XUV.jpeg'
        },
        {
            'id': 3,
            'name': 'Tata Altroz',
            'price': 18000,
            'speed': 140,
            'seats': 6,
            'image_url': 'assets/img/Tata_Altroz.jpeg'
        },
        {
            'id': 4,
            'name': 'Mahindra XUV',
            'price': 25000,
            'speed': 170,
            'seats': 5,
            'image_url': 'assets/img/Mahindra_XUV.jpg'
        },
        {
            'id': 5,
            'name': 'Mahindra Thar',
            'price': 30000,
            'speed': 165,
            'seats': 4,
            'image_url': 'assets/img/mahindra_thar.jpg'
        }
    ]
    return render_template('cars.html', cars=car_list)


@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        Username = request.form['username']
        Email = request.form['email']
        Address = request.form['address']
        Password = request.form['password']
        Confirm_password = request.form['confirm_password']

        if Password == Confirm_password:
            entry = Signup(name=Username, email=Email, address=Address, password=Password, confirm_password=Confirm_password)
            db.session.add(entry)
            db.session.commit()
            return redirect('/login')
        else:
            msg = "Passwords do not match"
            return render_template("signup.html", msg=msg)

    return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    # if 'user' in session:
    #     message = "You are already logged in"
    #     return render_template('index.html')
    if request.method == 'POST':
        Email = request.form['email']
        Password = request.form['password']
        user = Signup.query.filter_by(email=Email).first()

        if user and user.password == Password:
            session['email'] =Email
            message = "You have successfully logged in"
            return render_template('index.html',msg=message)
        else:
            msg = "Invalid username or password"
            return render_template("login.html", msg=msg)

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('email',None)
    return  redirect('/')

@app.route('/drivers')
def drivers():
    return render_template('drivers.html')



@app.route("/calender")
def calender():
    return render_template("calender.html")



if __name__=='__main__':
    app.run(debug=True)