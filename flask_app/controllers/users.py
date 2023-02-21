from flask import render_template, redirect, request, session
from flask_app import app
from flask_app.model.user import User
from flask_bcrypt import Bcrypt
from flask import flash

bcrypt = Bcrypt(app)

@app.route("/")
def root():
    return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    data = {
        "id": session["user_id"]
    }
    user = User.get_user_by_id(data)
    all_users = User.get_all_users()
    friends = User.get_user_friends(data)
    not_friends = User.get_none_friends(data)
    print(friends)
    return render_template("dashboard.html", user = user, all_users = all_users, friends = friends, not_friends = not_friends)

@app.route("/register_user", methods = ["POST"])
def register():
    if not User.validate_registration(request.form):
        return redirect("/login")

    pw_hash = bcrypt.generate_password_hash(request.form["password"])
    data = {
        "name": request.form["name"],
        "alias": request.form["alias"],
        "email": request.form["email"],
        "password": pw_hash,
        "birthday": request.form["birthday"]
    }
    user_id = User.add_user(data)
    session['user_id'] = user_id
    return redirect("/dashboard")

@app.route("/login_user", methods = ["POST"])
def login_user():
    data = {
        "email": request.form["email"]
    }
    user_in_db = User.get_user_by_email(data)
    if not user_in_db:
        flash(u"Invalid Email/Password", "login")
        return redirect("/login")
    if not bcrypt.check_password_hash(user_in_db.password, request.form["password"]):
        flash(u"Invalid Email/Password", "login")
        return redirect("/login")
    session["user_id"] = user_in_db.id
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ------ friendships --------

@app.route("/add_friend/<int:id>")
def add_friend(id):
    data = {
        "user_id": session["user_id"],
        "user2_id": id
    }
    User.add_friend(data)
    return redirect("/dashboard")

#---------- profile -----------

@app.route("/profile/<int:id>")
def show_profile(id):
    if "user_id" not in session:
        return redirect("/login")
    data = {
        "id": id
    }
    user = User.get_user_by_id(data)
    return render_template("profile.html", user = user)

# -------- remove friend ----------

@app.route("/remove/<int:id>")
def remove_friend(id):
    data = {
        "user_id": session["user_id"],
        "user2_id": id
    }
    User.remove_friend(data)
    return redirect("/dashboard")

