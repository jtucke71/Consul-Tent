from database import db
import datetime # something for time of day

class Content(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(100))
    date = db.Column("date", db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    username = db.Column("username", db.String(100))
    comments = db.relationship("Comment", backref="note", cascade="all, delete-orphan", lazy=True)
    upv = db.Column(db.Integer)
    dnv = db.Column(db.Integer)
    topic = db.Column("topic", db.String(100))

    def __init__(self, title, text, date, user_id, username, upv, dnv, topic):
        self.title = title
        self.text = text
        self.date = date
        self.user_id = user_id
        self.username = username
        self.upv = upv
        self.dnv = dnv
        self.topic = topic

class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    username = db.Column("username", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    notes = db.relationship("Content", backref="user", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)
    recentvote = db.Column(db.Integer)

    def __init__(self, first_name, last_name, username, email, password, recentvote):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = password
        self.recentvote = recentvote
        self.registered_on = datetime.date.today()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.VARCHAR, nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    username = db.Column("username", db.String(100))

    def __init__(self, content, content_id, user_id, username):
        self.date_posted = datetime.date.today()
        self.content = content
        self.content_id = content_id
        self.user_id = user_id
        self.username = username

class Vote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    user = db.relationship("User", backref=db.backref("votes", cascade="all, delete-orphan"))
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), primary_key=True)
    content = db.relationship("Content", backref=db.backref("votes", cascade="all, delete-orphan"))
    upvotes = db.Column(db.Integer)
    downvotes = db.Column(db.Integer)

    def __init__(self, user_id, content_id, upvotes, downvotes):
        self.user_id = user_id
        self.content_id = content_id
        self.upvotes = upvotes
        self.downvotes = downvotes

class Favorite(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    user = db.relationship("User", backref=db.backref("favorites", lazy=True))
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), primary_key=True)
    content = db.relationship("Content", backref=db.backref("favorites", lazy=True))
    title = db.Column("title", db.String(200))
    date = db.Column("date", db.String(50))
    username = db.Column("username", db.String(100))

    def __init__(self, title, date, username, user_id, content_id):
        self.title = title
        self.date = date
        self.username = username
        self.user_id = user_id
        self.content_id = content_id
