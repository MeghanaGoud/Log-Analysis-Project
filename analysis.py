# !/usr/bin/env python3

import psycopg2


def connect(DB_NAME = "news"):
    try:
        db = psycopg2.connect("dbname={}".format(DB_NAME))
        cursor = db.cursor()
        return db, cursor
    except:
        print("<error message>")


def top_three_articles():
    print('What are the most popular three articles of all time?')
    query_1 = """SELECT articles.title, count(log.path) as \
                    views FROM articles, log WHERE \
                    log.path=('/article/' || articles.slug)\
                    GROUP BY articles.title ORDER BY views desc limit 3"""
    cursor.execute(query_1)
    data = cursor.fetchall()
    for row in data:
        print ("%s -- %s views" % (row[0], row[1]))


def popular_authors():
    print('Who are the most popular article authors of all time?')
    query_2 = """SELECT authors.name, count(log.path) as views FROM\
                 articles, log, authors\
                 WHERE log.path=('/article/'||articles.slug)\
                 AND articles.author = authors.id \
                 GROUP BY authors.name ORDER BY views desc"""
    cursor.execute(query_2)
    data = cursor.fetchall()
    for row in data:
        print("%s -- %s" % (row[0], row[1]))


def error_percentage():
    print('On which days did more than 1% of requests lead to errors?')
    query_3 = """SELECT to_char(errors.date, 'Month DD, YYYY'),\
                 round((errors.errors*1.0/request.requests*1.0)*100,3)\
                 as percent FROM errors, request \
                 WHERE errors.date = request.date
                 AND (errors.errors*1.0 / request.requests*1.0)*100 > 1
                 ORDER BY percent desc; """
    cursor.execute(query_3)
    data = cursor.fetchall()
    for row in data:
        print("%s -- %s%% errors" % (row[0], row[1]))
    db.close()

if __name__ == '__main__':
    top_three_articles()
    popular_authors()
    error_percentage()


