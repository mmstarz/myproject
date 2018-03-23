import os
import re
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, send_from_directory
from passlib.apps import custom_app_context as pwd_context
from flask_session import Session
from flask import abort
from tempfile import mkdtemp
import uuid
import shutil



from helpers import *
import string

from cs50 import SQL
# from helpers import lookup

# Configure application
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
# app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///prj.db")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":

        production=db.execute("SELECT * FROM production")
        updates=db.execute("SELECT * FROM history")

        if not production:
            return render_template("index2.html", updates=updates)

        else:
            return render_template("index.html", production=production, updates=updates)


@app.route("/logged", methods=["GET", "POST"])
@login_required
def logged():

    if request.method == "GET":
        username = db.execute("SELECT username FROM users WHERE id = :id", id=session["user_id"])
        production = db.execute("SELECT * FROM production")
        updates=db.execute("SELECT * FROM history")
        if not production:
            return render_template("logged2.html", username=username[0]["username"], updates=updates)

        else:
            return render_template("logged.html", username=username[0]["username"], production=production, updates=updates)

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "GET":
        return render_template("index.html")

    elif request.method == "POST" and "signupform" and "signupbtn":
        """Register user."""
        # ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email")

        # query database for email
        emails = db.execute("SELECT * FROM users WHERE email = :email",
                            email=request.form.get("email"))

        # ensure email not taken
        if len(emails) != 0:
            return apology("Sorry, this email already taken.")

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # query database for username
        users = db.execute("SELECT * FROM users WHERE username = :username",
                           username=request.form.get("username"))

        # ensure username not taken
        if len(users) != 0:
            return apology("Sorry, this username already taken.")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password doesn't match")

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        generate_password_hash = pwd_context.hash(password)

        # add new user info in sql database
        adduser = db.execute("INSERT INTO users (username, hash, email) VALUES (:username, :hash, :email)",
                             username=username, hash=generate_password_hash, email=email)

        users = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        session["user_id"] = users[0]["id"]
        return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("index.html")

    # if user reached route via POST (as by submitting a form via POST)
    elif request.method == "POST" and "loginform" and "loginbtn":
        """Login user."""

        email2 = request.form.get("email2")
        password2 = request.form.get("password2")

        # ensure email was submitted
        if not request.form.get("email2"):
            return apology("must provide email")

        # ensure password was submitted
        elif not request.form.get("password2"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email2",
                          email2=email2)

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password2"), rows[0]["hash"]):
            return apology("invalid email or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("logged"))

@app.route("/logout")
@login_required
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("index"))

@app.route("/apage")
def apage():
    """admin test page"""

    production=db.execute("SELECT * FROM production")

    if request.method == "GET":
        return render_template("apage.html", production=production)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    username = db.execute("SELECT username FROM users WHERE id = :id", id=session["user_id"])

    if request.method == "GET":
        return render_template("logged.html", username=username[0]["username"])


@app.route("/addcard", methods=["GET", "POST"])
@login_required
def addcard():

    if request.method == "POST":

        productid = request.form.get("productid")
        title = request.form.get("title")
        trademark = request.form.get("trademark")
        model = request.form.get("model")
        year = request.form.get("year")
        mileage = request.form.get("mileage")
        color = request.form.get("color")
        engine = request.form.get("engine")
        size = request.form.get("size")
        doors = request.form.get("doors")
        seats = request.form.get("seats")
        interior = request.form.get("interior")
        advances = request.form.get("advances")
        defects = request.form.get("defects")
        activity = request.form.get("activity")
        status = "new supply"

        db.execute("INSERT INTO production (id, title, trademark, model, year, mileage, color, engine, size, doors, seats, interior, activity, advances, defects) VALUES (:productid, :title, :trademark, :model, :year, :mileage, :color, :engine, :size, :doors, :seats, :interior, :activity, :advances, :defects)",
                   productid=productid, title=title, trademark=trademark, model=model, year=year, mileage=mileage, color=color,
                   engine=engine, size=size, doors=doors, seats=seats, interior=interior, advances=advances, defects=defects, activity=activity)

        db.execute("INSERT INTO history (id, trademark, model, year, status) VALUES (:productid, :tardemark, :model, :year, :status)",
                   productid=productid, tardemark=trademark, model=model, year=year, status=status)

        target=os.path.join(APP_ROOT, "static/images/{}".format(productid))

        if not os.path.isdir(target):
            os.mkdir(target)

        file1 = request.files["file1"]
        image1 = file1.filename
        if image1 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image1])
            file1.save(destination)
            db.execute("UPDATE production SET image1 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image1), productid=productid)

        file2 = request.files["file2"]
        image2 = file2.filename
        if image2 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image2])
            file2.save(destination)
            db.execute("UPDATE production SET image2 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image2), productid=productid)

        file3 = request.files["file3"]
        image3 = file3.filename
        if image3 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image3])
            file3.save(destination)
            db.execute("UPDATE production SET image3 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image3), productid=productid)

        file4 = request.files["file4"]
        image4 = file4.filename
        if image4 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image4])
            file4.save(destination)
            db.execute("UPDATE production SET image4 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image4), productid=productid)

        file5 = request.files["file5"]
        image5 = file5.filename
        if image5 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image5])
            file5.save(destination)
            db.execute("UPDATE production SET image5 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image5), productid=productid)

        file6 = request.files["file6"]
        image6 = file6.filename
        if image6 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image6])
            file6.save(destination)
            db.execute("UPDATE production SET image6 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image6), productid=productid)

        file7 = request.files["file7"]
        image7 = file7.filename
        if image7 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image7])
            file7.save(destination)
            db.execute("UPDATE production SET image7 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image7), productid=productid)

        file8 = request.files["file8"]
        image8 = file8.filename
        if image6 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image8])
            file8.save(destination)
            db.execute("UPDATE production SET image8 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image8), productid=productid)

        file9 = request.files["file9"]
        image9 = file9.filename
        if image6 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image9])
            file9.save(destination)
            db.execute("UPDATE production SET image9 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image9), productid=productid)

        file10 = request.files["file10"]
        image10 = file10.filename
        if image10 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image10])
            file10.save(destination)
            db.execute("UPDATE production SET image10 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image10), productid=productid)

        file11 = request.files["file11"]
        image11 = file11.filename
        if image11 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image11])
            file11.save(destination)
            db.execute("UPDATE production SET image11 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image11), productid=productid)

        file12 = request.files["file12"]
        image12 = file12.filename
        if image12 == '':
            flash('No selected file')
        else:
            destination = "/".join([target, image12])
            file12.save(destination)
            db.execute("UPDATE production SET image12 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image12), productid=productid)

        return redirect(url_for("logged"))

    if request.method == "GET":
        return render_template("logged.html")



@app.route("/editcard", methods=["GET", "POST"])
def editcard():

    if request.method == "POST":

        productid = request.form.get("productid")
        status = "updated"
        db.execute("UPDATE history SET status = :status WHERE id = :productid", status=status, productid=productid)

        if not request.form.get("title"):
            title = db.execute("SELECT title FROM production WHERE id = :productid", productid=productid)
        else:
            title = request.form.get("title")
            db.execute ("UPDATE production SET title = :title WHERE id = :productid", title=title, productid=productid)

        if not request.form.get("trademark"):
            trademark = db.execute("SELECT trademark FROM production WHERE id = :productid", productid=productid)
        else:
            trademark = request.form.get("trademark")
            db.execute ("UPDATE production SET trademark = :trademark WHERE id = :productid", trademark=trademark, productid=productid)
            db.execute ("UPDATE history SET trademark = :trademark WHERE id = :productid", trademark=trademark, productid=productid)

        if not request.form.get("model"):
            model = db.execute("SELECT model FROM production WHERE id = :productid", productid=productid)
        else:
            model = request.form.get("model")
            db.execute ("UPDATE production SET model = :model WHERE id = :productid", model=model, productid=productid)
            db.execute ("UPDATE history SET model = :model WHERE id = :productid", model=model, productid=productid)

        if not request.form.get("year"):
            year = db.execute("SELECT year FROM production WHERE id = :productid", productid=productid)
        else:
            year = request.form.get("year")
            db.execute ("UPDATE production SET year = :year WHERE id = :productid", year=year, productid=productid)
            db.execute ("UPDATE history SET year = :year WHERE id = :productid", year=year, productid=productid)

        if not request.form.get("mileage"):
            mileage = db.execute("SELECT mileage FROM production WHERE id = :productid", productid=productid)
        else:
            mileage = request.form.get("mileage")
            db.execute ("UPDATE production SET mileage = :mileage WHERE id = :productid", mileage=mileage, productid=productid)

        if not request.form.get("color"):
            color = db.execute("SELECT color FROM production WHERE id = :productid", productid=productid)
        else:
            color = request.form.get("color")
            db.execute ("UPDATE production SET color = :color WHERE id = :productid", color=color, productid=productid)

        if not request.form.get("engine"):
            engine = db.execute("SELECT engine FROM production WHERE id = :productid", productid=productid)
        else:
            engine = request.form.get("engine")
            db.execute ("UPDATE production SET engine = :engine WHERE id = :productid", engine=engine, productid=productid)

        if not request.form.get("size"):
            size = db.execute("SELECT size FROM production WHERE id = :productid", productid=productid)
        else:
            size = request.form.get("size")
            db.execute ("UPDATE production SET size = :size WHERE id = :productid", size=size, productid=productid)

        if not request.form.get("doors"):
            doors = db.execute("SELECT doors FROM production WHERE id = :productid", productid=productid)
        else:
            doors = request.form.get("doors")
            db.execute ("UPDATE production SET doors = :doors WHERE id = :productid", doors=doors, productid=productid)

        if not request.form.get("seats"):
            seats = db.execute("SELECT seats FROM production WHERE id = :productid", productid=productid)
        else:
            seats = request.form.get("seats")
            db.execute ("UPDATE production SET seats = :seats WHERE id = :productid", seats=seats, productid=productid)

        if not request.form.get("interior"):
            interior = db.execute("SELECT interior FROM production WHERE id = :productid", productid=productid)
        else:
            interior = request.form.get("interior")
            db.execute ("UPDATE production SET interior = :interior WHERE id = :productid", interior=interior, productid=productid)

        if not request.form.get("advances"):
            advances = db.execute("SELECT advances FROM production WHERE id = :productid", productid=productid)
        else:
            advances = request.form.get("advances")
            db.execute ("UPDATE production SET advances = :advances WHERE id = :productid", advances=advances, productid=productid)

        if not request.form.get("defects"):
            defects = db.execute("SELECT defects FROM production WHERE id = :productid", productid=productid)
        else:
            defects = request.form.get("defects")
            db.execute ("UPDATE production SET defects = :defects WHERE id = :productid", defects=defects, productid=productid)

        if not request.form.get("activity"):
            activity = db.execute("SELECT activity FROM production WHERE id = :productid", productid=productid)
        else:
            activity = request.form.get("activity")
            db.execute("UPDATE production SET activity = :activity WHERE id = :productid", activity=activity, productid=productid)

        target=os.path.join(APP_ROOT, "static/images/{}".format(productid))

        if not os.path.isdir(target):
            os.mkdir(target)

        file1 = request.files["file1"]
        image1 = file1.filename
        if image1 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image1)):
                os.remove("static/images/{}/{}".format(productid, image1))

            destination = "/".join([target, image1])
            file1.save(destination)
            db.execute("UPDATE production SET image1 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image1), productid=productid)

        file2 = request.files["file2"]
        image2 = file2.filename
        if image2 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image2)):
                os.remove("static/images/{}/{}".format(productid, image2))

            destination = "/".join([target, image2])
            file2.save(destination)
            db.execute("UPDATE production SET image2 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image2), productid=productid)

        file3 = request.files["file3"]
        image3 = file3.filename
        if image3 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image3)):
                os.remove("static/images/{}/{}".format(productid, image3))

            destination = "/".join([target, image3])
            file3.save(destination)
            db.execute("UPDATE production SET image3 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image3), productid=productid)

        file4 = request.files["file4"]
        image4 = file4.filename
        if image4 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image4)):
                os.remove("static/images/{}/{}".format(productid, image4))

            destination = "/".join([target, image4])
            file4.save(destination)
            db.execute("UPDATE production SET image4 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image4), productid=productid)

        file5 = request.files["file5"]
        image5 = file5.filename
        if image5 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image5)):
                os.remove("static/images/{}/{}".format(productid, image5))

            destination = "/".join([target, image5])
            file5.save(destination)
            db.execute("UPDATE production SET image5 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image5), productid=productid)

        file6 = request.files["file6"]
        image6 = file6.filename
        if image6 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image6)):
                os.remove("static/images/{}/{}".format(productid, image6))

            destination = "/".join([target, image6])
            file6.save(destination)
            db.execute("UPDATE production SET image6 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image6), productid=productid)

        file7 = request.files["file7"]
        image7 = file7.filename
        if image7 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image7)):
                os.remove("static/images/{}/{}".format(productid, image7))

            destination = "/".join([target, image7])
            file7.save(destination)
            db.execute("UPDATE production SET image7 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image7), productid=productid)

        file8 = request.files["file8"]
        image8 = file8.filename
        if image8 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image8)):
                os.remove("static/images/{}/{}".format(productid, image8))

            destination = "/".join([target, image8])
            file8.save(destination)
            db.execute("UPDATE production SET image8 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image8), productid=productid)

        file9 = request.files["file9"]
        image9 = file9.filename
        if image9 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image9)):
                os.remove("static/images/{}/{}".format(productid, image9))

            destination = "/".join([target, image9])
            file9.save(destination)
            db.execute("UPDATE production SET image9 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image9), productid=productid)

        file10 = request.files["file10"]
        image10 = file10.filename
        if image10 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image10)):
                os.remove("static/images/{}/{}".format(productid, image10))

            destination = "/".join([target, image10])
            file10.save(destination)
            db.execute("UPDATE production SET image10 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image10), productid=productid)

        file11 = request.files["file11"]
        image11 = file11.filename
        if image11 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image11)):
                os.remove("static/images/{}/{}".format(productid, image11))

            destination = "/".join([target, image11])
            file11.save(destination)
            db.execute("UPDATE production SET image11 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image11), productid=productid)

        file12 = request.files["file12"]
        image12 = file12.filename
        if image12 == '':
            flash('No selected file')
        else:

            if os.path.isfile("static/images/{}/{}".format(productid, image12)):
                os.remove("static/images/{}/{}".format(productid, image12))

            destination = "/".join([target, image12])
            file12.save(destination)
            db.execute("UPDATE production SET image12 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image12), productid=productid)


        return redirect(url_for("logged"))

    if request.method == "GET":

        username = db.execute("SELECT username FROM users WHERE id = :id", id=session["user_id"])
        production = db.execute("SELECT * FROM production")
        productid = request.args.get("productid")
        select = db.execute("SELECT * FROM production WHERE id = :productid", productid=productid)
        updates = db.execute("SELECT * FROM history")

        return render_template("logged3.html", select=select, username=username[0]["username"], production=production, updates=updates)



@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():

    if request.method == "POST" and "removecard":

        productid = request.form.get("productid")
        shutil.rmtree("static/images/{}".format(productid))
        db.execute("DELETE FROM production WHERE id = :productid", productid=productid)
        status = "sold"
        db.execute("UPDATE history SET status = :status WHERE id = :productid", status=status, productid=productid)

        return redirect(url_for("logged"))

    if request.method == "GET":

        return render_template("logged.html")

@app.route("/select", methods=["GET", "POST"])
@login_required
def select():

    if request.method == "POST" and "selectcard":

        productid = request.form.get("productid")

        return redirect(url_for("editcard", productid=productid))

    if request.method == "GET":

        return render_template("logged.html")


@app.errorhandler(404)
def page_not_found(e):
    return pagenotfound("Page not found")
