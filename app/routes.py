from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Alain'}
    posts = [
        {
            'author': {'username': 'Al'},
            'body': 'How Bitcoin fixes this'
        },
        {
            'author': {'username': 'Bob'},
            'body': 'Why consistency matters'
        },
        {
            'author': {'username': 'Rhonda'},
            'body': 'What I learnt by mastering the handstand'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

