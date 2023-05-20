import os
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_ckeditor import CKEditor
from functools import wraps
from sqlalchemy import exc
from sqlalchemy.orm import relationship
from datetime import date
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from werkzeug.security import generate_password_hash, check_password_hash

# ========== App, Bootstrap and ckeditor initialization. ==========
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor = CKEditor(app)
Bootstrap(app)

# ========== DB initialization. ==========
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ========== Users table. ==========
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


# ========== Blogs table. ==========
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(30), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


# ========== Comment section table. ==========
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


# ========== Login manager initialization. ==========
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))


# ========== Create admin-only decorator. ==========
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            # Redirect to unauthorized page.
            return abort(403)
        # Otherwise, that's the admin user.
        return f(*args, **kwargs)

    return decorated_function


# # Line below only required once, when creating DB.
# with app.app_context():
#     db.create_all()

# ========== Gravatar initialization. ==========
gravatar = Gravatar(
    app,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)


# ========== Posts management section. ==========
@app.route('/')
def get_all_posts():
    """
    Function renders the home page with the blogs from the db.
    """
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>", methods=["GET", "POST"])
def show_post(index):
    """
    Function tries to fetch a blog from the db and render its page.
    :param index: ID of the blog post in the db.
    """
    requested_post = BlogPost.query.get(index)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You need to login or register to comment.')
            return redirect(url_for('login'))

        # Create new comment object.
        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        try:
            db.session.add(new_comment)
            db.session.commit()
            # Clean the comment section text.
            flash("Successfully added the comment.")
            return redirect(url_for("show_post", index=requested_post.id))
        except exc.IntegrityError:
            db.session.rollback()
    return render_template(
        'post.html',
        post=requested_post,
        form=comment_form,
        current_user=current_user
    )


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def new_post():
    """
    Function handles the possibility of adding
    a new blog post to the website.
    """
    post_form = CreatePostForm()
    if request.method == 'POST' and post_form.validate_on_submit():
        # Create new post object.
        add_new_post = BlogPost(
            title=post_form.title.data,
            subtitle=post_form.subtitle.data,
            body=post_form.body.data,
            img_url=post_form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        try:  # Try to add the new object to the db.
            db.session.add(add_new_post)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
        # Fetch all posts in the db.
        posts = db.session.query(BlogPost).all()
        # Redirect to the home page with the newly updated posts.
        return redirect(url_for('get_all_posts', all_posts=posts))
    return render_template("make-post.html", form=post_form, is_edit=False)


@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    """
    Function handles the ability to edit an existing post.
    :param post_id: The ID of the post that should be edited.
    """
    # Get current post
    post = db.session.get(BlogPost, post_id)
    # Populate the form with the existing post details.
    edit_form = CreatePostForm(obj=post)
    if edit_form.validate_on_submit():
        # Update the post with the data from the submitted form.
        edit_form.populate_obj(post)
        db.session.commit()
        return redirect(url_for('show_post', index=post.id))
    return render_template('make-post.html', form=edit_form, is_edit=True)


@app.route('/delete/<int:post_id>')
@admin_only
def delete_post(post_id):
    """
    Function handles the deletion of a post from the db.
    :param post_id: The ID of the post that should be deleted.
    """
    try:
        # Get the post that should be deleted from the db.
        post_to_delete = BlogPost.query.get(post_id)
        # Try to delete the post from the db.
        db.session.delete(post_to_delete)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
    return redirect(url_for('get_all_posts'))


# ========== Users management section ==========


@app.route('/register', methods=["GET", "POST"])
def register():
    """
    Function handles the blog registration.
    """
    register_form = RegisterForm()
    if request.method == 'POST' and register_form.validate_on_submit():
        # Get the
        name = register_form.name.data
        email = register_form.email.data
        password = register_form.password.data
        try:  # Try to create the new user.
            new_user = User(
                name=name,
                email=email,
                password=generate_password_hash(password, salt_length=8, method="pbkdf2:sha256")
            )
            db.session.add(new_user)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            flash("Email already exists. Log in instead or click on 'Forgot Password'.", category='error')
            return redirect(url_for('login'))
        else:
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
    return render_template('register.html', form=register_form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Function handles the blog login for existing users.
    """
    login_form = LoginForm()
    if request.method == 'POST' and login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = User.query.filter_by(email=email).first()
        # Check if "forgot password" was clicked.
        if login_form.forgot_password.data:
            flash("Forgot password functionality coming soon!", "info")
            return redirect(url_for('login'))
        # Check if email doesn't exist.
        elif not user:
            flash("Email does not exist, try again.")
            return redirect(url_for('login'))
        # Check if wrong password.
        elif not check_password_hash(user.password, password):
            flash("Incorrect password, please try again.")
            return redirect(url_for('login'))
        # Success login.
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template('login.html', form=login_form)


@app.route('/logout')
def logout():
    """
    Function handles logging out of the user.
    """
    logout_user()
    return redirect(url_for('get_all_posts'))


# ========== About and contact pages ==========

@app.route("/about")
def about():
    """
    Function renders the about page.
    """
    return render_template("about.html")


@app.route("/contact")
def contact():
    """
    Function renders the contact page.
    """
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
