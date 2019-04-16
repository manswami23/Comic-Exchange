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
from lxml import html, etree
import requests
from pprint import pprint
import unicodecsv as csv
from traceback import format_exc
import argparse
import urllib.request
import datetime
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import ssl
from .ml import mlOutputBooks, mlOutputGenre
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
        
        
        sql = text('SELECT series FROM comicbook JOIN author on comicbook.authoredBy = author.id WHERE UPPER(name) = :a AND UPPER(series) = :x AND issueNum = :i AND publisher = :p')
        
        result = connection.execute(sql, a = form.author.data.upper(), x = form.series.data.upper(), i = form.issueNum.data, p = form.publisher.data)
        
        row = result.fetchone()
        if not row:
            #comic book does not exist in database
            
            insertComicBook = text('INSERT INTO ComicBook (publisher, series, seriesUpper, issueNum, primaryCharacter, primaryVillain, genre, authoredBy, id)'
                                   'VALUES(:a, :b, :c, :d, :e, :f, :g, :h, :i)')
            isAuthor = text('SELECT name FROM Author WHERE UPPER(Author.name) = :authorName')
            result1 = engine.execute(isAuthor, authorName=form.author.data.upper())
            row1 = result1.fetchone()
            if not row1:
                #author does not exist in database
                insertAuthor = text('INSERT INTO Author (name) VALUES (:authorName)')
                engine.execute(insertAuthor, authorName = form.author.data)
            #We know now that author must be in database 
            getAuthorId = text('SELECT id FROM Author WHERE Author.name = :authorName')
            authorId = engine.execute(getAuthorId, authorName=form.author.data).fetchone().id
            maxId = 0
            getTableSize = text('SELECT * FROM comicbook')
            r = engine.execute(getTableSize)
            if r.first():
                getMaxId = text('SELECT MAX(id) AS id FROM comicbook')
                maxId = engine.execute(getMaxId).fetchone().id + 1
            print ('hello')
            print (maxId)
            engine.execute(insertComicBook, a = form.publisher.data, b = form.series.data, c = seriesUpper,
                          d = form.issueNum.data, e = form.primaryCharacter.data, f=form.primaryVillain.data, g = form.genre.data, h = authorId, i = maxId)
        #We know now that book must exist in database
        getBookId = text('SELECT comicbook.id FROM comicbook JOIN author on comicbook.authoredBy = author.id WHERE UPPER(name) = :a AND UPPER(series) = :x AND issueNum = :i AND publisher = :p')
        bookId = engine.execute(getBookId, a =form.author.data, x = form.series.data.upper(), i = form.issueNum.data, p = form.publisher.data).first().id
        userID = current_user.id
        now = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        insertListing = text('INSERT INTO Selling (price, date_posted, book, userID, cgc) VALUES (:p, :dp, :bo, :u, :c)')
        engine.execute(insertListing, p = form.price.data, dp = now, bo = bookId, u = userID, c = form.cgc.data)
       
            
        # Add user to the database
        #db.session.add(user)
        #db.session.commit()
    

        #connection.close()
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
        
        
        sql = text('SELECT series FROM comicbook JOIN author on comicbook.authoredBy = author.id WHERE UPPER(name) = :a AND UPPER(series) = :x AND issueNum = :i AND publisher = :p')
        
        result = connection.execute(sql, a = form.author.data.upper(), x = form.series.data.upper(), i = form.issueNum.data, p = form.publisher.data)
        row = result.fetchone()
        if (not row):
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
        getBookId = text('SELECT comicbook.id FROM comicbook JOIN author on comicbook.authoredBy = author.id WHERE UPPER(name) = :a AND UPPER(series) = :x AND issueNum = :i AND publisher = :p')
        bookId = connection.execute(getBookId, a =form.author.data.upper(),  x = form.series.data.upper(), i = form.issueNum.data, p = form.publisher.data).first().id
        userID = current_user.id
        now = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        updateListing = text('UPDATE selling SET price = :p, date_posted = :dp, book = :bo, userID = :u, cgc = :c WHERE selling.id= :si')
        connection.execute(updateListing, p = form.price.data, dp = now, bo = bookId, u = userID, c = form.cgc.data, si =sellID)
       
            
        # Add user to the database
        #db.session.add(user)
        #db.session.commit()
        #flash('Listing added')

        connection.close()
        return redirect(url_for('home.dashboard'))
        
    # listing not validated
    return render_template('listings/editListing.html', form=form, title='Edit Listing')

def ebayPrice(book,issueNum, cgc, value, year):
    item = book + ' ' + issueNum + ' cgc ' + cgc + ' ' + str(year);
    item_def = item.replace(' ','+')
    url = 'http://www.ebay.com/sch/i.html?_nkw={0}&_sacat=0'.format(item_def)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    print ("Retrieving %s"%(url))
    response = requests.get(url, headers=headers, verify=True)
    #parser = html.fromstring(response.text)
    #print(response.text)		
    page = urllib.request.urlopen(url)
    page_contents = str(page.read())
    #print(page_contents)
    idx = page_contents.find('"s-item__title" role="text">')
    #print(str(idx))
    sumPrice = 0
    count = 0
    str1 = ' ' + issueNum + ' '
    str2 = '#' + issueNum + ' '
    str3 = '# ' + issueNum + ' '
    while idx != -1:
        #page_contents = page_contents[idx + 28:len(page_contents)]
        #print(page_contents)
        idxEnd = page_contents.find('</h3>', idx + 28, len(page_contents))

        #print(str(idxEnd))
        title = page_contents[idx+28:idxEnd]
        title1 = title.upper()
        book1 = book.upper()
        if ((title.find(str1) == -1 and title.find(str2) == -1 and title.find('str3') == -1) or (title1.find(book1) == -1) and title1.find('REPRINT') != -1):
            page_contents = page_contents[idxEnd + 5: len(page_contents)]
            idx = page_contents.find('"s-item__title" role="text">')
            continue
        #print(title)
        page_contents = page_contents[idxEnd + 5: len(page_contents)]
        
        idxPriceStart = page_contents.find('class="s-item__price">$')
        idxPriceEnd = page_contents.find('.', idxPriceStart)
        price = page_contents[idxPriceStart + 23: idxPriceEnd]
        page_contents = page_contents[idxPriceEnd + 1:len(page_contents)]
        #print(str(len(title))+ ': ' + price)
        price = price.replace(',','')
        print (title, price)
        if (abs(int(price) - value) <= (value * .25)):
            sumPrice += int(price)
            count = count + 1;
        idx = page_contents.find('"s-item__title" role="text">')
    if (count == 0):
        return 'NA'
    print(str(sumPrice/count))         
    return '$' + str(int(sumPrice/count)) + '.00'
def otherPrice(book,issueNum, cgc):
    item = book + ' ' + issueNum# + ' cgc ' + cgc;
    item_def = item.replace(' ','+')
    url = 'https://comics.gocollect.com/guide/search?q='+item_def
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    print ("Retrieving %s"%(url))
    

    
@listings.route('/openListings/<int:sellID>',methods=['GET', 'POST'])
def openListings(sellID):
    engine = db.engine
    connection = engine.connect()
    

    sql = text('SELECT  comicbook.primaryCharacter, comicbook.primaryVillain, comicbook.authoredBy, comicbook.id, comicbook.series, comicbook.issueNum, comicbook.year, comicbook.genre, sell.price, sell.cgc, sell.id AS sellID FROM comicbook, (SELECT selling.id, selling.book, selling.price, selling.cgc FROM selling WHERE selling.id = :si) AS sell WHERE comicbook.id = sell.book')
    result= connection.execute(sql, si = sellID).fetchall()
    connection.close() 
    for _r in result:
        ebay = ebayPrice(_r.series, str(_r.issueNum), str(_r.cgc), _r.price, _r.year)
        newGenre = mlOutputGenre(_r.primaryCharacter, _r.primaryVillain, _r.authoredBy)
        #otherPrice(_r.series, str(_r.issueNum), str(_r.cgc))

    if current_user.is_authenticated:
        connection = engine.connect()
        user = current_user.id
        sql = text('UPDATE users SET favGenre = :g WHERE users.id = :u')
        connection.execute(sql, g = newGenre, u = user)
        connection.close()
        
    
    return render_template('listings/openListing.html', output1=result, output2 = ebay)
def getPopularSoldSelling():
    engine = db.engine
    connection = engine.connect()
    sql = text(
'SELECT s1.series, s1.issueNum, s1.cgc, s1.price, s1.sellID FROM (SELECT comicbook.series, comicbook.primaryCharacter, comicbook.issueNum, selling.cgc, '+
'selling.price, selling.id as sellID FROM comicbook JOIN selling on comicbook.id = selling.book) as s1, '+
'(SELECT comicbook.primaryCharacter, COUNT(*) FROM (comicbook JOIN sold ON comicbook.id = sold.book) GROUP BY comicbook.primaryCharacter '+
' ORDER BY(COUNT(*)) DESC LIMIT 5) as s2' +' WHERE s1.primaryCharacter = s2.primaryCharacter '+ 
'UNION ' +
'SELECT s3.series, s3.issueNum, s3.cgc, s3.price, s3.sellID FROM (SELECT comicbook.series, comicbook.primaryVillain, comicbook.issueNum, selling.cgc, ' +
'selling.price, selling.id as sellID FROM comicbook JOIN selling on comicbook.id = selling.book) as s3, '+
'(SELECT comicbook.primaryVillain, COUNT(*) FROM (comicbook JOIN sold ON comicbook.id = sold.book) GROUP BY comicbook.primaryVillain ' +
'ORDER BY(COUNT(*)) DESC LIMIT 5) as s4' +' WHERE s3.primaryVillain = s4.primaryVillain '+
'UNION ' +
'SELECT s5.series, s5.issueNum, s5.cgc, s5.price, s5.sellID FROM (SELECT comicbook.series, comicbook.primaryVillain, comicbook.primaryCharacter, '+
'comicbook.issueNum, selling.cgc, selling.price, selling.id as sellID FROM comicbook JOIN selling on comicbook.id = selling.book) as s5, '+
'(SELECT comicbook.primaryCharacter, comicbook.primaryVillain, COUNT(*) FROM (comicbook JOIN sold ON comicbook.id = sold.book) '+
 'GROUP BY comicbook.primaryVillain, comicbook.primaryCharacter ' +
'ORDER BY(COUNT(*)) DESC LIMIT 5) as s6' +' WHERE s5.primaryCharacter = s6.primaryCharacter AND s5.primaryVillain = s6.primaryVillain'
)
    result = connection.execute(sql).fetchall()
    connection.close()
    return result

@listings.route('/popularSold', methods=['GET', 'POST'])
def popularSold():
    #engine = db.engine
    #connection = engine.connect()
    #sql = text(
#'SELECT s1.series, s1.issueNum, s1.cgc, s1.price, s1.sellID FROM (SELECT comicbook.series, comicbook.primaryCharacter, comicbook.issueNum, selling.cgc, '+
#'selling.price, selling.id as sellID FROM comicbook JOIN selling on comicbook.id = selling.book) as s1, '+
#'(SELECT comicbook.primaryCharacter, COUNT(*) FROM (comicbook JOIN sold ON comicbook.id = sold.book) GROUP BY comicbook.primaryCharacter'+
#' ORDER BY(COUNT(*)) DESC LIMIT 5) as s2' +' WHERE s1.primaryCharacter = s2.primaryCharacter')
    
    result = getPopularSoldSelling()
    for _r in result:
        print(_r.series + ', #' +str(_r.issueNum)) 
    #connection.close()
    return render_template('listings/recommendedListings.html', output1=result)

@listings.route('/machineLearning', methods=['GET', 'POST'])
def machineLearning():
    #engine = db.engine
    #connection = engine.connect()
    #sql = text(
#'SELECT s1.series, s1.issueNum, s1.cgc, s1.price, s1.sellID FROM (SELECT comicbook.series, comicbook.primaryCharacter, comicbook.issueNum, selling.cgc, '+
#'selling.price, selling.id as sellID FROM comicbook JOIN selling on comicbook.id = selling.book) as s1, '+
#'(SELECT comicbook.primaryCharacter, COUNT(*) FROM (comicbook JOIN sold ON comicbook.id = sold.book) GROUP BY comicbook.primaryCharacter'+
#' ORDER BY(COUNT(*)) DESC LIMIT 5) as s2' +' WHERE s1.primaryCharacter = s2.primaryCharacter')
    
    result = getPopularSoldSelling()
    for _r in result:
        print(_r.series + ', #' +str(_r.issueNum))
    if current_user.is_authenticated:
        user = current_user.id
    engine = db.engine
    connection = engine.connect()
    sql = text('SELECT users.favGenre FROM users WHERE users.id = :u')
    result_genre = connection.execute(sql, u = user).fetchall()
    connection.close()
    for _r in result_genre:
        genre = _r.favGenre
    print(genre)
    if genre is None:
        print('changing genre')
        genre = 'action'
    result2 = mlOutputBooks(genre)
    return render_template('listings/recommendedListings.html', output1=result, output2 = result2)
@listings.route('/buyListings/<int:sellID>',methods=['GET', 'POST'])
def buyListings(sellID):
    engine = db.engine
    connection = engine.connect()
    if current_user.is_authenticated:
        user = current_user.id
        
    now = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    sql = text('SELECT selling.price, selling.userID, selling.book, selling.cgc FROM selling WHERE selling.id = :s')
    result = connection.execute(sql, s = sellID).fetchone()
    sql = text('INSERT INTO sold (priceSold, dateSold, userID, book, cgc) VALUES (:p, :d, :u, :b, :c)')
    
    connection.execute(sql, p = result.price, d = now, u = result.userID, b = result.book, c = result.cgc)
    sql = text('DELETE FROM selling WHERE selling.id = :z')
    connection.execute(sql, z = sellID)
    return redirect(url_for('listings.allListings'))

