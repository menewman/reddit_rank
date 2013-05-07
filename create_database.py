# creates a SQLite database to store user, submission, comment data
import sqlite3
import sys

# read in command-line arguments
if len(sys.argv) != 2:
    sys.exit("Must provide database name.")
dbName = sys.argv[1]

db = sqlite3.connect(dbName)
db.execute("CREATE TABLE IF NOT EXISTS User(username text primary key, linkScore integer, commentScore integer);")
db.execute("CREATE TABLE IF NOT EXISTS Submission(id text primary key, author text, score integer, subreddit text);")
db.execute("CREATE TABLE IF NOT EXISTS Comment(id text primary key, author text, score integer, level integer, parent text, submissionID text, subreddit text, foreign key (parent) references Comment(id), foreign key (submissionID) references Submission(id));")
db.execute("CREATE TABLE IF NOT EXISTS Rank(username text primary key, page_score real, page_rank real, hits_score real, hits_rank real, combo_score real, combo_rank real, foreign key (username) references User(username));")

db.commit()
db.close()
