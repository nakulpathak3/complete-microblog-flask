from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, OAuthSignIn
from forms import EditForm, PostForm, EmailForm
from models import User, Post
from datetime import datetime
from config import POSTS_PER_PAGE

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    if not g.user.is_authenticated():
        return redirect(url_for('login'))
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html', title="Home", form=form, posts=posts)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not g.user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    username=User.make_unique_nickname(username)
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
    login_user(user, False)
    if g.user.email is None:
        return redirect(url_for('ask_email'))
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found' % nickname)
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html', user = user, posts = posts)

@app.route('/users')
@app.route('/users/<int:page>')
def users(page=1):
    users = User.query.all()
    return render_template('users.html', users = users)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        return render_template('edit.html', form=form)

@app.route('/ask_email', methods=['GET', 'POST'])
@login_required
def ask_email():
    form = EmailForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first() is None:
            g.user.email = form.email.data
            db.session.add(g.user)
            db.session.commit()
            flash('Your changes have been saved')
            return redirect(url_for('index'))
        else:
            flash('Email already in use')
            return redirect(url_for('ask_email'))
    else:
        return render_template('ask_email.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash("User %s not found." % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash("You can't unfollow yourself!")
        return redirect(url_for('index'))
    u = g.user.unfollow(user)
    if u is None:
        flash("Cannot unfollow user %s." % nickname)
        return redirect(url_for('user'), nickname=nickname)
    db.session.add(u)
    db.session.commit()
    flash("You have stopped following" + nickname + ".")
    return redirect(url_for('user', nickname=nickname))

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash("User %s not found." % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash("You can't follow yourself!")
        return redirect(url_for('index'))
    u = g.user.follow(user)
    if u is None:
        flash("Cannot follow user %s." % nickname)
        return redirect(url_for('user'), nickname=nickname)
    db.session.add(u)
    db.session.commit()
    flash("You are now following " + nickname + ".")
    return redirect(url_for('user', nickname=nickname))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post is None:
        flash('Post not found buddy')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('Not your post to delete')
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('Your post is gone :(')
    return redirect(url_for('index'))