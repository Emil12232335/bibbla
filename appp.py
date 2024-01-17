from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from os import path, makedirs, listdir

# Set the application configuration.
app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['SECRET_KEY'] = 'secret-key'

# Initialize the Flask-Login extension.
login_manager = LoginManager()
login_manager.init_app(app)

# Define a dictionary to store user data.
users = {}

# Add a new user to the system.
users['help'] = {'password': 'me'}

# Define a User class for the Flask-Login extension.
class User(UserMixin):
    def __init__(self, id, password):
        self.id = id
        self.password = password


@login_manager.user_loader
def user_loader(username):
    # This function is called when Flask-Login needs to load a user from their username.
    if username in users:
        user = User(username, users[username]['password'])
        return user
    else:
        return None


@app.route('/')
def index():
    # This page displays a simple message when the user is logged in or out.
    folders = [f for f in listdir(app.config['UPLOAD_FOLDER']) if path.isdir(path.join(app.config['UPLOAD_FOLDER'], f))]
    folders.sort()
    if not current_user.is_authenticated:
        flash('You must be logged in to access this page')
        return redirect(url_for('login'))
    else:
        return render_template('index.html', user=current_user, folders=folders)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # This page allows users to log in using their username and password.
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            user = User(username, password)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # Destroy the user's session and redirect them to the login page.
    logout_user()
    return redirect(url_for('index'))


@app.route('/<folder>/')
@login_required
def folder(folder):
    antfolder = folder + "/ant"
    anteckningar = [f for f in listdir(path.join(app.config['UPLOAD_FOLDER'], antfolder)) if path.isfile(path.join(app.config['UPLOAD_FOLDER'], antfolder, f))]
    booksfolder = folder + "/books"
    books = [f for f in listdir(path.join(app.config['UPLOAD_FOLDER'], booksfolder)) if path.isfile(path.join(app.config['UPLOAD_FOLDER'], booksfolder, f))]
    tentorfolder = folder + "/tentor"
    tentor = [f for f in listdir(path.join(app.config['UPLOAD_FOLDER'], tentorfolder)) if path.isfile(path.join(app.config['UPLOAD_FOLDER'], tentorfolder, f))]
    anteckningar.sort()
    books.sort()
    tentor.sort()
    return render_template('folder.html', anteckningar=anteckningar, books=books, tentor=tentor,folder=folder)


@app.route('/<folder>/<sub>/<filename>', methods=['GET'])
@login_required
def download(folder, sub, filename):
    return send_from_directory(path.join(app.config['UPLOAD_FOLDER'], folder, sub), filename, as_attachment=False)


@app.route('/preview/<folder>/<sub>/<filename>', methods=['GET'])
@login_required
def preview(folder, sub, filename):
    return send_from_directory(path.join(app.config['UPLOAD_FOLDER'], folder, sub), filename, as_attachment=False)


if __name__ == '__main__':
    if not path.exists(app.config['UPLOAD_FOLDER']):
        makedirs(app.config['UPLOAD_FOLDER'])

    with app.app_context():
        app.run(debug=False, host="0.0.0.0")
