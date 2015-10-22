"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from correlation import pearson

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    @classmethod
    def get_user_by_email_password(cls, user_email, user_password):
        
        try:
            user_login_info = cls.query.filter_by(email=user_email, password=user_password).one()
            return user_login_info
        
        except Exception, error:
            print error
    
    @classmethod
    def get_user_by_email(cls, user_email):
        
        try:
            user_login_info = cls.query.filter_by(email=user_email).one()
            return user_login_info
        
        except Exception, error:
            print error

    @classmethod
    def create_user_by_email_password(cls, user_email, user_password):

        user = User(email = user_email, password = user_password)
        print user
        db.session.add(user)
        db.session.commit()

    
    

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)

 
class Movie(db.Model):
    __tablename__ = 'movies'

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Movie movie_id=%s title=%s>" % (self.movie_id, self.title)    

class Rating(db.Model):
    __tablename__ = 'ratings'

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=False)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("ratings", order_by=rating_id))

    # Define relationship to movie
    movie = db.relationship("Movie",
                           backref=db.backref("ratings", order_by=rating_id))

    @classmethod
    def get_rating_by_userid_movieid(cls, user_id, movie_id):

        try:
            user_rating = cls.query.filter_by(user_id=user_id, movie_id = movie_id).one()
            return user_rating
        
        except Exception, error:
            print error

    @classmethod
    def add_new_rating(cls, user_id, movie_id, score):

        new_rating = Rating(user_id = user_id, movie_id = movie_id, score = score)
        print new_rating
        db.session.add(new_rating)
        db.session.commit()

    @classmethod
    def predict_rating(cls, user_id, movie_id):

        m = Movie.query.filter_by(movie_id=movie_id).one()
        u = User.query.get(user_id)

        u_ratings = u.ratings

        other_ratings = Rating.query.filter_by(movie_id=movie_id).all()
        other_users = [r.user for r in other_ratings]
        ratings_pairs = []
        pearson_results = {}

        for otheruser in other_users:
            for rating in otheruser.ratings:
                if rating.movie_id in u_ratings.movie_id:
                    rating_pairs.append((u.rating.score, rating.score))
                pearson_results[otheruser.user_id]= correlation.pearson(rating_pairs)
    
        correlations = pearson_results.values()
        highest_correlation = max(correlations)

        for item in pearson_results.items():
            if item[1] == highest_correlation:
                print item[0]


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Rating movie_id=%s user_id=%s score=%s>" % (self.movie_id, self.user_id, self.score)    


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
