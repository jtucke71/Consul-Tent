######################################################################################################
# imports

import os
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for
from database import db
from models import Content as Content, Favorite
from models import User as User
import bcrypt
from flask import session
from models import Comment as Comment
from forms import RegisterForm, LoginForm, CommentForm, VoteForm, FilterForm, FavoriteForm, UnfavoriteForm, TopicForm
from models import Vote as Vote
from sqlalchemy import exc

app = Flask(__name__)     # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tent_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SECRET_KEY'] = 'SE3155'

#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)
# Setup models
with app.app_context():
    db.create_all()   # run under the app context

######################################################################################################
# Jake's backend stuff

# display signed in user profile page
@app.route('/account')
def account():
    if session.get('user'):
        my_contents = db.session.query(Content).filter_by(user_id=session['user_id']).all() # shows only the signed in user's posts
        user_favorites = db.session.query(Favorite).filter_by(user_id=session['user_id']).all()
        unfavorite_form = UnfavoriteForm()
        bool2 = True
        if len(user_favorites) == 0:
            bool2 = False
        return render_template('account.html', contents=my_contents, favorites=user_favorites, usrn=session['username'], user=session['user'], uid=session['user_id'], formu=unfavorite_form, bool2=bool2)
    else:
        return redirect(url_for('login'))

# display specific user profile page
@app.route('/user/<user_id>')
def user(user_id):
    if session.get('user'):
        uname = db.session.query(User).filter_by(id=user_id).one()
        # shows only the selected user's posts
        my_contents = db.session.query(Content).filter_by(user_id=user_id).all()
        filter_form = FilterForm()
        return render_template('targetuser.html', u=uname.id, contents=my_contents, usrn=session['username'], user=uname.username, formf=filter_form)
    else:
        return redirect(url_for('login'))

# default page
@app.route('/', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            session['username'] = the_user.username
            # render view
            return redirect(url_for('home'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)

# display home page
@app.route('/home', methods=['GET', 'POST'])
def home():
    if session.get('user'):
        my_contents = db.session.query(Content).order_by(Content.id.desc()).all()
        filter_form = FilterForm()
        topic_form = TopicForm()
        return render_template('home.html', contents=my_contents, usrn=session['username'], user=session['user'], formf=filter_form, formt=topic_form)
    else:
        return redirect(url_for('login'))

# gets specific post
@app.route('/home/<content_id>', methods=['GET', 'POST'])
def content(content_id):
    if session.get('user'):
        my_content = db.session.query(Content).filter_by(id=content_id).one()
        esrn = my_content.username
        my_vote = db.session.query(Vote).filter_by(content_id=content_id).first()
        form = CommentForm()
        formv = VoteForm()
        formf = FavoriteForm()
        return render_template('content.html', content=my_content, esrn=esrn, usrn=session['username'], user=session['user'], form=form, formv=formv, formf=formf, votes=my_vote, responder=session['username'])
    else:
        return redirect(url_for('login'))

# makes post and adds to database
@app.route('/home/new', methods=['GET', 'POST'])
def newpost():
    if session.get('user'):
        if request.method == 'POST':
            title = request.form['title']
            text = request.form['content']
            topic = request.form['genres']
            from datetime import datetime
            today = datetime.today()
            today = today.strftime("[%H:%M] ~ %m-%d-%Y")
            new_record = Content(title, text, today, session['user_id'], session['username'], 0, 0, topic)
            db.session.add(new_record)
            db.session.commit()

            return redirect(url_for('home'))
        else:
            return render_template('newpost.html', usrn=session['username'], user=session['user'])
    else:
        return render_template(url_for('login'))

# update post
@app.route('/home/edit/<content_id>', methods=['GET', 'POST'])
def update_content(content_id):
    if session.get('user'):
        if request.method == 'POST':
            # get title data
            title = request.form['title']
            # get note data
            text = request.form['content']
            # get topic data
            topic = request.form['genres']

            content = db.session.query(Content).filter_by(id=content_id).one()
            if content.username == session['username']:
                # update note data
                content.title = title
                content.text = text
                # update note in DB
                content.topic = topic
                db.session.add(content)
                db.session.commit()

                return redirect(url_for('home'))
            # not your post
            else:
                return redirect(url_for('content', content_id=content_id))
        else:
           # retrieve note
            my_content = db.session.query(Content).filter_by(id=content_id).one()

            return render_template('newpost.html', content=my_content, user=session['user'])
    else:
        return render_template(url_for('login'))
# delete post
@app.route('/home/delete/<content_id>', methods=['POST'])
def delete_content(content_id):
    if session.get('user'):
        # get from DB
        my_content = db.session.query(Content).filter_by(id=content_id).one()
        if my_content.username == session['username']:
            db.session.delete(my_content)
            db.session.commit()

            return redirect(url_for('home'))
        # not your post
        else:
            return redirect(url_for('content', content_id=content_id))
    else:
        return render_template(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        username = request.form['username']
        # create user model
        new_user = User(first_name, last_name, username, request.form['email'], h_password, -1)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        session['username'] = username
        # show user dashboard view
        return redirect(url_for('home'))

    # something went wrong - display register view
    return render_template('register.html', form=form)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()

    return redirect(url_for('login'))

@app.route('/home/<content_id>/reply', methods=['POST', 'GET'])
def reply(content_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int (content_id), session['user_id'], session['username'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('content', content_id=content_id))

    else:
        return redirect(url_for('login'))

@app.route("/home/<content_id>/vote", methods=['POST', 'GET'])
def vote(content_id):
    if session.get('user'):
        # fetch current post and store a vote based on its initial upvotes and downvotes
        voted = False
        cv = db.session.query(Content).filter_by(id=content_id).one()
        cu = db.session.query(User).filter_by(id=session['user_id']).one()
        vote = Vote(user_id=session['user_id'], content_id=cv.id, upvotes=cv.upv, downvotes=cv.dnv)
        try:
            db.session.add(vote)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            voted = True
        # call form
        vote_form = VoteForm()
        if vote_form.validate_on_submit():
            # if the user hasn't voted
            if not voted:
                # if the user selects downvote, fetch the prior created vote and update the value of downvotes
                if request.form['vote']=='downvote':
                    c = db.session.query(Vote).filter_by(content_id=content_id).first()
                    newDcount = c.downvotes + 1
                    c.downvotes = newDcount
                    cv.dnv = newDcount
                    cu.recentvote = 0
                    db.session.add(cu)
                    db.session.add(c)
                    db.session.add(cv)
                    db.session.commit()
                # if the user selects upvote, fetch the prior created vote and update the value of upvotes
                if request.form['vote']=='upvote':
                    c = db.session.query(Vote).filter_by(content_id=content_id).first()
                    newUcount = c.upvotes + 1
                    c.upvotes = newUcount
                    cv.upv = newUcount
                    cu.recentvote = 1
                    db.session.add(cu)
                    db.session.add(c)
                    db.session.add(cv)
                    db.session.commit()
            # if the user has voted
            if voted:
                # switches vote from upvote to downvote
                if request.form['vote']=='downvote' and cu.recentvote == 1:
                    c = db.session.query(Vote).filter_by(content_id=content_id).first()
                    newDcount2 = c.downvotes + 1
                    newUcount2 = c.upvotes - 1
                    c.downvotes = newDcount2
                    c.upvotes = newUcount2
                    cv.dnv = newDcount2
                    cv.upv = newUcount2
                    cu.recentvote = 0
                    db.session.add(cu)
                    db.session.add(c)
                    db.session.add(cv)
                    db.session.commit()
                # switches vote from downvote to upvote
                if request.form['vote']=='upvote' and cu.recentvote == 0:
                    c = db.session.query(Vote).filter_by(content_id=content_id).first()
                    newUcount2 = c.upvotes + 1
                    newDcount2 = c.downvotes - 1
                    c.upvotes = newUcount2
                    c.downvotes = newDcount2
                    cv.upv = newUcount2
                    cv.dnv = newDcount2
                    cu.recentvote = 1
                    db.session.add(cu)
                    db.session.add(c)
                    db.session.add(cv)
                    db.session.commit()

        return redirect(url_for('content', content_id=content_id))
    else:
        return redirect(url_for('login'))

@app.route('/home/sort', methods=['GET', 'POST'])
def sort():
    if session.get('user'):
        filter_form = FilterForm()
        topic_form = TopicForm()
        if filter_form.validate_on_submit():
            # most upvotes first
            if request.form['attribute'] == 'Best':
                my_contents = db.session.query(Content).order_by(Content.upv.desc()).all()
            # most downvotes first
            if request.form['attribute'] == 'Worst':
                my_contents = db.session.query(Content).order_by(Content.dnv.desc()).all()
            # most recent first
            if request.form['attribute'] == 'New':
                my_contents = db.session.query(Content).order_by(Content.id.desc()).all()
            # Oldest first
            if request.form['attribute'] == 'Old':
                my_contents = db.session.query(Content).all()

            return render_template('home.html', contents=my_contents, user=session['user'], formf=filter_form, formt=topic_form)
    else:
        return redirect(url_for('login'))

@app.route('/user/<user_id>/sort', methods=['GET', 'POST'])
def sort2(user_id):
    if session.get('user'):
        filter_form = FilterForm()
        if filter_form.validate_on_submit():
            un = db.session.query(User).filter_by(id=user_id).one()
            # most upvotes first
            if request.form['attribute'] == 'Best':
                my_contents = db.session.query(Content).filter_by(user_id=user_id).order_by(Content.upv.desc()).all()
            # most downvotes first
            if request.form['attribute'] == 'Worst':
                my_contents = db.session.query(Content).filter_by(user_id=user_id).order_by(Content.dnv.desc()).all()
           # most recent first
            if request.form['attribute'] == 'New':
                my_contents = db.session.query(Content).order_by(Content.id.desc()).all()
            # Oldest first
            if request.form['attribute'] == 'Old':
                my_contents = db.session.query(Content).all()

            return render_template('targetuser.html', contents=my_contents, user=un.username, formf=filter_form, u=user_id)
    else:
        return redirect(url_for('login'))

@app.route('/home/topic/sort/<top2>', methods=['GET', 'POST'])
def sort3(top2):
    if session.get('user'):
        filter_form = FilterForm()
        topic_form = TopicForm()
        if filter_form.validate_on_submit():
            # most upvotes first
            if request.form['attribute'] == 'Best':
                my_contents = db.session.query(Content).filter_by(topic=top2).order_by(Content.upv.desc()).all()
            # most downvotes first
            if request.form['attribute'] == 'Worst':
                my_contents = db.session.query(Content).filter_by(topic=top2).order_by(Content.dnv.desc()).all()
           # most recent first
            if request.form['attribute'] == 'New':
                my_contents = db.session.query(Content).order_by(Content.id.desc()).all()
            # Oldest first
            if request.form['attribute'] == 'Old':
                my_contents = db.session.query(Content).all()

            return render_template('home.html', contents=my_contents, user=session['user'], formf=filter_form, formt=topic_form)
    else:
        return redirect(url_for('login'))

@app.route('/home/<content_id>/favorite', methods=['GET', 'POST'])
def favorite(content_id):
    if session.get('user'):
        favorite_form = FavoriteForm()
        if favorite_form.validate_on_submit():
            c = db.session.query(Content).filter_by(id=content_id).one()
            # add post to favorites
            f = Favorite(c.title, c.date, c.username, session['user_id'], content_id)
            # add favorite to database and commit
            try:
                db.session.add(f)
                db.session.commit()
            except exc.IntegrityError:
                bool3 = False
                db.session.rollback()

            return redirect(url_for('content', content_id=content_id))
    else:
        return redirect(url_for('login'))

@app.route('/home/<content_id>/unfavorite', methods=['GET', 'POST'])
def unfavorite(content_id):
    if session.get('user'):
        unfavorite_form = UnfavoriteForm()
        if unfavorite_form.validate_on_submit():
            uf = db.session.query(Favorite).filter_by(content_id=content_id).filter_by(user_id=session['user_id']).one()
            # remove post from database and commit
            try:
                db.session.delete(uf)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()

            return redirect(url_for('account'))
    else:
        return redirect(url_for('login'))

@app.route('/home/topic/', methods=['GET', 'POST'])
def topic():
    if session.get('user'):
        topic_form = TopicForm()
        filter_form = FilterForm()
        if topic_form.validate_on_submit():
            top1 = request.form['genre']
            if request.form['genre'] != "All":
                cond = True
            if request.form['genre'] == "All":
                cond = False
            # most upvotes first
            if request.form['genre'] == 'All':
                my_contents = db.session.query(Content).all()
            # most upvotes first
            if request.form['genre'] == 'General':
                my_contents = db.session.query(Content).filter_by(topic='General').all()
            # most upvotes first
            if request.form['genre'] == 'Computers':
                my_contents = db.session.query(Content).filter_by(topic='Computers').all()
                # most upvotes first
            if request.form['genre'] == 'Math':
                my_contents = db.session.query(Content).filter_by(topic='Math').all()
                # most upvotes first
            if request.form['genre'] == 'Science':
                my_contents = db.session.query(Content).filter_by(topic='Science').all()
                # most upvotes first
            if request.form['genre'] == 'Nature':
                my_contents = db.session.query(Content).filter_by(topic='Nature').all()
                # most upvotes first
            if request.form['genre'] == 'Entertainment':
                my_contents = db.session.query(Content).filter_by(topic='Entertainment').all()
                # most upvotes first
            if request.form['genre'] == 'Gaming':
                my_contents = db.session.query(Content).filter_by(topic='Gaming').all()
                # most upvotes first
            if request.form['genre'] == 'School':
                my_contents = db.session.query(Content).filter_by(topic='School').all()
                # most upvotes first
            if request.form['genre'] == 'Art':
                my_contents = db.session.query(Content).filter_by(topic='Art').all()
                # most upvotes first
            if request.form['genre'] == 'Music':
                my_contents = db.session.query(Content).filter_by(topic='Music').all()
                # most upvotes first
            if request.form['genre'] == 'Work':
                my_contents = db.session.query(Content).filter_by(topic='Work').all()
                # most upvotes first
            if request.form['genre'] == 'Sports':
                my_contents = db.session.query(Content).filter_by(topic='Sports').all()

            return render_template('home.html', contents=my_contents, user=session['user'], formf=filter_form, formt=topic_form, cond=cond, top=top1)
    else:
        return redirect(url_for('login'))
########################################################################################################
# IP
app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000

# Note that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.
