from flask import Flask, render_template, request, redirect, flash, url_for, session, logging 
# from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt 
from functools import wraps 


app = Flask(__name__)

# config myssql
app.config['SECRET_KEY'] = 'you_can_never_guess'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'yabal'
app.config['MYSQL_PASSWORD'] = 'Yabal@911*' 
app.config['MYSQL_DB'] = 'news21'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MYSQL
mysql = MySQL(app)

# Articles = Articles()
# home
@app.route("/")
def home():
    return render_template("home.html")
# about
@app.route('/about')
def about():
    return render_template("about.html")

# articles
@app.route('/articles') 
def articles():
    # cerate cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=articles)

    else:
        msg = 'No Articles Found'    
        return render_template("articles.html", msg=msg)
    
    # close connection
    cur.close()

# articles
@app.route('/article/<string:id>/') 
def article(id):
    # create cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute('SELECT * FROM articles WHERE id = %s', [id])

    article = cur.fetchone()

    return render_template('article.html', article = article)
    

# register form class 
class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField(' Password', [
        validators.DataRequired(),
        validators.EqualTo('comfirm', message='Passwords must match')
    ])
    comfirm = PasswordField('Comfirm Password')
# register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # create cursor
        cur = mysql.connection.cursor()

        #  execute cursor
        cur.execute('INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)', (name, email, username, password))

        # commit to db
        mysql.connection.commit()

        # close connection
        cur.close()

        flash('You are now registered and can login', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# login now
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        #  Get form field
        username = request.form['username']
        candidate_password = request.form['password']
        
        # Create cursor
        cur = mysql.connection.cursor()
        
        # GEt user by username
        result = cur.execute("SELECT * FROM users  WHERE username = %s", [username])

        if result > 0:

            # get stored hash 
            data = cur.fetchone()
            password = data['password']
        
            # compare password
            if sha256_crypt.verify(candidate_password, password):
                #  passes   
                session['logged_in'] = True
                session['username'] = username

                flash('you are loged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error  = 'Invalid login'
                return render_template('login.html', error = error)
            # close connection
            cur.close()
        else:        
            error = 'Username not found' 
            return render_template('login.html', error = error)

    return render_template("login.html")


# is logged in 
def is_logged_in(f):  
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please login', 'danger')  
        return redirect(url_for('login'))
        if 'logged_out' in session:
            return f(*args, **kwargs)
    return wrap   
    
# logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are logged out', 'success')
    return redirect(url_for("login"))   


# dashboard
@app.route("/dashboard", methods=["GET", "POST"])
@is_logged_in   
def dashboard():
    # cerate cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles=articles)

    else:
        msg = 'No Articles Found'    
        return render_template("dashboard.html", msg=msg)
    
    # close connection
    cur.close()


# article form class 
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])
    
# add article
@app.route("/add_article", methods= ['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # create cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute('INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)',(title, body, session['username']))

        # commit to DB
        mysql.connection.commit() 

        # close connection
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form =form)    


# edit article
@app.route("/edit_article/<string:id>", methods = ["GET", "POST"])
@is_logged_in
def edit_article(id):

    # create cuesor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute('SELECT * FROM articles WHERE id = %s' [id])
    
    article = cur.fetchone()

    # Get form
    form = ArticleForm(request.form)
    
    # populate article form fields
    form.title.date = article['title']
    form.body.date = article['body']

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # create cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute('UPDATE articles SET  name=%s, body=%s WHERE id = %s', (name, body, id))

        # commit to DB
        mysql.connection.commit() 

        # close connection
        cur.close()

        flash('Article updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template("edit_article.html", form=form)    

  
if __name__ == '__main__':
    app.run() 