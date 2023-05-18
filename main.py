import os
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from sqlalchemy import exc
from datetime import datetime

# App, Bootstrap and ckeditor initialization.
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor = CKEditor(app)
Bootstrap(app)

# DB Initialization.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class BlogPost(db.Model):
    """
    Class configures the db columns inside "BlogPost" table.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm.
class CreatePostForm(FlaskForm):
    """
    Class configures new blog adding form.
    """
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    """
    Function renders the home page with the blogs from the db.
    """
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    """
    Function tries to fetch a blog from the db and render its page.
    :param index: ID of the blog post in the db.
    """
    requested_post = None
    posts = db.session.query(BlogPost).all()
    for blog_post in posts:
        if blog_post.id == index:
            requested_post = blog_post
            return render_template("post.html", post=requested_post)
    return redirect(url_for('get_all_posts', post=requested_post))


@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
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

@app.route('/delete/<int:post_id>', methods=["GET", "POST"])
def delete_post(post_id):
    """
    Function handles the deletion of a post from the db.
    :param post_id: The ID of the post that should be deleted.
    """
    try:
        # Get the post that should be deleted from the db.
        post_to_delete = db.session.get(BlogPost, post_id)
        # Try to delete the post from the db.
        db.session.delete(post_to_delete)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
    return redirect(url_for('get_all_posts'))
    # return render_template('index.html')

@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    """
    Function handles the possibility of adding a new blog post to the
    website.
    """
    post = CreatePostForm()
    if request.method == 'POST' and post.validate_on_submit():
        # Create new post object.
        post_to_add = BlogPost(
            title=request.form['title'],
            subtitle=request.form['subtitle'],
            author=request.form['author'],
            img_url=request.form['img_url'],
            body=request.form['body'],
            date=datetime.today().strftime("%B %d, %Y")
        )
        try:  # Try to add the new object to the db.
            db.session.add(post_to_add)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
        # Fetch all posts in the db.
        posts = db.session.query(BlogPost).all()
        # Redirect to the home page with the newly updated posts.
        return redirect(url_for('get_all_posts', all_posts=posts))
    return render_template("make-post.html", form=post, is_edit=False)


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
