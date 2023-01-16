import os
import html

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helper import apology, login_required

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

os.chdir("./")
db = SQL("sqlite:///inspirer.db")

app.config['MAX_CONTENT_LENGTH'] =  10 * 1024 * 1024
app.config["MAX_IMAGE_FILESIZE"] = 10 * 1024 * 1024

registrants = os.path.join('static', 'registrants')
app.config['UPLOAD_FOLDER'] = registrants

event_images = os.path.join('static','events')

@app.route("/")
def home():

    featured_speaker = db.execute("SELECT * FROM info LIMIT 4")

    for i in featured_speaker:
        im = i["firstname"] + ".jpg"
        image = os.path.join(app.config['UPLOAD_FOLDER'], im)
        i["image"] = image

    if session.get("user_id") is None:
        return render_template ("index.html", featured_speaker = featured_speaker )

    else:

        user_id = session["user_id"]
        users = db.execute("SELECT * FROM info JOIN users on info.email = users.email WHERE id = :user_id", user_id = user_id)[0]
        return render_template("index.html", featured_speaker = featured_speaker, users = users)

@app.route("/speaker", methods=["GET","post"])
def speaker():
    if request.method =="GET":

        rows = db.execute("select * from info")

        for i in rows:
            im = i["firstname"] + ".jpg"
            image = os.path.join(app.config['UPLOAD_FOLDER'], im)
            i["image"] = image

        if session.get("user_id") is None:

            return render_template("speaker.html", rows = rows)

        else:

            user_id = session["user_id"]
            users = db.execute("SELECT * FROM info JOIN users on info.email = users.email WHERE id = :user_id", user_id = user_id)[0]

            return render_template("speaker.html", rows = rows, users = users)

    else:

        topic = request.form.get("topic")
        a = '%' + topic + '%'
        rows = db.execute("select * from info where topic like :topic", topic = a)

        for i in rows:
            im = i["firstname"] + ".jpg"
            image = os.path.join(app.config['UPLOAD_FOLDER'], im)
            i["image"] = image


        if session.get("user_id") is None:

            return render_template("speaker.html", rows = rows)

        else:

            user_id = session["user_id"]
            users = db.execute("SELECT * FROM info JOIN users on info.email = users.email WHERE id = :user_id", user_id = user_id)[0]

            return render_template("speaker.html", rows = rows, users = users)

@app.route("/event")
def event():
    rows = db.execute("select * from events")

    for i in rows:
        im = i["event"] + ".jpg"
        # image = os.path.join(event_images, im)
        i["image"] = "./static/events/" + im

    if session.get("user_id") is None:

        return render_template("event.html", rows = rows)

    else:
        user_id = session["user_id"]
        users = db.execute("SELECT * FROM info JOIN users on info.email = users.email WHERE id = :user_id", user_id = user_id)[0]
        return render_template("event.html", rows = rows, users = users)

@app.route("/event/add", methods=["GET", "POST"])
def event2():

    if request.method == "GET":

        if session.get("user_id") is None: #you are not logging in
            return render_template("event2.html")

        else:
            user_id = session["user_id"]
            users = db.execute("SELECT * FROM info JOIN users on info.email = users.email WHERE id = :user_id", user_id = user_id)[0]

            return render_template("event2.html", users = users)

    else:
        
        event = request.form.get("event")
        category = request.form.get("category")
        date = request.form.get("date")
        month = request.form.get("month")
        year = request.form.get("year")
        region = request.form.get("region")
        country = request.form.get("country")
        city = request.form.get("city")
        size = request.form.get("size")
        intro = request.form.get("intro")
        speaker = session["user_id"]
        db.execute("insert into events (speaker, event, category, date, month, year, region, country, city, size, intro) values (:speaker, :event, :category, :date, :month, :year, :region, :country, :city, :size, :intro)", speaker = speaker, event=event, category=category, date=date, month=month, year=year, region=region, country=country, city=city, size=size, intro=intro)
        
        return redirect("/event")

@app.route("/event/<name>")
def name(name):
    
    user_id = session["user_id"]
    users = db.execute("SELECT * FROM info WHERE user_id = :user_id", user_id = user_id)[0]

    name = name.replace("%20", " ")
    event = db.execute("SELECT * FROM events WHERE event = :name", name = name)[0]
    speaker = db.execute("select firstname, lastname from info join events on events.speaker = info.user_id")[0]

    im = event["event"] + ".jpg"
    event["images"] = "../static/events/" + im

    return render_template("eventpage.html", event = event, speaker=speaker, users=users)

@app.route("/guide", methods = ["GET", "POST"])
def guide():

    if request.method == "POST":
        return apology("todo", 403)

    else:

        if session.get("user_id") is None:
            return render_template ("comingsoon.html" )

        else:

            user_id = session["user_id"]
            users = db.execute("SELECT * FROM info JOIN users on info.email = users.email WHERE id = :user_id", user_id = user_id)[0]

            return render_template("comingsoon.html", users = users)

@app.route("/blog", methods = ["GET", "POST"])
def blog():

    if request.method == "POST":
        return apology("todo", 403)

    else:

        if session.get("user_id") is None:
            return render_template ("comingsoon.html" )

        else:

            user_id = session["user_id"]
            users = db.execute("SELECT * FROM info JOIN users on info.email = users.email WHERE id = :user_id", user_id = user_id)[0]

            return render_template("comingsoon.html", users = users)

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        if not request.form.get("email"):
            return apology("must provide email", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE email = :email",email=request.form.get("email"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hashcode"], request.form.get("password")):
            return apology("invalid email and/or password", 403)

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:

        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        hashcode = generate_password_hash(request.form.get("password"))

        # Ensure username was submitted
        if not email:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        elif not confirmation:
            return apology("must reenter password", 403)

        elif not firstname:
            return apology("must provide first name", 403)

        elif not lastname:
            return apology("must provide last name", 403)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        else:
            # Query database for username

            rows = db.execute("SELECT * FROM users WHERE email = :email", email=email)
            check = db.execute("SELECT * FROM info WHERE firstname = :firstname", firstname = firstname)

            if len(rows) == 1:
                return apology("email already exists", 403)

            if len(check) == 1:
                return apology("you have already registered", 403)

            else:

                register = db.execute("INSERT INTO users (email, hashcode) VALUES (:email, :hashcode)", email = email, hashcode = hashcode)
                session["user_id"] = register

                user_id = session["user_id"]
                db.execute("INSERT INTO info (firstname, lastname, email, user_id) VALUES (:firstname, :lastname, :email, :user_id)", firstname = firstname, lastname = lastname, email=email, user_id = user_id)

                # Redirect user to home page
                return redirect("/")

    else:

        return render_template("register.html")


@app.route("/profile/<name>")
def profile(name):

    users = db.execute("SELECT * FROM info WHERE firstname = :name", name = name)[0]
    im = users["firstname"] + ".jpg"
    image = os.path.join(app.config['UPLOAD_FOLDER'], im)
    users["images"] = "../" + image

    return render_template("profile.html", users = users)


@app.route("/profile/edit/personal_info", methods = ["GET", "POST"])
@login_required
def edit_profile_1():

    if request.method == "POST":

        user_id = session["user_id"]

        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        country = request.form.get("country")
        city = request.form.get("city")

        if not firstname:
            return apology("please provide first name", 403)

        elif not lastname:
            return apology("please provide last name", 403)

        elif not country:
            return apology("please provide country", 403)

        elif not city:
            return apology("please provide city", 403)

        else:

            db.execute("UPDATE info SET firstname = :firstname, lastname = :lastname, country = :country, city = :city WHERE user_id = :user_id", firstname = firstname, lastname = lastname, country = country, city = city, user_id = user_id)

            return redirect("/profile/edit/expertise")

    else:

        user_id = session["user_id"]

        info = db.execute("SELECT * FROM info JOIN users on info.email = users.email WHERE user_id = :user_id", user_id = user_id)[0]

        return render_template("edit_profile_1.html" , users = info)

@app.route("/profile/edit/expertise", methods = ["GET", "POST"])
@login_required
def edit_profile_2():

    if request.method == "POST":

        user_id = session["user_id"]
        topic = request.form.get("topic")
        expertise = request.form.get("expertise")
        school = request.form.get("school")
        grade = request.form.get("grade")
        field = request.form.get("field")
        position = request.form.get("position")
        company = request.form.get("company")
        language = request.form.get("language")

        db.execute("UPDATE info SET topic = :topic, school = :school, grade = :grade, field = :field, position = :position, company = :company, language = :language, expertise = :expertise \
        WHERE user_id = :user_id", topic = topic, school = school, grade = grade, field = field, position = position, company = company, language = language, expertise = expertise, user_id = user_id)

        return redirect("/profile/edit/privacy")

    if request.method == "GET":

        user_id = session["user_id"]
        info = db.execute("SELECT * FROM info JOIN users on info.email = users.email WHERE id = :user_id", user_id = user_id)[0]

        return render_template("edit_profile_2.html", users = info)

@app.route("/profile/edit/privacy", methods = ["GET", "POST"])
@login_required
def edit_profile_3():

    if request.method == "POST":

        return redirect("/profile")

    if request.method == "GET":

        user_id = session["user_id"]
        info = db.execute("SELECT * FROM info JOIN users on info.email = users.email WHERE id = :user_id", user_id = user_id)[0]

        return render_template("edit_profile_3.html", users = info)

@app.route("/subscribe", methods=["GET", "POST"])
def subscribe():

    if request.method == "POST":

        email=request.form.get("email")
        name = request.form.get("name")

        if not request.form.get("email"):
            return apology("must provide email", 403)

        elif not request.form.get("name"):
            return apology("must provide name", 403)

        rows = db.execute("SELECT * FROM subscribe WHERE email = :email", email=email)
        if len(rows) == 1:
            return apology("Your email already subscribed!", 403)

        else:
            db.execute("INSERT INTO subscribe (name, email) VALUES (:name, :email)", name = name, email=email)

        return redirect("/")

    else:

        return redirect("/")

@app.route('/upload', methods = ['POST'])
def upload():

   file = request.files['image']

   user_id = session["user_id"]
   info = db.execute("SELECT * FROM info WHERE user_id = :user_id", user_id = user_id)[0]

   file.filename = info["firstname"] + ".jpg"
   file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

   redirected = "/profile/edit/personal_info"

   flash("Image uploaded!")

   return redirect(redirected)

@app.route('/upload_event', methods = ['POST'])
def upload_event():

   file = request.files['image']

   user_id = session["user_id"]
   event = db.execute("SELECT * FROM events WHERE speaker = :user_id", user_id = user_id)[0]

   file.filename = event["event"] + ".jpg"
   file.save(os.path.join(event_images, file.filename))

   redirected = "/event/add"

   flash("Image uploaded!")

   return redirect("/event/add")

