import pandas as pd
import math

def ML():
    comicbook = readComicbook()

    genre = naiveBayesFindGenre(comicbook)

    books = randomSelectBooks(genre)

    return books

def readComicbook():
    # connect to the database
    config = {
        'user': 'ba4f284f7d53c5',
        'password': 'ff337ef1',
        'host': 'us-cdbr-iron-east-03.cleardb.net',
        'database': 'heroku_ac9d5074a62e26f',
        'raise_on_warnings': True
    }

    cnx = mysql.connector.connect(**config)

    # initialize cursor
    # mycursor = cnx.cursor()
    #
    # genre = 'mystery'
    # # # SQL query (replace * with column attribute(s))
    # sql = ("SELECT * FROM comicbook WHERE genre = (:g)")
    # #
    # # # execute SQL query
    # mycursor.execute(sql, g = genre)
    # #
    # myresult = mycursor.fetchall()
    #
    # for x in myresult:
    # 	print(x)

    # query the table and put it in a dataframe
    df = pd.read_sql('SELECT * FROM comicbook', con = cnx)
    cnx.close()
    return df

def randomSelectBooks(genre):
    # connect to the database
    config = {
        'user': 'ba4f284f7d53c5',
        'password': 'ff337ef1',
        'host': 'us-cdbr-iron-east-03.cleardb.net',
        'database': 'heroku_ac9d5074a62e26f',
        'raise_on_warnings': True
    }

    cnx = mysql.connector.connect(**config)

    # join with the selling table using attributes 'comicbook.id = selling.book'
    sql = "SELECT * FROM comicbook INNER JOIN selling ON comicbook.id = selling.book WHERE genre = '%s'" % genre

    books = pd.read_sql(sql, con = cnx)

    cnx.close()

    # Randomly select 5 books from Books
    numBooks = books.shape[0]

    n = 5
    if n > numBooks:
        n = numBooks

    randomBooks = books.sample(n=n, random_state=1)

    # return the five books
    return randomBooks

def naiveBayesFindGenre(comicbook):
    # import searched data array
    # test information hard coded for now
    search = pd.Series(['Batman','Hush','12'],['primaryCharacter','primaryVillain','authoredBy'])
    character = search['primaryCharacter']
    villain = search['primaryVillain']
    author = search['authoredBy']

    w = 3 # number of features
    h = 6 # number of labels

    prob_table = [[0 for x in range(w)] for y in range (h)]# 2d matrix |genre| x 3, rows mean specific genre, columns mean P(char/genre), P(villain/genre), P(author/genre)
    genre_count = [0 for x in range(h)]#<- 1d array it keeps count of each genre
    #action: 0
    #horror: 1
    #adventure: 2
    #comedy: 3
    #mystery: 4
    #scifi: 5
    for index, book in comicbook.iterrows():
        if book['genre'] == 'action':
            genre_count[0] += 1
            prob_table = updateCount(book, prob_table, character, villain, author, 0)
        elif book['genre'] == 'horror':
            genre_count[1] += 1
            prob_table = updateCount(book, prob_table, character, villain, author, 1)
        elif book['genre'] == 'adventure':
            genre_count[2] += 1
            prob_table = updateCount(book, prob_table, character, villain, author, 2)
        elif book['genre'] == 'comedy':
            genre_count[3] += 1
            prob_table = updateCount(book, prob_table, character, villain, author, 3)
        elif book['genre'] == 'mystery':
            genre_count[4] += 1
            prob_table = updateCount(book, prob_table, character, villain, author, 4)
        elif book['genre'] == 'scifi':
            genre_count[5] += 1
            prob_table = updateCount(book, prob_table, character, villain, author, 5)

    # k = 1 # smoothing factor for Laplace Smoothing, choose between 0.1 - 10
    for i in range(0, 6):
        for j in range(0, 3):
            prob_table[i][j] = float(prob_table[i][j]) / float(genre_count[i])

    total_count = sum(genre_count)
    genre_prob = [float(x) / float(total_count) for x in genre_count]
    genre_prob_avg = float(sum(genre_prob))/len(genre_prob)

    Bayes_table = [0 for x in range(h)] # <- 1d array where index means genre and entries mean the probabilities.

    for i in range(0, h):
        Bayes_table[i] = math.log(genre_prob[i])
        for j in range(0, w):
            if prob_table[i][j] == 0:
                Bayes_table[i] += math.log(genre_prob_avg/w)
            else:
                Bayes_table[i] += math.log(prob_table[i][j])

    genre_idx = Bayes_table.index(max(Bayes_table))

    genre = findGenre(genre_idx)

    return genre

def updateCount(book, table, character, villain, author, genre_idx):
    if book['primaryCharacter'] == character:
        table[genre_idx][0] += 1
    elif book['primaryVillain'] == villain:
        table[genre_idx][1] += 1
    elif book['authoredBy'] == author:
        table[genre_idx][2] += 1
    return table

def findGenre(genre_idx):
    if genre_idx == 0:
        return 'action'
    elif genre_idx == 1:
        return 'horror'
    elif genre_idx == 2:
        return 'adventure'
    elif genre_idx == 3:
        return 'comedy'
    elif genre_idx == 4:
        return 'mystery'
    elif genre_idx == 5:
        return 'scifi'
