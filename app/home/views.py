# app/home/views.py

from flask import render_template
from flask_login import login_required
from sqlalchemy import text
from .. import db
from . import home
from ..models import User, comicbook, Selling, Sold, Author
from werkzeug.datastructures import MultiDict
@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    
    """
    engine = db.engine
    connection = engine.connect()
    sql = text(
'SELECT s1.series, s1.issueNum, s1.cgc, s1.price FROM (SELECT comicbook.series, comicbook.primaryCharacter, comicbook.issueNum, selling.cgc, '+
'selling.price, selling.id as sellID FROM comicbook JOIN selling on comicbook.id = selling.book) as s1, '+
'(SELECT comicbook.primaryCharacter, COUNT(*) FROM (comicbook JOIN sold ON comicbook.id = sold.book) GROUP BY comicbook.primaryCharacter'+
' ORDER BY(COUNT(*)) DESC LIMIT 5) as s2' +' WHERE s1.primaryCharacter = s2.primaryCharacter')
    
    result = connection.execute(sql).fetchall()
    for _r in result:
        print(_r.series + ', #' +str(_r.issueNum)) 
    connection.close()


    return render_template('home/index.html', title="Welcome", output = result)


@home.route('/dashboard')
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """

    return render_template('home/dashboard.html', title="Dashboard")
