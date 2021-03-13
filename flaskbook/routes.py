from flask import render_template, url_for, flash, redirect, request, abort
from flaskbook import app, db, bcrypt
from flaskbook.forms import RegistrationForm, LoginForm, AddBookForm, UpdateAccountForm
from flaskbook.models import UserModel, Book
from flask_login import login_user, current_user, logout_user, login_required


""" creating routes and rendering templates """

# index redirects
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('my_books'))
    else:
        return redirect(url_for('login'))

# user stuff
@app.route('/register', methods=['GET', 'POST'])
def register():
    # redirect user if authenticated
    if current_user.is_authenticated:
        return redirect(url_for('my_books'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # hash password, store form input with hashed pw in db
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = UserModel(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('my_books'))
    form = LoginForm()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('my_books'))
        else:
            flash('Login Unsuccessful. Please chek email and password.', 'danger')
    return render_template('login.html', title='Log In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# user books and book stats displayed
# TODO: delete this shit and the .html file
@app.route('/my_books')
def my_books():
    books = Book.query.all()
    return render_template('my_books.html', title='User Page', books=books)

# TODO: rename this into 'my_books', add delete, complete and update functionality
# TODO: add html buttons for above mentioned functionality
# BASICALLY: copy stuff from the 'book' route and add 'complete'
# TODO: add 'complete' route
@app.route('/actual_my_books/<string:username>')
@login_required
def actual_my_books(username):
    if username != current_user.username:
        abort(403)
    else:
        user = UserModel.query.filter_by(username=username).first_or_404()
        books = Book.query.filter_by(user_book=user)
        return render_template('actual_my_books.html', books=books, user=user)


# change user stuff
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)

# book stuff
@app.route('/book/add', methods=['GET', 'POST'])
@login_required
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data, author=form.author.data, num_pages=form.num_pages.data, complete=False, user_book=current_user)
        db.session.add(book)
        db.session.commit()
        flash(f"{form.title.data}, {form.author.data} has been added as current book!", 'success')
        # TODO: fix this redirect
        return redirect(url_for('my_books'))
    return render_template('new_book.html', title = 'Add Book', form = form, legend='Add Book')

@app.route('/book/<int:book_id>')
def book(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book.html', title=book.title, book=book)

@app.route('/book/<int:book_id>/update', methods=['GET', 'POST'])
@login_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.user_book != current_user:
        abort(403)
    form = AddBookForm()
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.num_pages = form.num_pages.data
        db.session.commit()
        flash('Book info has been updated!')
        return redirect(url_for('book', book_id=book.id))
    elif request.method == 'GET':
        form.title.data = book.title
        form.author.data = book.author
        form.num_pages.data = book.num_pages
    return render_template('new_book.html', title='Update Book Info', form=form, legend='Update Book Info')

@app.route('/book/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.user_book != current_user:
        abort(403)
    db.session.delete(book)
    db.session.commit()
    flash('Book has been deleted!', 'success')
    # TODO: fix this route
    return redirect(url_for('my_books'))
