from flask import Flask, render_template, request, flash, session, redirect
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
import yaml
import os

app = Flask(__name__)
Bootstrap(app)
CKEditor(app)    # app is now ckeditor enabled

#configure db
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']  # for the tuple error
mysql = MySQL(app) 
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')

def index(): # display all available blogs as a link

    cur=mysql.connection.cursor()
    values = cur.execute("SELECT * FROM blog")
    if values > 0:
        blogs = cur.fetchall()
        cur.close()
        return render_template ('index.html', blogs = blogs)
    else:
        cur.close()
        return render_template ('index.html', blogs = None)


@app.route('/about/')

def about():
    
    return render_template ('about.html')

@app.route('/register/', methods = ["GET", "POST"])

def register():
    if request.method == "POST":
        try:
            userInfo = request.form
            first_name = userInfo['first_name']
            last_name = userInfo['last_name']
            username = userInfo['username']
            email = userInfo['email']
            password = generate_password_hash(userInfo['password'])
            
        except:
            flash("Input unsuccessful.", 'danger')
            return render_template ('register.html')   

        else:
            if userInfo['password'] == userInfo['password_confirm']:
                cur = mysql.connection.cursor()  
                cur.execute("INSERT INTO blog_user(first_name, last_name, username, email, password) VALUES (%s, %s, %s, %s, %s)", [first_name, last_name, username, email, password])  
                mysql.connection.commit()        # to execute operation in SQL query
                flash("Successfully inserted data!", 'success')   
                return redirect('/login')
            else:
                flash("Passwords do not match.", 'danger')
                return render_template ('register.html')

    
    return render_template ('register.html')


@app.route('/login/', methods = ["GET", "POST"]) # check username and password showing in the url

def login():

    if request.method == "POST":
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']
        cur=mysql.connection.cursor()
        values = cur.execute("SELECT * FROM blog_user WHERE username = %s", [username])   
        if values > 0: # check that this username does exist
            user = cur.fetchone() # fetch info for this user
            if check_password_hash(user[5], password): # check that hashed password matches inserted pw
                session['login'] = True
                session['username'] = user[3]
                session['firstName'] = user [1]
                session['lastName'] = user [2]
                cur.close() 
                flash("Welcome back {}, you have been successfully logged in!".format(session['firstName']), 'success')
                return redirect ('/')

            else:
                cur.close()
                flash("That password is incorrect.", 'danger')
                return render_template ('login.html')
        
        else:
            cur.close()
            flash("That user does not exist.", 'danger')

    return render_template ('login.html')


@app.route('/logout/')

def logout():

    session['login'] = False
    flash("You have been succesfully logged out.", 'success')
    return redirect ('/')


@app.route('/write-blog/', methods = ["GET", "POST"])

def write_blog():

    if request.method == "POST":
        blogInfo = request.form
        title = blogInfo['title']
        text = blogInfo['text']
        author = session ['firstName'] + ' ' + session ['lastName']
        cur = mysql.connection.cursor()  
        cur.execute("INSERT INTO blog(title, author, body) VALUES (%s, %s, %s)", [title, author, text])  
        mysql.connection.commit()
        cur.close()
        flash("Successfully created blog post!", 'success')
        return redirect ('/')

    return render_template ('write-blog.html')

@app.route('/blogs/<int:id>/')
   
def blogs(id): # display blog that has been clicked on at index

    cur = mysql.connection.cursor()
    value = cur.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
    if value > 0:
        blog = cur.fetchone()
        return render_template ('blogs.html', blog = blog)
    else:
        return 'Blog not found'


@app.route('/myblogs/')
   
def my_blogs(): 


    author = session ['firstName'] + ' ' + session ['lastName']
    cur = mysql.connection.cursor()
    value = cur.execute("SELECT * FROM blog WHERE author = %s",[author])
    if value > 0:
        myblogs = cur.fetchall()
        return render_template ('myblogs.html', myblogs = myblogs)   
    else:
        return render_template ('myblogs.html', myblogs = None)


@app.route('/delete-blog/<int:id>/')

def delete_blog(id):

    cur = mysql.connection.cursor()   
    cur.execute("DELETE FROM blog WHERE blog_id = %s", [id])  
    mysql.connection.commit()        
    cur.close()
    flash("This blog post has been deleted.", 'success')
    return redirect ('/myblogs/')




    




if __name__ == "__main__":
   app.run(debug=True)