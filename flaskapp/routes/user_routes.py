from flask import request, render_template, redirect, session

from flaskapp.shared_variables import *
from flaskapp.routes import routes_module
from flaskapp.routes.process import *


# Login page
@routes_module.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        form_data = request.form
        if valid_login(form_data["user_name"], form_data["user_pass"]):
            session["user_name"] = form_data["user_name"]
            return redirect("/")
        else:
            return render_template("error.html", message="Invalid user")


# Sign Up page
@routes_module.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        form_data = request.form
        user_name = form_data["user_name"]
        user_pass = form_data["user_pass"]
        confirm_user_pass = form_data["confirm_user_pass"]
        if(user_pass != confirm_user_pass):
            return render_template("error.html",
                                   message="Passwords do not match")
        if user_name and user_pass:
            res = create_user(user_name, user_pass)
            if(res == "Success"):
                session["user_name"] = user_name
                return redirect("/")
            else:
                return render_template("error.html", message=res)
        else:
            return render_template("error.html",
                                   message="All the fields are necessary")


# Logout page
@routes_module.route("/logout", methods=["GET"])
def logout_page():
    if request.method == "GET":
        session.pop("user_name", None)
        return redirect("/")
