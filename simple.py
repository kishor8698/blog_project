import os
from datetime import datetime

from flask import Flask, request, flash, redirect
from flask.templating import render_template
from flask_login import LoginManager, login_user, UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SECRET_KEY"] = "thisissecret"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


migrate=Migrate(app,db)
manager=Manager(app)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password = db.Column(db.String(100), index=True)
    address = db.Column(db.String(256))
    city = db.Column(db.String(64), index=True)

    def __repr__(self):
        return '<User % r>' % self.email,self.password,self.address,self.city
    
class Blog(db.Model):
    blog_id= db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(80),nullable=False)
    author=db.Column(db.String(80),nullable=False)
    content=db.Column(db.Text(),nullable=False)
    pb_date=db.Column(db.DateTime(),nullable=False,default=datetime.utcnow)
    b_img=db.Column(db.String(80),nullable=False)
 
    
    def __repr__(self):
        return '<Blog % r>' % self.pb_date
    



db.create_all()
UPLOAD_FOLDER = 'first_project/static/blog_img/'    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index_fun():
    result=Blog.query.all()
    return render_template('index.html',result=result)
    # return "<p>Hello, World!</p>"


@app.route("/main")
def main_fun():
    return render_template('main.html')


@app.route("/login", methods=['POST', 'GET'])
def login_fun():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email,password)
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            flash('Login Successfully','success')
            return redirect("/")
        else:
            flash('Invalid User', 'danger')
            return redirect("/login")

    return render_template('login.html')

@app.route("/logout")
def logout_fun():
    logout_user()
    return redirect("/")

@app.route("/blogpost",methods=['POST','GET'])
def blogpost_fun():
    if request.method == "POST":
        title=request.form.get('title')
        author=request.form.get('author')
        content=request.form.get('content')
        file=request.files['file']
        if file.filename == '':
        	flash('No image selected for uploading','danger')
	        return redirect("/blogpost")
     
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    
        #f= secure_filename(file.filename)
        #file.save('first_project/static/blog_img/'+file.filename)
        #save data into database
            result=Blog(title=title,author=author,content=content)
            db.session.add(result)
            db.session.commit()
            flash("Blog has been Posted",'info')
            return redirect("/")
        else:
            flash("Allowed image types are -> png, jpg, jpeg, gif","danger")
            return redirect("/blogpost")  
          
    return render_template("/blog.html")

@app.route("/blog_details/<int:id>",methods=["GET","POST"])
def blog_details_fun(id):
    blog=Blog.query.get(id)
    print(blog)
    return render_template("blog_details.html",blog=blog)
    
@app.route("/delete_blog/<int:id>",methods=["POST","GET"])
def delete_blog(id):
    result=Blog.query.get(id)
    db.session.delete(result)
    db.session.commit()
    flash("Record Deleted Successfully",'success')
    return redirect("/")

@app.route("/edit_blog/<int:id>",methods=["POST","GET"])
def edit_blog(id):
    result=Blog.query.get(id)
    if request.method == 'POST':
        
        if result.title != request.form['title'] or result.author != request.form['author'] or result.content != request.form['content']:
            
            result.title=request.form['title']
            result.author=request.form['author']
            result.content=request.form['content']
            db.session.commit()
            flash("Post has been Updated","success")
            return redirect("/")
        else:
            flash("You Have not Updated your data........",'warning')
            return redirect("/")
            
    result=Blog.query.get(id)
    
    return render_template('edit_blog.html',result=result)
    


@app.route("/r_user_list",methods=['GET','POST'])
def user_list():
    result=User.query.all()
    return render_template('registered_user.html',result=result)


@app.route("/register", methods=['POST', 'GET'])
def register_fun():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        city = request.form.get('city')
        print(email, password, address, city)
        try:
            result = User(email=email, password=password, address=address, city=city)
            db.session.add(result)
            db.session.commit()
            flash('User Has been Successfully registered...', 'success')
            return redirect("/login")
        except:
            flash('User is already registered...','danger')
            print('this is except block')
            return redirect('/register')
            

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
