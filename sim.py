# includes functions that are helpful for calculating similarity scores
import sqlite3
import sys

# given a string representing a subreddit name, returns list of users
# who have posted in that subreddit
def findUsersBySubreddit(srName):
    conn = sqlite3.connect("merge.sqlite")
    conn.text_factory = str
    c = conn.cursor()

    users = []

    c.execute('select author from Submission where subreddit=?', (srName,))
    submissions = c.fetchall()
    for submission in submissions:
        # find the author, add if not already in users
        if submission[0] is not None:
            users.append(submission[0])

    c.execute('select author from Comment where subreddit=?', (srName,))
    comments = c.fetchall()
    for comment in comments:
        # find author, add if not already in users
        if comment[0] is not None:
            users.append(comment[0])

    users = list(set(users))

    # print a warning if nothing was found
    if (len(users) == 0):
        print "No submissions found in this subreddit: " + srName

    conn.commit()
    c.close()
    conn.close()

    return users

# given two subreddit name strings, find the proportion of shared/total users
def findOverlap(sr1, sr2):
    users1 = findUsersBySubreddit(sr1)
    users2 = findUsersBySubreddit(sr2)

    totalUserSet = list(set(users1 + users2))
    totalSize = len(totalUserSet)
    sharedCount = 0.0
    for user in totalUserSet:
        if user in users1 and user in users2:
            sharedCount += 1.0
    return (sharedCount/totalSize)

# main script
# currently just a test
def main():
    if len(sys.argv) == 3:
        srname1 = sys.argv[1]
        srname2 = sys.argv[2]
        print findOverlap(srname1, srname2)
    else:
        sys.exit("Please provide the two subreddits to compare")

if __name__ == "__main__":
    main()
