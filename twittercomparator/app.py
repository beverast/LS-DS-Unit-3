"""
Main application and routing logic for Twitter-Comparator
"""
import os
from decouple import config
from flask import Flask, render_template, request
from .models import DB, User
from .predict import predict_user
from .twitter import add_or_update_user


def create_app():
    """Create and configure an instance of the Flask application"""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    DB.init_app(app)


    @app.route("/")
    def root():
        users = User.query.all()
        return render_template('base.html',title='Home',users=users)


    @app.route("/user", methods=["POST"])
    @app.route("/user/<name>", methods=["GET"])
    def user(name=None, message=''):
        name = name or request.values["user_name"]
        try:
            if request.method == "POST":
                add_or_update_user(name)
                message = "User {} successfully added!".format(name)
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = "Error adding {}: {}".format(name, e)
            tweets = []
        return render_template("user.html", title=name, tweets=tweets, message=message)


    @app.route("/compare", methods=["POST"])
    def compare(message=''):
        # Consider making a one-liner with list-unpacking
        user1 = request.values['user1']
        user2 = request.values['user2']
        
        if user1 == user2:
            return 'Cannot compare same account!'
        else:
            prediction = predict_user(user1, user2, request.values['tweet_text'])
            return user1 if prediction else user2
    
    return app
