from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from mattehjelperen.auth import login_required, get_message, unauthorized_character, admin_required
from mattehjelperen.db import get_db

bp = Blueprint('general', __name__)

@bp.route('/')
def index():
  db = get_db()
  posts = db.execute(
    ' SELECT post_id, p.title, p.body, p.created, author_id, username '
    ' FROM post p JOIN user u on p.author_id = u.user_id '
    ' ORDER BY created DESC'
  ).fetchall()
  return render_template('posts/index.html', posts=posts)

def get_post(id, check_author=True):
  post = get_db().execute(
    'SELECT p.post_id, title, body, created, author_id, username '
    'FROM post p JOIN user u ON p.author_id = u.user_id '
    'WHERE p.post_id = ?',
    (id,)
  ).fetchone()

  if post is None:
    abort(404, f'Post med id {id} eksisterer ikke.')
  
  if check_author and post['author_id'] != g.user['user_id']:
    abort(403)
  
  return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
@admin_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        error = None
    
        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE post_id = ?', 
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('general.index'))
    
    return render_template('posts/update.html', post=post)

@bp.route('/create-post', methods=('GET', 'POST'))
@login_required
@admin_required
def create_post():
  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']
    error = None
     
    if not title:
      error = 'Tittel er obligatorisk'

    if error is not None:
       flash(error)
    else:
       db = get_db()
       db.execute(
          'INSERT INTO post (title, body, author_id)'
          'VALUES (?, ?, ?)',
          (title, body, g.user['user_id'])
       )
       db.commit()
       return redirect(url_for('general.index'))
  
  return render_template('posts/create.html')
      
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
   get_post(id)
   db = get_db()
   db.execute('DELETE FROM post WHERE post_id = ?', (id,))
   db.commit()
   return redirect(url_for('general.index'))


@bp.route('/message-to-admin', methods=('GET', 'POST'))
@login_required
def message_to_admin():
    if request.method == 'POST':
      sender_id = g.user['user_id']
      topic = request.form['topic']
      body = request.form['body']
      error = None

      if not body:
         error = 'Meldingen din har ingen tekst'
      elif unauthorized_character(topic) or unauthorized_character(body):
        error = 'Følgende tegn er ikke tillatt: < > / ; ='
      
      if error is not None:
        flash(error)
      else:
        db = get_db()
        db.execute(
          'INSERT INTO message (sender_id, topic, body)'
          'VALUES (?, ?, ?)',
         (sender_id, topic, body)
         )
        db.commit()
        return redirect(url_for('general.index'))
  
    return render_template('message.html')
   
@bp.route('/message/<int:id>/delete', methods=('POST','GET'))
@login_required
def delete_message(id):
   get_message(id)
   db = get_db()
   db.execute('DELETE FROM message WHERE message_id = ?', (id,))
   db.commit()
   return redirect(url_for('auth.check_messages'))

