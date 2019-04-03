# app/listings/views.py

from flask import flash, redirect, render_template, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import text
from . import listings
from .forms import ListingForm, CheckForm
from .. import db
from ..models import User, comicbook, Selling, Author
from werkzeug.security import generate_password_hash
from werkzeug.datastructures import MultiDict
import datetime
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
        
        
        sql = text('SELECT series FROM comicbook WHERE UPPER(series) = :x AND issueNum = :i AND publisher = :p')
        
        result = connection.execute(sql, x =form.series.data.upper() , i = form.issueNum.data, p = form.publisher.data)
        row = result.fetchone()
        if not row:
            #comic book does not exist in database
            
            insertComicBook = text('INSERT INTO ComicBook (publisher, series, seriesUpper, issueNum, primaryCharacter, primaryVillain, genre, authoredBy, id)'
                                   'VALUES(:a, :b, :c, :d, :e, :f, :g, :h, :i)')
            isAuthor = text('SELECT name FROM Author WHERE UPPER(Author.name) = :authorName')
            result1 = connection.execute(isAuthor, authorName=form.author.data.upper())
            row1 = result1.fetchone()
            if not row1:
                #author does not exist in database
                insertAuthor = text('INSERT INTO Author (name) VALUES (:authorName)')
                connection.execute(insertAuthor, authorName = form.author.data)
            #We know now that author must be in database 
            getAuthorId = text('SELECT id FROM Author WHERE Author.name = :authorName')
            authorId = connection.execute(getAuthorId, authorName=form.author.data).fetchone().id
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
        getBookId = text('SELECT id FROM comicbook WHERE UPPER(series) = :x AND issueNum = :i AND publisher = :p')
        bookId = connection.execute(getBookId, x = form.series.data.upper(), i = form.issueNum.data, p = form.publisher.data).first().id
        userID = current_user.id
        insertListing = text('INSERT INTO Selling (price, date_posted, book, userID, cgc) VALUES (:p, :dp, :bo, :u, :c)')
        connection.execute(insertListing, p = form.price.data, dp = form.datePosted.data, bo = bookId, u = userID, c = form.cgc.data)
       
            
        # Add user to the database
        #db.session.add(user)
        #db.session.commit()
    

        connection.close()
        return redirect(url_for('home.dashboard'))
        
    # listing not validated
    return render_template('listings/addListing.html', form=form, title='New Listing')


@listings.route('/allListings', methods=['GET', 'POST'])
def allListings():
    """
    Handle requests to see all listings
    """
    
    form = CheckForm()
    
    engine = db.engine
    connection = engine.connect()

    if form.validate_on_submit():
        if (form.reset.data == True):
            #sql = text('SELECT author.name, comicbook.id, comicbook.series, comicbook.issueNum, selling.price, selling.cgc, selling.id AS sellID FROM author JOIN (comicbook JOIN selling ON comicbook.id = selling.book) ON author.id = comicbook.authoredBy')
            #result = connection.execute(sql).fetchall()
            #connection.close()
            #return render_template('listings/allListings.html', title='All Listings', output1 = result, form = form)
            return redirect(url_for('listings.allListings'))
        if (form.series.data != '' and form.issueNum.data is not None):
            
            sql = text('SELECT author.name, comicbook.id, comicbook.series, comicbook.issueNum, selling.price, selling.cgc, selling.id AS sellID FROM author JOIN (comicbook JOIN selling ON comicbook.id = selling.book) ON author.id = comicbook.authoredBy WHERE UPPER(comicbook.series) = :x AND comicbook.issueNum = :y')
            result = connection.execute(sql, x = form.series.data.upper(), y = form.issueNum.data).fetchall()
        elif (form.series.data != '' and form.issueNum.data is None):
            sql = text('SELECT author.name, comicbook.id, comicbook.series, comicbook.issueNum, selling.price, selling.cgc, selling.id AS sellID FROM author JOIN (comicbook JOIN selling ON comicbook.id = selling.book) ON author.id = comicbook.authoredBy WHERE comicbook.series = :x')
            result = connection.execute(sql, x = form.series.data).fetchall()        
        elif (form.character.data == '' and form.villain.data != ''):
            sql = text('SELECT author.name, comicbook.id, comicbook.series, comicbook.issueNum, selling.price, selling.cgc, selling.id AS sellID FROM author JOIN (comicbook JOIN selling ON comicbook.id = selling.book) ON author.id = comicbook.authoredBy WHERE UPPER(comicbook.primaryVillain) = :x')
            result = connection.execute(sql, x = form.villain.data.upper()).fetchall()
        elif (form.character.data != '' and form.villain.data == ''):
            sql = text('SELECT author.name, comicbook.id, comicbook.series, comicbook.issueNum, selling.price, selling.cgc, selling.id AS sellID FROM author JOIN (comicbook JOIN selling ON comicbook.id = selling.book) ON author.id = comicbook.authoredBy WHERE UPPER(comicbook.primaryCharacter) = :x')
            result = connection.execute(sql, x = form.character.data.upper()).fetchall()
        elif (form.character.data != '' and form.villain.data != ''):
            sql = text('SELECT author.name, comicbook.id, comicbook.series, comicbook.issueNum, selling.price, selling.cgc, selling.id AS sellID FROM author JOIN (comicbook JOIN selling ON comicbook.id = selling.book) ON author.id = comicbook.authoredBy WHERE UPPER(comicbook.primaryCharacter) = :x AND  UPPER(comicbook.primaryVillain) = :y')
            result = connection.execute(sql, x = form.character.data.upper(), y = form.villain.data.upper()).fetchall()
        else:
            sql = text('SELECT author.name, comicbook.id, comicbook.series, comicbook.issueNum, selling.price, selling.cgc, selling.id AS sellID FROM author JOIN (comicbook JOIN selling ON comicbook.id = selling.book) ON author.id = comicbook.authoredBy')
            result = connection.execute(sql).fetchall()
            connection.close()
            return render_template('listings/allListings.html', title='All Listings', output1 = result, form = form) 
        connection.close()
        return render_template('listings/allListings.html', title='All Listings', output1 = result, form = form)
    
    sql = text('SELECT author.name, comicbook.id, comicbook.series, comicbook.issueNum, selling.price, selling.cgc, selling.id AS sellID FROM author JOIN (comicbook JOIN selling ON comicbook.id = selling.book) ON author.id = comicbook.authoredBy')
    
    result = connection.execute(sql).fetchall()
    
    
    connection.close()
    return render_template('listings/allListings.html', title='All Listings', output1 = result, form = form)

@listings.route('/yourListings', methods=['GET', 'POST'])
def yourListings():
    engine = db.engine
    connection = engine.connect()
    if current_user.is_authenticated:
        user = current_user.id
        
    sql = text('SELECT comicbook.id, comicbook.series, comicbook.issueNum, s1.price, s1.id AS sellID, s1.cgc FROM comicbook, (SELECT selling.book, selling.cgc, selling.price, selling.id FROM selling WHERE selling.userID = :x) as s1 WHERE comicbook.id = s1.book')
    

    result = connection.execute(sql, x = user).fetchall()

    connection.close()
    return render_template('listings/yourListings.html', title='Your Listings', output1 = result)    
    #return redirect(url_for('home.dashboard'))

@listings.route('/deleteListings/<int:id>',methods=['GET', 'POST'])
def deleteListings(id):
    engine = db.engine
    connection = engine.connect()
    
    sql = text('DELETE from selling WHERE selling.id = :x')
    connection.execute(sql, x = id)
    
    connection.close()
    return redirect(url_for('home.dashboard'))


@listings.route('/editListings/<int:sellID>',methods=['GET', 'POST'])
def editListings(sellID):
    form = ListingForm()
    
    if form.validate_on_submit():
        engine = db.engine
        connection = engine.connect()
       
        

        
        seriesUpper = form.series.data
        seriesUpper.upper()
        
        
        sql = text('SELECT series FROM comicbook WHERE UPPER(series) = :x AND issueNum = :i AND publisher = :p')
        
        result = connection.execute(sql, x = form.series.data.upper(), i = form.issueNum.data, p = form.publisher.data)
        row = result.fetchone()
        if not row:
            #comic book does not exist in database
            
            insertComicBook = text('INSERT INTO ComicBook (publisher, series, seriesUpper, issueNum, primaryCharacter, primaryVillain, genre, authoredBy, id)'
                                   'VALUES(:a, :b, :c, :d, :e, :f, :g, :h, :i)')
            isAuthor = text('SELECT name FROM Author WHERE UPPER(Author.name) = :authorName')
            result1 = connection.execute(isAuthor, authorName=form.author.data.upper())
            row1 = result1.fetchone()
            if not row1:
                #author does not exist in database
                insertAuthor = text('INSERT INTO Author (name) VALUES (:authorName)')
                connection.execute(insertAuthor, authorName = form.author.data)
            #We know now that author must be in database 
            getAuthorId = text('SELECT id FROM Author WHERE Author.name = :authorName')
            authorId = connection.execute(getAuthorId, authorName=form.author.data).fetchone().id
            maxId = 0
            getTableSize = text('SELECT * FROM comicbook')
            r = connection.execute(getTableSize)
            if r.first():
                getMaxId = text('SELECT MAX(id) AS id FROM comicbook')
                maxId = connection.execute(getMaxId).fetchone().id + 1
            
            connection.execute(insertComicBook, a = form.publisher.data, b = form.series.data, c = seriesUpper,
                          d = form.issueNum.data, e = form.primaryCharacter.data, f=form.primaryVillain.data, g = form.genre.data, h = authorId, i = maxId)
        #We know now that book must exist in database
        getBookId = text('SELECT id FROM comicbook WHERE UPPER(series) = :x AND issueNum = :i AND publisher = :p')
        bookId = connection.execute(getBookId, x = form.series.data.upper(), i = form.issueNum.data, p = form.publisher.data).first().id
        userID = current_user.id
        updateListing = text('UPDATE selling SET price = :p, date_posted = :dp, book = :bo, userID = :u, cgc = :c WHERE selling.id= :si')
        connection.execute(updateListing, p = form.price.data, dp = form.datePosted.data, bo = bookId, u = userID, c = form.cgc.data, si =sellID)
       
            
        # Add user to the database
        #db.session.add(user)
        #db.session.commit()
        flash('Listing added')

        connection.close()
        return redirect(url_for('home.dashboard'))
        
    # listing not validated
    return render_template('listings/editListing.html', form=form, title='Edit Listing')

@listings.route('/openListings/<int:sellID>',methods=['GET', 'POST'])
def openListings(sellID):
    engine = db.engine
    connection = engine.connect()

    sql = text('SELECT  comicbook.id, comicbook.series, comicbook.issueNum, sell.price, sell.cgc, sell.id AS sellID FROM comicbook, (SELECT selling.id, selling.book, selling.price, selling.cgc FROM selling WHERE selling.id = :si) AS sell WHERE comicbook.id = sell.book')
    result= connection.execute(sql, si = sellID).fetchall()
    
    connection.close()    
    return render_template('listings/openListing.html', output1=result)
@listings.route('/buyListings/<int:sellID>',methods=['GET', 'POST'])
def buyListings(sellID):
    engine = db.engine
    connection = engine.connect()

    now = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    sql = text('SELECT selling.price, selling.userID, selling.book, selling.cgc FROM selling WHERE selling.id = :s')
    result = connection.execute(sql, s = sellID).fetchone()
    sql = text('INSERT INTO sold (priceSold, dateSold, userID, book, cgc) VALUES (:p, :d, :u, :b, :c)')
    
    connection.execute(sql, p = result.price, d = now, u = result.userID, b = result.book, c = result.cgc)
    sql = text('DELETE FROM selling WHERE selling.id = :z')
    connection.execute(sql, z = sellID)
    return redirect(url_for('home.dashboard'))

