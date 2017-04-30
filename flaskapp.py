import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField, PasswordField, IntegerField
from wtforms.validators import Required, DataRequired
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    posts = db.relationship('Post', backref='genres', lazy='dynamic')

    def __repr__(self):
        return '<Genre %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    homeTown = db.Column(db.Integer)
    bio = db.Column(db.String(64))
    is_musician = db.Column(db.Boolean)
    posts = db.relationship('Post', backref='users', lazy='dynamic')
    comments = db.relationship('Comment', backref='users', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.name

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(64))
    content = db.Column(db.String(64))
    votes = db.Column(db.Integer)
    comments = db.relationship('Comment', backref='posts', lazy='dynamic')

    def __repr__(self):
        return '<Post %r>' % self.name

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(64))
    whoPosted = db.Column(db.String(64))
    posts_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Comment %r>' % self.name


class PostForm(Form):
    genre = SelectField('Breed', coerce=int, validators=[DataRequired()])
    name = StringField('Name of Post?', validators=[Required()])
    content = StringField('Content?', validators=[Required()])
    submit = SubmitField('Submit')

class CommentForm(Form):
    content = StringField('Comment?', validators=[Required()])
    submit = SubmitField('Submit')

class ArtistSignUpForm(Form):
    email = StringField('What is your email?', validators=[Required()])
    hometown = IntegerField('What is your Zip Code?', validators=[Required()])
    bio = StringField('What is your description?', validators=[Required()])
    password1 = PasswordField('Password', validators=[Required()])
    password2 = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Submit')

class LoginForm(Form):
    email = StringField('What is your email?', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Submit')

class GenreForm(Form):
    name = StringField('What is your Genre name?', validators=[Required()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/New Post', methods=['GET', 'POST'])
def NewPost():
    form = PostForm()
    form.genre.choices = [(a.id, a.name) for a in Genre.query.order_by(Genre.name)]
    name = session['user']
    userDetails = User.query.filter_by(name=name).first()
    if form.validate_on_submit():
        newPost = Post(genre_id=form.genre.data, user_id = userDetails.id, name=form.name.data, content=form.content.data)
        db.session.add(newPost)
        flash('Added Post to database!')
        return redirect(url_for('NewPost'))
    return render_template('New Post.html', form=form)

@app.route('/Show Post/<id>', methods=['GET', 'POST'])
def ShowPost(id):
    form = CommentForm()
    Posts = Post.query.filter_by(id=id).first()
    name = session['user']
    userDetails = User.query.filter_by(name=name).first()
    postComments = Comment.query.filter_by(posts_id=id)
    if form.validate_on_submit():
        newComment = Comment(posts_id=id, user_id=userDetails.id, content=form.content.data, whoPosted = userDetails.name)
        db.session.add(newComment)
        flash('Added Comment to database!')
        return redirect(url_for('ShowPost' , postDetails=Posts , id=id, postComments=postComments))
    return render_template('Show Post.html', postDetails=Posts, id=id, postComments=postComments, form=form)



@app.route('/New Genre', methods=['GET', 'POST'])
def NewGenre():
    form = GenreForm()
    if form.validate_on_submit():
        newGenre = Genre.query.filter_by(name=form.name.data).first()
        if newGenre is None:
            newGenre = Genre(name=form.name.data)
            db.session.add(newGenre)
            flash('Added Genre to database!')
        return redirect(url_for('NewGenre'))
    return render_template('New Breed.html', form=form)

@app.route('/New Artist', methods=['GET', 'POST'])
def NewArtist():
    form = ArtistSignUpForm()
    if form.validate_on_submit():
        newArtist = User.query.filter_by(name=form.email.data).first()
        if newArtist is None and (form.password1.data == form.password2.data):
            newArtist = User(name=form.email.data, password=form.password1.data, homeTown=form.hometown.data, bio=form.bio.data, is_musician = True)
            session['user'] = form.email.data
            session['logged_in'] = True
            db.session.add(newArtist)
            flash('Added Artist to database!')
        return redirect(url_for('UserPage'))
    return render_template('New Breeder.html', form=form)

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    form = LoginForm()
    if form.validate_on_submit():
        userName = User.query.filter_by(name=form.email.data).first()
        if (form.password.data == userName.password):
            session['user'] = form.email.data
            session['logged_in'] = True
            return redirect(url_for('UserPage'))
        flash('Wrong Login Details!')
    return render_template('Login.html', form=form)

@app.route('/Logout', methods=['GET', 'POST'])
def Logout():
    session['logged_in'] = False
    return render_template('index.html')

@app.route('/New User', methods=['GET', 'POST'])
def NewUser():
    form = ArtistSignUpForm()
    if form.validate_on_submit():
        newUser = User.query.filter_by(name=form.email.data).first()
        if newUser is None and (form.password1.data == form.password2.data):
            newUser = User(name=form.email.data, password=form.password1.data, homeTown=form.hometown.data, bio=form.bio.data, is_musician = False)
            session['user'] = form.email.data
            session['logged_in'] = True
            db.session.add(newUser)
            flash('Added User to database!')
        return redirect(url_for('UserPage'))
    return render_template('New User.html', form=form)

@app.route('/User Page', methods=['GET', 'POST'])
def UserPage():
    name = session['user']
    allDetails = User.query.filter_by(name=name).first()
    userPosts = Post.query.filter_by(user_id=allDetails.id)
    return render_template('User Page.html', allDetails=allDetails, userPosts = userPosts)

@app.route('/All Breeds', methods=['GET', 'POST'])
def AllBoards():
    allBoards = Genre.query.all()
    return render_template('All Breeds.html', allBoards=allBoards)

@app.route('/Breed/<id>', methods=['GET', 'POST'])
def Board(id):
    Posts = Post.query.filter_by(genre_id=id)
    thisBoard = Genre.query.filter_by(id=id).first()
    return render_template('Board.html', Posts=Posts, thisBoard=thisBoard)

@app.route('/UserOrArtist', methods=['GET', 'POST'])
def UserOrArtist():
    return render_template('UserOrBreeder.html')

@app.route('/Breeder List', methods=['GET'])
def ArtistList():
    name = session['user']
    userDetails = User.query.filter_by(name=name).first()
    allArtists = User.query.filter_by(is_musician=True)
    localArtists = User.query.filter_by(homeTown = userDetails.homeTown, is_musician=True)
    return render_template('Breeder List.html', allArtists=allArtists, localArtists = localArtists)

@app.route('/Breeder Details/<name>', methods=['GET', 'POST'])
def ArtistDetails(name):
    allArtists = User.query.filter_by(name = name).first()
    artistPosts = Post.query.filter_by(user_id=allArtists.id)
    return render_template('Breeder Details.html', allArtists=allArtists, artistPosts=artistPosts)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
