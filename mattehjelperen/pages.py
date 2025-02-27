from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from mattehjelperen.auth import login_required

from mattehjelperen.db import get_db

bp = Blueprint('pages', __name__)

@bp.route('/not-developed-yet')
def not_developed():
  return render_template('page-not-developed.html')

# Rulebook urls
@bp.route('/rulebook')
def rulebook():
  return render_template('rulebook/nav.html')

@bp.route('/rulebook/tall-og-tallregning')
def rulebook_tall():
  return render_template('rulebook/tall-og-tallregning/tall-og-tallregning-nav.html')

@bp.route('/rulebook/tall-og-tallregning/brok-prosent')
def rulebook_brok_prosent():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_brok_prosent')
    return render_template('rulebook/tall-og-tallregning/brok-prosent.html', favorite = favorite)
  return render_template('rulebook/tall-og-tallregning/brok-prosent.html', favorite = -1)

@bp.route('/rulebook/tall-og-tallregning/brokregning')
def rulebook_brokregning():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_brokregning')
    return render_template('rulebook/tall-og-tallregning/brokregning.html', favorite = favorite)
  return render_template('rulebook/tall-og-tallregning/brokregning.html', favorite = -1)

@bp.route('/rulebook/tall-og-tallregning/delelighet')
def rulebook_delelighet():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_delelighet')
    return render_template('rulebook/tall-og-tallregning/delelighet.html', favorite = favorite)
  return render_template('rulebook/tall-og-tallregning/delelighet.html', favorite = -1)

@bp.route('/rulebook/tall-og-tallregning/kvadratrot-og-kvadrattall')
def rulebook_kvadratrot():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_kvadratrot')
    return render_template('rulebook/tall-og-tallregning/kvadratrot-og-kvadrattall.html', favorite = favorite)
  return render_template('rulebook/tall-og-tallregning/kvadratrot-og-kvadrattall.html', favorite = -1)

@bp.route('/rulebook/tall-og-tallregning/overslag')
def rulebook_overslag():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_overslag')
    return render_template('rulebook/tall-og-tallregning/overslag.html', favorite = favorite)
  return render_template('rulebook/tall-og-tallregning/overslag.html', favorite = -1)

@bp.route('/rulebook/tall-og-tallregning/potenser')
def rulebook_potenser():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_potenser')
    return render_template('rulebook/tall-og-tallregning/potenser.html', favorite = favorite)
  return render_template('rulebook/tall-og-tallregning/potenser.html', favorite = -1)

@bp.route('/rulebook/tall-og-tallregning/primtallsfaktorisering')
def rulebook_primtallsfaktorisering():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_primtallsfaktorisering')
    return render_template('rulebook/tall-og-tallregning/primtallsfaktorisering.html', favorite = favorite)
  return render_template('rulebook/tall-og-tallregning/primtallsfaktorisering.html', favorite = -1)

@bp.route('/rulebook/tall-og-tallregning/regnerekkefolge')
def rulebook_regnerekkefolge():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_regnerekkefolge')
    return render_template('rulebook/tall-og-tallregning/regnerekkefolge.html', favorite = favorite)
  return render_template('rulebook/tall-og-tallregning/regnerekkefolge.html', favorite = -1)


@bp.route('/rulebook/algebra')
def rulebook_algebra():
  return render_template('rulebook/algebra/algebra-nav.html')

@bp.route('/rulebook/algebra/algebraiske-uttrykk')
def rulebook_algebraiske_uttrykk():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_algebraiske_uttrykk')
    return render_template('rulebook/algebra/algebraiske-uttrykk.html', favorite = favorite)
  return render_template('rulebook/algebra/algebraiske-uttrykk.html', favorite = -1)

@bp.route('/rulebook/algebra/figurtall')
def rulebook_figurtall():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_figurtall')
    return render_template('rulebook/algebra/figurtall.html', favorite = favorite)
  return render_template('rulebook/algebra/figurtall.html', favorite = -1)

@bp.route('/rulebook/algebra/likninger')
def rulebook_likninger():
  if g.user:
    favorite = check_for_favorite('pages.rulebook_likninger')
    return render_template('rulebook/algebra/likninger.html', favorite = favorite)
  return render_template('rulebook/algebra/likninger.html', favorite = -1)





@bp.route('/tasks')
def tasks():
  return render_template('tasks/nav.html')

@bp.route('/tasks/tall-og-tallregning')
def tasks_tall():
  return render_template('tasks/tall-og-tallregning/tall-og-tallregning-nav.html')





@bp.route('/<string:page_id>/<string:category>/<string:title>/add_favorite')
def add_favorite(page_id, category, title):
  db = get_db()
  db.execute(
    ' INSERT INTO favorite (user_id, page_id, category, title)'
    ' values (?, ?, ?, ?)',
    (g.user['user_id'], page_id, category, title)
  )
  db.commit()
  return redirect(url_for(page_id))

@bp.route('/<string:page_id>/delete_favorite')
def delete_favorite(page_id):
  db = get_db()
  db.execute(
    ' DELETE FROM favorite WHERE ((page_id = ?) and (user_id = ?)) ',
    (page_id, g.user['user_id'])
  )
  db.commit()
  return redirect(url_for(page_id))

def check_for_favorite(page_id):
  db = get_db()
  favorite = db.execute(
    ' SELECT * FROM favorite '
    ' WHERE (page_id = ?) and (user_id = ?)',
    (page_id, g.user['user_id'])
  ).fetchone()
  if favorite:
    return 1
  else:
    return 0