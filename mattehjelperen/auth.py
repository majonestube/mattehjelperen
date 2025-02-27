import functools

from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for)

from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.exceptions import abort

from mattehjelperen.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def unauthorized_character(string):
  unauthorized_characters = ['<', '>', '/', ';', '=']
  if any(x in unauthorized_characters for x in string):
    return True

@bp.route('/register', methods=("GET", "POST"))
def register():
  if request.method == "POST":
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    db = get_db()
    error = None

    if not username:
      error = 'Brukernavn er obligatorisk.'
    elif not password:
      error = 'Passord er obligatorisk.'
    elif password != confirm_password:
      error = 'Passordene er ikke like.'
    elif unauthorized_character(username) or unauthorized_character(password) or unauthorized_character(confirm_password):
      error = 'Følgende tegn er ikke tillatt: < > / ; ='

    if error is None:
      try:
        db.execute(
          "INSERT INTO user(username, password) VALUES (?, ?)",
          (username, generate_password_hash(password)),
        )
        db.commit()
      except db.IntegrityError:
        error = f'Bruker {username} er allerede registrert.'
      else: 
        return redirect(url_for("auth.login"))
      
    flash(error)
  
  return render_template('auth/register.html')

@bp.route('/login', methods=("GET", "POST"))
def login():
  if request.method == "POST":
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None
    user = db.execute(
      'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
      error = f'Bruker {username} er ikke registrert.'
    elif not check_password_hash(user['password'], password):
      error = "Feil passord."
    elif unauthorized_character(username) or unauthorized_character(password):
      error = 'Følgende tegn er ikke tillatt: < > / ; ='

    if error is None:
      session.clear()
      session['user_id'] = user['user_id']
      session['admin'] = user['admin']
      return redirect(url_for('index'))
    
    flash(error)
  
  return render_template('auth/login.html')
    
@bp.before_app_request
def load_loggin_in_user():
  user_id = session.get('user_id')

  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute(
      'SELECT * FROM user WHERE user_id = ?', (user_id,)
    ).fetchone()

@bp.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))

def login_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))
  
    return view(**kwargs)
  return wrapped_view

def admin_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user['admin'] != 1:
      return redirect(url_for('auth.login'))
  
    return view(**kwargs)
  return wrapped_view

@bp.route('/my-page')
@login_required
def my_page():
  db = get_db()
  favorites = db.execute(
    ' SELECT * FROM favorite '
    ' WHERE user_id = ? ',
    (g.user['user_id'],)
  ).fetchall()

  if g.user['admin'] == 1:
    cursor = db.execute(
      'SELECT COUNT(*) AS message_count '
      ' FROM message '
    )
    row = cursor.fetchone()
    messages_count = row[0] if row else 0
    return render_template('my-page.html', favorites=favorites, messages_count=messages_count)

  return render_template('my-page.html', favorites=favorites)


@bp.route('/admin/change-password', methods=('GET', 'POST'))
@login_required
@admin_required
def admin_change_password():
  if request.method =='POST':
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    db = get_db()
    error = None
    user = db.execute(
      'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if not username: 
      error = 'Brukernavn er obligatorisk.'
    elif user is None:
      error = 'Bruker finnes ikke.'
    elif password != confirm_password:
      error = 'Passordene må være like.'
    
    if error is None:
      db.execute(
        'UPDATE user '
        'SET password = ?'
        'WHERE username = ?',
        (generate_password_hash(password), username,)
      )
      db.commit()
      flash('Passord endret.')

    flash(error)
  return render_template('auth/admin-change-password.html')

@bp.route('/change-password', methods=('GET', 'POST'))
@login_required
def change_password():
    if request.method == "POST":
      previous_password = request.form['previous_password']
      new_password = request.form['new_password']
      confirm_password = request.form['confirm_password']
      db = get_db()
      error = None

      if not previous_password:
        error = 'Tidligere passord er obligatorisk.'
      elif not new_password:
        error = 'Passord er obligatorisk.'
      elif not confirm_password:
        error = 'Passordet må bekreftes.'
      elif previous_password == new_password:
        error = 'Ditt nye passord kan ikke være det samme som ditt gamle.'
      elif new_password != confirm_password:
        error = 'De to siste feltene må være like.'
      elif unauthorized_character(previous_password) or unauthorized_character(new_password) or unauthorized_character(confirm_password):
        error = 'Følgende tegn er ikke tillatt: < > / ; ='

      if error is None:
          db.execute(
            'UPDATE user '
            'SET password = ?'
            'WHERE username = ?',
            (generate_password_hash(new_password), g.user['username'],)
          )
          db.commit()
          return redirect(url_for('auth.logout'))
        
      flash(error)
    
    return render_template('auth/change-password.html')


@bp.route('/admin/check-messages', methods=('GET', 'POST'))
@login_required
@admin_required
def check_messages():
  db = get_db()
  messages = db.execute(
      ' SELECT message_id, sender_id, created, topic, body, username '
      ' FROM message m JOIN user u on m.sender_id = u.user_id '
      ' ORDER BY created DESC').fetchall()
  return render_template('auth/check-messages.html', messages=messages)


# Trengs dette?
def get_message(id, check_author=True):
  message = get_db().execute(
    ' SELECT message_id, sender_id, created, topic, body, username '
      ' FROM message m JOIN user u on m.sender_id = u.user_id '
      ' ORDER BY created DESC'
  ).fetchone()

  if message is None:
    abort(404, f'Post med id {id} eksisterer ikke.')
  
  if check_author and g.user['admin'] != 1:
    abort(403)
  
  return message