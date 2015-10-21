"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/users/<int:userid>")
def get_user_info(userid):
    """Show user info"""

    user = User.query.filter_by(user_id=userid).one()
    
    return render_template("user_info.html", user= user)

@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)

@app.route("/movies/<int:movieid>")
def get_movie_info(movieid):
    """Show movie info"""

    movie = Movie.query.filter_by(movie_id=movieid).one()
    
    return render_template("movie_info.html", movie= movie)
    

@app.route("/register")
def register_user():

    return render_template("signup_form.html")

@app.route("/register-confirm", methods=["POST"])
def confirm_new_user():
    """Create new user"""
    user_email = request.form.get("email")
    user_password = request.form.get("password")    
    
    confirmed_user = User.get_user_by_email(user_email)
    
    if not confirmed_user:
        User.create_user_by_email_password(user_email, user_password)
        flash("You successfully created an account!")
    else:
        flash("You already have an account")

    return redirect("/")

@app.route("/login")
def login_user():

    return render_template("login_form.html")

@app.route('/login_confirm', methods=["POST"])
def get_login():
    """Get user info"""
    user_email = request.form.get("email")
    user_password = request.form.get("password")
    
    confirmed_user = User.get_user_by_email_password(user_email, user_password)
    
    if confirmed_user:
        flash("You're logged in!")
        userid = confirmed_user.user_id
        session["User"] = userid
        print session["User"]
        return redirect("/users/%d" % userid)
    else:
        flash("Your email and password combination are not correct.")
        return redirect("/login")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()