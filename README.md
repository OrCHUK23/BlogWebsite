# Project: Blogging Website

## Description
This project is a blogging website developed using the Flask framework.
It allows users to create accounts, write blog posts, add comments, and manage the content of the website.
The website includes features like user registration, login, authentication, and authorization.

## Technologies Used
- Flask: Python web framework used for developing the website.
- Flask-Bootstrap: Extension for Flask that integrates Bootstrap CSS framework.
- Flask-SQLAlchemy: Extension for Flask that provides integration with SQLAlchemy ORM.
- Flask-Gravatar: Extension for Flask to generate Gravatar images based on user email.
- Flask-Login: Extension for Flask that handles user session management.
- Flask-WTF: Extension for Flask that integrates WTForms library for form handling.
- Flask-CKEditor: Extension for Flask that provides a rich text editor using CKEditor.
- SQLite: Database system used for storing user information, blog posts, and comments.
- Gunicorn: WSGI HTTP server used for deployment.

## Project Structure
The project consists of the following files and directories:

- `main.py`: The main Flask application file that contains the routes and logic for the website.
- `forms.py`: Contains the form classes used for user registration, login, creating posts, and adding comments.
- `templates/`: Directory containing the HTML templates for the website.
- `static/`: Directory containing static assets such as CSS stylesheets and images.
- `blog.db`: SQLite database file used for storing the website data.
- `Procfile`: File specifying the command to run the application using Gunicorn.
- `requirements.txt`: File listing the required Python packages and versions.

## Installation and Setup
To run the project locally, follow these steps:

1. Clone the project repository.
2. Create a virtual environment and activate it.
3. Install the required packages using the command: `pip install -r requirements.txt`.
4. Set the `SECRET_KEY` environment variable.
5. Run the Flask application using the command: `python main.py`.
6. Access the website in a web browser at `http://localhost:5000`.

## Usage
- Access the home page to view all the blog posts.
- Register a new account or login with an existing account.
- Create new blog posts and add comments to existing posts.
- Only the admin user (user ID 1) has the ability to create, edit, and delete posts.
- Edit or delete your own posts or comments.
- Logout from the website when done.

## Deployment

To deploy the project to a production environment, follow these steps:

1. Set up a server with the required dependencies (Python, Gunicorn, SQLite).
2. Clone the project repository onto the server.
3. Configure the server to run the Flask application using Gunicorn with the specified Procfile.
4. Set up a domain name and configure the server to serve the website on that domain.
5. Configure SSL/TLS certificates for secure HTTPS communication.
6. Start the Gunicorn server and access the website using the domain name.

## Future Enhancements

- Implement password reset functionality.
- Add user profile pages.
- Improve the UI and design of the website.
- Implement pagination for blog posts.
- Allow users to like or rate blog posts.
- Implement a search feature to search for blog posts.

---

*Note: This Markdown file provides an overview of the project and its structure. Refer to the source code for the actual implementation details.*
