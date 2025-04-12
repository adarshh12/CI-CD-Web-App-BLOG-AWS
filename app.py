from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'

USERS_CSV = 'users.csv'
POSTS_CSV = 'posts.csv'


def read_users():
    with open(USERS_CSV, 'r') as f:
        return list(csv.DictReader(f))


def read_posts():
    with open(POSTS_CSV, 'r') as f:
        return list(csv.DictReader(f))


def write_post(post_list):
    with open(POSTS_CSV, 'w', newline='') as f:
        fieldnames = ['id', 'title', 'content', 'author', 'date']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(post_list)


@app.route('/')
def home():
    posts = read_posts()
    return render_template('base.html', posts=posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = read_users()
        if any(user['username'] == username for user in users):
            flash('Username already exists')
            return redirect(url_for('signup'))
        with open(USERS_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password])
        flash('Signup successful. Please login.')
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = read_users()
        username = request.form['username']
        password = request.form['password']
        if any(u['username'] == username and u['password'] == password for u in users):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    posts = read_posts()
    return render_template('dashboard.html', posts=posts, username=session['username'])


@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        posts = read_posts()
        new_id = str(len(posts) + 1)
        new_post = {
            'id': new_id,
            'title': request.form['title'],
            'content': request.form['content'],
            'author': session['username'],
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        posts.append(new_post)
        write_post(posts)
        return redirect(url_for('dashboard'))

    return render_template('create_post.html')


@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    posts = read_posts()
    post = next((p for p in posts if p['id'] == id), None)

    if not post or post['author'] != session['username']:
        return "Unauthorized"

    if request.method == 'POST':
        post['title'] = request.form['title']
        post['content'] = request.form['content']
        write_post(posts)
        return redirect(url_for('dashboard'))

    return render_template('update_post.html', post=post)


@app.route('/delete/<id>')
def delete(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    posts = read_posts()
    post = next((p for p in posts if p['id'] == id), None)

    if not post or post['author'] != session['username']:
        return "Unauthorized"

    posts = [p for p in posts if p['id'] != id]
    write_post(posts)
    return redirect(url_for('dashboard'))


@app.route('/view/<id>')
def view_post(id):
    if 'username' not in session:
        # Force login if not logged in
        flash("Please login to read the full blog.")
        return redirect(url_for('login'))
        
    posts = read_posts()
    post = next((p for p in posts if p['id'] == id), None)
    if not post:
        return "Post Not Found"
    return render_template('view_post.html', post=post)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)