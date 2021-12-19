from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
#from flaskext.mysql import MySQL
from flask_mysqldb import MySQL

from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import email_validator
from passlib.hash import sha256_crypt
from functools import wraps


# User Decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash(
                "Bu sayfayı sadece kayıtlı kullanıcılar görebilir. Lütfen giriş yapın.", "danger")
            return redirect(url_for("login"))
    return decorated_function

# Kullanıcı Kayıt Formu


class RegisterForm(Form):
    name_surname = StringField("İsim Soyisim", validators=[validators.Length(
        min=4, max=25, message="Lütfen geçerli bir isim soyisim giriniz")])
    username = StringField("Kullanıcı Adı", validators=[validators.Length(
        min=5, max=35, message="Lütfen geçerli bir kullanıcı adı giriniz.")])
    emailaddress = StringField("Email Adresi", validators=[validators.Email(
        message="Lütfen geçerli bir email adresi giriniz.")])
    city = StringField("Şehir", validators=[validators.Length(
        min=5, max=10, message="Lütfen geçerli bir şehir adı giriniz.")])
    blood_group = StringField("Kan Grubu(Rh değeriyle)", validators=[validators.Length(
        min=1, max=3, message="Lütfen geçerli bir kan grubu giriniz(AB+,0+).")])
    diseases = StringField("Hastalıklar", validators=[validators.Length(
        min=3, max=30)])
    password = PasswordField("Parola:", validators=[
        validators.DataRequired(message="Lütfen Geçerli bir Parola giriniz."),
        validators.EqualTo(fieldname="confirm",
                           message="Parolanız uyuşmuyor."),

    ])
    confirm = PasswordField("Parola Doğrula")


class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

class Predictinput(Form):
    recipient_age = StringField("Alıcının Yaşı")
    recipient_gender = StringField("Alıcının Cinsiyeti")
    recipient_body_mass	= StringField("Alıcının Kilosu(KG)")
    recipient_ABO = StringField("Alıcının Kan Grubu")
    recipient_rh = StringField("Alıcının Rh değeri")
    disease = StringField("Alıcının Hastalığı")
    disease_group = StringField("Alıcının Hastalık Grubu")
    donor_age = StringField("Donör Yaşı")
    donor_ABO = StringField("Donör Kan Grubu")


# Boostrap hazır modüller barındıran css kütüphanesi
app = Flask(__name__)
app.secret_key = "organdonation"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "organ"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route('/predict', methods=["GET", "POST"])
    
def predict():
    form = Predictinput(request.form)  # Requesti almak için request.form

    if request.method == "POST" and form.validate():
        
        recipient_age = form.recipient_age.data
        recipient_gender = form.recipient_gender.data
        recipient_body_mass = form.recipient_body_mass.data
        recipient_ABO = form.recipient_ABO.data
        recipient_rh = form.recipient_rh.data
        disease	= form.disease.data
        disease_group = form.disease_group.data
        donor_age = form.donor_age.data
        donor_ABO = form.donor_ABO.data


        cursor = mysql.connection.cursor()

        sorgu = "Insert into users(recipient_age,recipient_gender,recipient_body_mass,recipient_ABO,recipient_rh,disease,disease_group,donor_age,donor_ABO) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        cursor.execute(sorgu, (recipient_age,recipient_gender,recipient_body_mass,recipient_ABO,recipient_rh,disease,disease_group,donor_age,donor_ABO))
        mysql.connection.commit()

        cursor.close()

        flash("Tahmin için parametreler alındı.", "success")

        return redirect(url_for('predict'))
    else:

        return render_template("predict.html", form=form)

    return render_template("predict.html")

     

@app.route('/')
def index():
    return render_template("index.html") 


@app.route('/about')
def about():
    return render_template("about.html")

# Makale Sayfası


@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles"

    result = cursor.execute(sorgu)

    if result > 0:
        articles = cursor.fetchall()
        return render_template("articles.html", articles=articles)
    else:
        return render_template("articles.html")


@app.route('/dashboard')
@login_required
def dashboard():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles where author = %s"

    result = cursor.execute(sorgu, (session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html", articles=articles)
    else:

        return render_template("dashboard.html")




# Register Section


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)  # Requesti almak için request.form

    if request.method == "POST" and form.validate():
        name_surname = form.name_surname.data
        username = form.username.data
        emailaddress = form.emailaddress.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()

        sorgu = "Insert into users(name_surname,emailaddress,username,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu, (name_surname, emailaddress, username, password))
        mysql.connection.commit()

        cursor.close()

        flash("Başarıyla kayıt oldunuz.", "success")

        return redirect(url_for('login'))
    else:

        return render_template("register.html", form=form)

    return render_template("register.html")

# login işlemi


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()

        sorgu = "Select * From users where username = %s"
        results = cursor.execute(sorgu, (username,))

        if results > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered, real_password):
                flash("Başarıyla giriş yaptınız.", "success")

                session["logged_in"] = True
                session["username"] = username

                return redirect(url_for("index"))
            else:
                flash("Parolanızı yanlış girdiniz.", "danger")
        else:
            flash("Böyle bir kullanıcı bulunamadı.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)

#detay

@app.route("/article/<string:id>")
@login_required
def article(id):
    cursor = mysql.connection.cursor()
    
    sorgu = "Select * from articles where id = %s"

    result = cursor.execute(sorgu,(id,))

    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article = article)
    else:
        return render_template("article.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

# makaleekleme


@app.route('/addarticle', methods=["GET", "POST"])
@login_required
def addarticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        

        cursor = mysql.connection.cursor()

        sorgu = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"

        cursor.execute(sorgu, (title, session["username"], content))

        mysql.connection.commit()

        cursor.close()

        flash("Rapor Başarıyla Eklendi", "success")

        return redirect(url_for("dashboard"))

    return render_template("addarticle.html", form=form)

#Makale Silme
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where author = %s and id = %s"

    result = cursor.execute(sorgu,(session["username"],id))

    if result > 0:
        sorgu2 = "Delete from articles where id = %s"

        cursor.execute(sorgu2,(id,))

        mysql.connection.commit()

        return redirect(url_for("dashboard"))
    else:
        flash("Böyle bir rapor yok veya bu işleme yetkiniz yok","danger")
        return redirect(url_for("index"))

#Makale Güncelleme
@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def update(id):
   if request.method == "GET":
       cursor = mysql.connection.cursor()

       sorgu = "Select * from articles where id = %s and author = %s"
       result = cursor.execute(sorgu,(id,session["username"]))

       if result == 0:
           flash("Böyle bir rapor yok veya bu işleme yetkiniz yok","danger")
           return redirect(url_for("index"))
       else:
           article = cursor.fetchone()
           form = ArticleForm()

           form.title.data = article["title"]
           form.content.data = article["content"]
           return render_template("update.html",form = form)

   else:
       # POST REQUEST
       form = ArticleForm(request.form)

       newTitle = form.title.data
       newContent = form.content.data

       sorgu2 = "Update articles Set title = %s,content = %s where id = %s "

       cursor = mysql.connection.cursor()

       cursor.execute(sorgu2,(newTitle,newContent,id))

       mysql.connection.commit()

       flash("Rapor başarıyla güncellendi","success")

       return redirect(url_for("dashboard"))

       pass

# Makaleform


class ArticleForm(Form):
    title = StringField("Rapor Başlığı", validators=[
                        validators.Length(min=5, max=100)])
    content = TextAreaField("Rapor İçeriği", validators=[
                            validators.Length(min=10)])

# Arama URL
@app.route("/search",methods = ["GET","POST"])
def search():
   if request.method == "GET":
       return redirect(url_for("index"))
   else:
       keyword = request.form.get("keyword")

       cursor = mysql.connection.cursor()

       sorgu = "Select * from articles where title like '%" + keyword +"%'"

       result = cursor.execute(sorgu)

       if result == 0:
           flash("Aranan kelime iile uygun rapor bulunamadı.","warning")
           return redirect(url_for("articles"))
       else:
           articles = cursor.fetchall()

           return render_template("articles.html",articles = articles)

if __name__ == "__main__":
    app.run(debug=True)
