# checks for submission, comment authors; saves their info to database
import praw
import sys
import sqlite3

#if len(sys.argv) != 2:
#    sys.exit('Must provide database name')

#conn = sqlite3.connect(sys.argv[1])
conn = sqlite3.connect("merge.sqlite")
c = conn.cursor()

userAgent = "Bot retrieving user data for analysis, by /u/AspiringGeodudeMode"
r = praw.Reddit(user_agent=userAgent)

# fetch the authors from all submissions, comments
users = []
c.execute('select author from Submission')
for row in c.fetchall():
    users.append(row[0])
c.execute('select author from Comment')
for row in c.fetchall():
    users.append(row[0])
users = list(set(users))

# fetch a list of users already indexed
existing = []
c.execute('select username from User')
for row in c.fetchall():
    existing.append(row[0])

users = [x for x in users if x not in existing]
numMissing = len(users)
counter = 0
for user in users:
    print "Retrieving", user # DEBUG
    redditor = r.get_redditor(user)
    userData = [user, redditor.link_karma, redditor.comment_karma]
    c.execute("insert into User(username, linkScore, commentScore) values (?, ?, ?);", userData)
    c.execute("insert into Rank(username) values (?);", (user,))
    conn.commit()
    counter += 1
    print "Added user", user, "(" + str(counter), "of", str(numMissing) + ")"

conn.commit()
c.close()
conn.close()
