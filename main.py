from flask import Flask, request, redirect, render_template, session, flash

from flask_sqlalchemy import SQLAlchemy 
import hashlib

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'MakeAWish'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'users', 'page', 'blog_page']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']



        password_hash = hashlib.sha256(str.encode(password)).hexdigest()


        user = User.query.filter_by(username=email).first()

        if user and user.password == password_hash:
            session['email'] = email
            flash("Logged in")
            return render_template('entry.html')
        elif user and user.password != password_hash:
            flash('User password incorrect', 'error')
            return render_template('login.html')
        else:
            flash('User does not exist, please register', 'error')
            return render_template('register.html')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_hash = hashlib.sha256(str.encode(password)).hexdigest()
        verify = request.form['verify']

        if len(email) < 3:
            flash('username must be at least 3 characters', 'error')
            return render_template('register.html')
        if len(password) < 3:
            flash('password must be at least 3 haracters', 'error')
            return render_template('register.html')
        if password != verify:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        existing_user = User.query.filter_by(username=email).first()
        if not existing_user:
            new_user = User(email, password_hash)
            db.session.add(new_user)
            db.session.commit()

            session['email'] = email

            return redirect('/')
        else:
            flash('User already exist', 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    flash('You have successfully logged out')
    return redirect('/')



@app.route('/allblogs', methods=['POST', 'GET'])
def blog_page():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['entry']

        owner = User.query.filter_by(username=session['email']).first()

        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()

    users = User.query.all()
    blogs = Blog.query.all()
    return render_template('blog.html', page_title="Welcome to Blogz", blogs=blogs, users=users)

@app.route('/entry', methods=['POST', 'GET'])
def go_to_entry():
    return render_template('entry.html', page_title="Build a Blog")



@app.route('/page', methods=['GET'] )
def page():

    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)
    users = User.query.all()
    return render_template('page.html', page_title=blog.title, entry=blog.body, blog=blog, users=users)



@app.route('/enter-data', methods=['POST', 'GET'])
def entry():

    owner = User.query.filter_by(username=session['email']).first()

    if request.method == 'POST':
        title = request.form['title']
        entry = request.form['entry']

        if title == '' or entry == '':
            return render_template('entry.html', title=title, entry=entry, page_title="Blogz")

        new_blog = Blog(title, entry, owner)
        db.session.add(new_blog)
        db.session.commit()
    
    users = User.query.all()
    return render_template('page.html', entry=entry, page_title=title, blog=new_blog, users=users)


@app.route('/blog', methods=['GET'])
def users():
    owner_id = request.args.get('user_id')
    blogs = Blog.query.filter_by(owner_id=owner_id).all()
    users = User.query.all()
    return render_template('blog.html', blogs=blogs, users=users, page_title="Blogz")

@app.route('/')
def index():
    users = User.query.all()

    return render_template('index.html', users=users)



if __name__=='__main__':
    app.run()


