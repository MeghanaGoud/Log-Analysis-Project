import psycopg2

DBNAME = "news"
db = psycopg2.connect(database=DBNAME)


def top_three_articles():
    print('What are the most popular three articles of all time?')
    cur = db.cursor()
    query_1 = """SELECT articles.title, count(log.path) as \
                    views from articles, log where \
                    log.path=('/article/' || articles.slug)\
                    group by articles.title order by views desc limit 3"""
    cur.execute(query_1)
    data = cur.fetchall()
    for row in data:
        print ("%s -- %s views" % (row[0], row[1]))


def popular_authors():
    print('Who are the most popular article authors of all time?')
    cur = db.cursor()
    query_2 = """SELECT authors.name, count(log.path) as views from\
                 articles, log, authors\
                 where log.path=('/article/'||articles.slug)\
                 and articles.author = authors.id \
                 group by authors.name order by views desc"""
    cur.execute(query_2)
    data = cur.fetchall()
    for row in data:
        print("%s -- %s" % (row[0], row[1]))


def error_percentage():
    print('On which days did more than 1% of requests lead to errors?')
    cur = db.cursor()
    query_3 = """SELECT to_char(errors.date, 'Month DD, YYYY'),\
                 round((errors.errors*1.0/request.requests*1.0)*100,3)\
                 as percent from errors, request \
                 WHERE errors.date = request.date
                 and (errors.errors*1.0 / request.requests*1.0)*100 > 1
                 ORDER BY percent desc; """
    cur.execute(query_3)
    data = cur.fetchall()
    for row in data:
        print("%s -- %s%% errors" % (row[0], row[1]))
    db.close()

if __name__ == '__main__':
    top_three_articles()
    popular_authors()
    error_percentage()
