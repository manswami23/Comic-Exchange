# app/listings/views.py

from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import text
from . import listings
from .forms import ListingForm
from .. import db
from ..models import User, comicbook, Selling, Author
from werkzeug.security import generate_password_hash
@listings.route('/newListing', methods=['GET', 'POST'])
def newListing():
    """
    Handle requests to the /register route
    Add a user to the database through the registration form
    """
    form = ListingForm()
    
    if form.validate_on_submit():
        engine = db.engine
        connection = engine.connect()
       
        

        
        seriesUpper = form.series.data
        seriesUpper.upper()
        
        
        sql = text('SELECT series FROM comicbook WHERE seriesUpper = :x AND issueNum = :i AND publisher = :p')
        
        result = connection.execute(sql, x = seriesUpper, i = form.issueNum.data, p = form.publisher.data)
        row = result.fetchone()
        if not row:
            #comic book does not exist in database
            
            insertComicBook = text('INSERT INTO ComicBook (publisher, series, seriesUpper, issueNum, primaryCharacter, primaryVillain, genre, authoredBy, id)'
                                   'VALUES(:a, :b, :c, :d, :e, :f, :g, :h, :i)')
            isAuthor = text('SELECT name FROM Author WHERE Author.name = :authorName')
            result1 = connection.execute(isAuthor, authorName=form.author.data.upper())
            row1 = result1.fetchone()
            if not row1:
                #author does not exist in database
                insertAuthor = text('INSERT INTO Author (name) VALUES (:authorName)')
                connection.execute(insertAuthor, authorName = form.author.data.upper())
            #We know now that author must be in database 
            getAuthorId = text('SELECT id FROM Author WHERE Author.name = :authorName')
            authorId = connection.execute(getAuthorId, authorName=form.author.data.upper()).fetchone().id
            maxId = 0
            getTableSize = text('SELECT * FROM comicbook')
            r = connection.execute(getTableSize)
            if r.first():
                getMaxId = text('SELECT MAX(id) AS id FROM comicbook')
                maxId = connection.execute(getMaxId).fetchone().id + 1
            print ('hello')
            print (maxId)
            connection.execute(insertComicBook, a = form.publisher.data, b = form.series.data, c = seriesUpper,
                          d = form.issueNum.data, e = form.primaryCharacter.data, f=form.primaryVillain.data, g = form.genre.data, h = authorId, i = maxId)
        #We know now that book must exist in database
        getBookId = text('SELECT id FROM comicbook WHERE seriesUpper = :x AND issueNum = :i AND publisher = :p')
        bookId = connection.execute(getBookId, x = seriesUpper, i = form.issueNum.data, p = form.publisher.data).first().id
        userID = current_user.id
        insertListing = text('INSERT INTO Selling (price, date_posted, book, userID) VALUES (:p, :dp, :bo, :u)')
        connection.execute(insertListing, p = form.price.data, dp = form.datePosted.data, bo = bookId, u = userID)
       
            
        # Add user to the database
        #db.session.add(user)
        #db.session.commit()
        flash('Listing added')

        # redirect to the login page
        connection.close()
        return redirect(url_for('home.dashboard'))
        
    # load registration template
    return render_template('listings/addListing.html', form=form, title='New Listing')


@listings.route('/allListings', methods=['GET', 'POST'])
def allListings():
    """
    Handle requests to the /login route
    Log in a user through the login form
    """
    engine = db.engine
    connection = engine.connect()
    sql = text('SELECT comicbook.id, comicbook.series, comicbook.issueNum, selling.price FROM comicbook JOIN selling ON comicbook.id = selling.book')
    #deleteSelling = text('DELETE FROM selling WHERE selling.id <> -1')
    #deleteBook = text('DELETE FROM comicbook WHERE series = "Batman"')
    #connection.execute(deleteSelling)
    #connection.execute(deleteBook)
    

    #sql = text('SELECT comicbook.id, comicbook.series, comicbook.issueNum FROM comicbook')
    #sql = text('SELECT * FROM selling')
    result = connection.execute(sql)
    output = ''
    for _r in result:
        output += str(_r.id) + ', ' + _r.series + ', ' + str(_r.issueNum) + ', ' + str(_r.price) + '\n'
        print(str(_r.id) + ', ' + _r.series + ', ' + str(_r.issueNum) + ', ' + str(_r.price))
        #print(str(_r.book) + ', ' + str(_r.id) + ', ' + str(_r.price))
    

    
    
    
    return render_template('listings/allListings.html', title='All Listings', output1=output)


