from flask import render_template, url_for, redirect, flash, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.mongoflask import User, Post, Moviesdb, Ratings
from flaskblog import app, bcrypt, db
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
import secrets
import os
from flaskblog.mvrcsys import mvlogic


@app.route("/")
def home():
    # posts = Post.objects.order_by('-date_posted') doesn't work with cosmosdb don't know why?
    page = request.args.get('page', 1, type=int)
    posts = Post.objects.paginate(page=page, per_page=2)
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return "<h1>About Page</h1>"


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_pw)
        user.save()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful.', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            User.objects(id=current_user.id).update_one(
                set__image_file=picture_file)

        User.objects(id=current_user.id).update_one(
            username=form.username.data, email=form.email.data)
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.content.data, user_id=current_user.id)
        post.save()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)


@app.route("/post/<post_id>")
def post(post_id):
    post = Post.objects.get(id=post_id)
    return render_template('post.html', title=post.title, post=post, legend="New Post")


@app.route("/post/<post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.objects.get(id=post_id)
    if post.user_id.id != current_user.id:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        # Post.objects(id= post_id).update(title= form.title.data, content= form.content.data)
        post.title = form.title.data
        post.content = form.content.data
        post.save()
        flash('Your Post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title="Update Post", form=form, legend="Update Legend")


@app.route("/post/<post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.objects.get(id=post_id)
    if post.user_id.id != current_user.id:
        abort(403)
    post.delete()
    flash('Your Post has been deleted !', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.objects(username=username).first_or_404()
    posts = Post.objects(user_id=user)\
        .paginate(page=page, per_page=2)
    return render_template('user_post.html', posts=posts, user=user)


@app.route("/movies", methods=["GET", "POST"])
def movies():
    if request.method == 'POST':
        temprating = Ratings.objects(
            userId=current_user.id, movieId=request.args.get('mvidb')).first()
        if temprating:
            Ratings.objects(userId=current_user.id, movieId=request.args.get(
                'mvidb')).update_one(rating=request.form['movieratings'])
        else:
            newrating = Ratings(userId=current_user.id, movieId=request.args.get(
                'mvidb'), rating=request.form['movieratings'])
            newrating.save()

    page = request.args.get('page', 1, type=int)

    movieslist = Moviesdb.objects.paginate(page=page, per_page=5)
    tempr = Ratings.objects()
    return render_template("movies.html", movies=movieslist, tempr=tempr)


@app.route("/recommendations", methods=["POST", "GET"])
def recommendations():
    page = request.args.get('page', 1, type=int)
    userInput = []
    ratingsuser = Ratings.objects(userId=current_user.id)
    if not ratingsuser:
        return render_template('error.html')

    for obj in ratingsuser:
        dit = {}
        dit['title'] = obj.movieId.title
        dit['rating'] = obj.rating
        userInput.append(dit)

    # debug testing input
    # userInput = [
    #     {'title': 'Breakfast Club, The', 'rating': 5},
    #     {'title': 'Toy Story', 'rating': 3.5},
    #     {'title': 'Jumanji', 'rating': 2},
    #     {'title': "Pulp Fiction", 'rating': 5},
    #     {'title': 'Akira', 'rating': 4.5}
    # ]

    result = mvlogic(userInput).getrecommendations()

    recommendedmovies = Moviesdb.objects(
        movieId__in=result).paginate(page=page, per_page=5)
    return render_template('recommendations.html', recommendedmovies=recommendedmovies)
