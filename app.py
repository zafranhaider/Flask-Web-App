from flask import Flask, render_template, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, login_required, logout_user
from model import db, User, Contact

app = Flask(__name__, template_folder='template')
app.secret_key = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)
admin = Admin(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Create admin views for your models
class UserModelView(ModelView):
    can_delete = False
    column_searchable_list = ['username']
    column_filters = ['username']

admin.add_view(UserModelView(User, db.session))
admin.add_view(ModelView(Contact, db.session))

# Define user loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/adm')
@login_required
def adm():
    contacts = Contact.query.all()
    return render_template('adm.html', contacts=contacts)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # Login user using Flask-Login's login_user function
            login_user(user)
            # Redirect the user back to the originally requested page (if any)
            next_page = request.args.get('next')
            return redirect(next_page or '/adm')

        flash('Invalid username or password. Please try again.', 'error')
        return redirect('/login')

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/Reg', methods=['GET', 'POST'])
def Reg():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect('/Reg')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect('/login')
    return render_template('Reg.html')

#Contacts
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    contact = Contact(name=name, email=email, message=message)
    db.session.add(contact)
    db.session.commit()
    
    return redirect('/contact')

if __name__ == '__main__':
    app.run(debug=True)