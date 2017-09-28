# Log Analysis Project
Building an informative summary from logs, using python and psql that prints out reports (in plain text) based on the data in the database, using the psycopg2 module to connect to the database
## Getting started
These instructions will help you to run the project on your local computer. See deployment for notes on how to deploy the project on a live system 
## Prerequisites
Install virtual machine(vagrant), download the newsdata.sql file and psycopg2
### Installation and Execution
This project makes use of the Linux-based virtual machine (VM). This will give you the PostgreSQL database and support software needed for this project, use tools called Vagrant and VirtualBox to install and manage the VM. VirtualBox is the software that actually runs the virtual machine download it https://www.virtualbox.org/wiki/Downloads
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem download it https://www.vagrantup.com/downloads.html
After the successful installation of vagrant run 
```
Vagrant --version
Vagrant 1.9.8
```
after that download the VM configuration and navigate to your vagrant directory using `cd`. Inside the vagrant directory, run the command `vagrant up`. This will cause Vagrant to download the Linux operating system and install it. 
When `vagrant up` is finished running, run `vagrant ssh` to log in to your newly installed Linux VM!
```
The shared directory is located at /vagrant
To access your shared files: cd /vagrant
Last login: Thu Sep 28 05:50:54 2017 from 10.0.2.2
vagrant@vagrant:~$
``` 
navigate to your vagrant by `cd /vagrant` you'll get the command line like
```
vagrant@vagrant:~$ cd /vagrant
vagrant@vagrant:/vagrant$
```
after that install the required python libraries psycopyg2(used to connect to the database). To install pip package in ubuntu try the given commands
```
sudo easy_install pip
	or
sudo apt-get install python-pip
```
it’s better to use sudo while installing any packages in ubuntu instead of `pip install psycopg2` use `sudo pip install psycopg2`
#### Download and load the data
Put newsdata.sql file into the vagrant directory, which is shared with our virtual machine. To load the data, cd into the vagrant directory and use the command 
```
psql -d news -f newsdata.sql
```
from the above command -d is used to connect to the database as `-d news`, -f is used to run the SQL statements in the file `-f newsdata.sql`. After loading the data in to our database we can connect to our database as mentioned `psql -d news or psql news`.
to list out the tables use \dt
```
news-> \dt
          List of relations
 Schema |   Name   | Type  |  Owner
--------+----------+-------+---------
 public | articles | table | vagrant
 public | authors  | table | vagrant
 public | log      | table | vagrant
(3 rows)
```
to list out particular table rows and columns use \d table
```
news-> \d authors
                         Table "public.authors"
 Column |  Type   |                      Modifiers
--------+---------+------------------------------------------------------
 name   | text    | not null
 bio    | text    |
 id     | integer | not null default nextval('authors_id_seq'::regclass)
Indexes:
    "authors_pkey" PRIMARY KEY, btree (id)
Referenced by:
    TABLE "articles" CONSTRAINT "articles_author_fkey" FOREIGN KEY (author) REFERENCES authors(id)
```
similarly check for `\d articles, \d log`, after successfully loading data try to extract data from the database try some basic queries. Use ctrl+D to come out of it
#### Procedure
open a new python file in the vagrant directory save it as analysis.py and import psycopg2 module `import psycopg2` and after that use the .connect() to connect to our database
```
DBNAME = "news"
db = psycopg2.connect(database=DBNAME)
```
And create 3 different procedures for our requirement, define a cur to use it as a connecting object, .execute() to execute our query and .fetchall() to fetch all the rows and after print our required data and close the connection using .close() 
```cur = db.cursor()
   cur.execute(query)
   data = cur.fetchall()
   for row in data:
   		print(row[0], row[1])	#row[0] the count depends upon our columns 
   db.close()
```
As the program execution starts from main use the below commands or we can simply call our required function `top_three_articles()`
```
if __name__=='__main__':
    top_three_articles()
    popular_authors()
    error_percentage()
```
From the first query
``` 
query_1 = """SELECT articles.title, count(log.path) as views \
             from articles, log where log.path=('/article/' || articles.slug) \
             group by articles.title order by views desc limit 3"""
```
here we use `log.path=('/article/' || articles.slug)` we are concatenating both /article/ with articles.slug and comparing it with the log.path and if they are true then count them based on this(as views) and grouping them by articles.title(`i.e, for xxx-xxx title we got 234 views(we get it from count(log.path)`)) and order by max numbers of views at top by `desc` and limit to first 3.
Second query
```
query_2 = """select authors.name, count(log.path) as views from \
             articles, log, authors \
             where log.path=('/article/'||articles.slug) \
             and articles.author = authors.id \
             group by authors.name order by views desc"""
```
second query is similar to our first one but addition to that we added one more condition `artciles.author = authors.id` if true then return the authors name as well as views
Third query
To answer this we need total requests per day and total errors occurred on that particular day
by using `(errors/totalrequests)*100` so create 2 views for these two.
For easy accessing we created views here lets create a view to show  number of errors on each day this can be done by using status and time columns in log table if `status = 404 NOT FOUND` count it as an error
```
create view errors as 
	SELECT date_trunc('day', time)"date",
	count(status) as errors
	FROM log
	WHERE status = '404 NOT FOUND'
	GROUP BY date;
```
The `date_trunc` function truncates a TIMESTAMP or an INTERVAL value based on a specified date part e.g., hour, week, or month and returns the truncated timestamp or interval with a level of precision. `count(status) as errors` counts only when status is 404, check the below example
```
select date_trunc('day', time);
       date_trunc
------------------------
 2015-12-15 00:00:00+02
(1 row)
```
create a view to show total number of requests on each day this can be done by using status and time column in log table
```
create view request as 
	SELECT date_trunc('day', time)"date",
	count(status) as requests
	FROM log
	GROUP BY date;
```
Now we have created our required views after that just these in our database now coming to 3rd query 
```
query_3 = """SELECT to_char(errors.date, 'Month DD, YYYY'), \
             round((errors.errors*1.0/request.requests*1.0)*100,3) \
             as percent from errors, request \
             WHERE errors.date = requests.date \
             and (errors.errors*1.0 / request.requests*1.0)*100 > 1 \
             ORDER BY percent desc; """
```
here PostgreSQL to_char function converts a number or date to a string. Check the below example
```
SELECT to_char(date '2014-04-25', 'YYYY/MM/DD');
  to_char
------------
 2014/04/25
(1 row)
```
if we want the month date and year we can get it by changing th format
```
SELECT to_char(date '2014-04-25', 'Month DD, YYYY');
    to_char
--------------------
 April     25, 2014
(1 row)
```
and round function is used to roundoff the result to particular digits here we used `round((errors.errors*1.0/requests.requests*1.0)*100,3)` simply round(x/y, 3) roundoff to 3 digits and 
`(errors.errors*1.0 / requests.requests*1.0)*100 > 1` is used to know the errors >1 and day when maximum erorrs occured
#### Run the program
save your file open your vm and type python analysis.py it runs your python program  we’ll get the list of outputs, check the output.txt file for results.
