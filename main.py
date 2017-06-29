from flask import Flask, request, redirect, render_template, url_for

from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()
    return render_template('blog.html', page_title="Build a Blog", blogs=blogs)

@app.route('/entry', methods=['POST', 'GET'])
def go_to_entry():
    return render_template('entry.html', page_title="Build a Blog")



@app.route('/page', methods=['GET'] )
def page():

    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)

    return render_template('page.html', page_title=blog.title, entry=blog.body)



@app.route('/enter-data', methods=['POST', 'GET'])
def blog_entry():

    if request.method == 'POST':
        title = request.form['title']
        entry = request.form['entry']

        if title == '' or entry == '':
            return render_template('entry.html', title=title, entry=entry, page_title="Build a Blog")

        new_blog = Blog(title, entry)
        db.session.add(new_blog)
        db.session.commit()
    

    blogs = Blog.query.all()
    return render_template('page.html', entry=entry, page_title=title)


if __name__=='__main__':
    app.run()


