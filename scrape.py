# attempts to scrape data from a given subreddit, save it to database
import praw
import sys
import sqlite3

# read in command-line arguments
if len(sys.argv) != 3:
    sys.exit("Must provide subreddit name, number of posts to retrieve")
subreddit = sys.argv[1]
fetchLimit = int(sys.argv[2])

# open the database connection
#conn = sqlite3.connect(sys.argv[3])
conn = sqlite3.connect("merge.sqlite")
c = conn.cursor()

# create the user-agent
userAgent = "Bot retrieving post/comment data for analysis, by /u/AspiringGeodudeMode"
r = praw.Reddit(user_agent=userAgent)

# fetch the given number of submissions from the given subreddit
submissions = r.get_subreddit(subreddit).get_hot(limit=fetchLimit)

# keep a list of unique submission IDs already in the database
c.execute('select id from Submission')
submissionIDs = []
for row in c.fetchall():
    submissionIDs.append(row[0])

counter = 0
for submission in submissions:
    counter += 1

    # no point saving the submission if the author is unknown
    if not submission.author:
        continue

    # check for duplicates
    if submission.id in submissionIDs:
        continue

    # add the submission data to the database
    subData = [submission.id, str(submission.author), submission.score, str(submission.subreddit)]
    c.execute("""insert into Submission(id, author, score, subreddit) values (?, ?, ?, ?);""", subData)
    submissionIDs.append(submission.id)

    # expand all comment threads
    submission.replace_more_comments(limit=None)
    
    # flatten the comment tree into a list
    comments = praw.helpers.flatten_tree(submission.comments)
    for comment in comments:
        if not comment.author:
            continue
        level = 1
        if comment.is_root:
            level = 0
        commData = [comment.id, str(comment.author), comment.score, level, comment.parent_id, submission.id, str(submission.subreddit)]
        c.execute("""insert into Comment(id, author, score, level, parent, submissionID, subreddit) values (?, ?, ?, ?, ?, ?, ?);""", commData)

    conn.commit()
    print "Added submission " + str(submission.id) + " and " + str(len(comments)) + " comments (" + str(counter) + " of " + str(fetchLimit) + ")"
    

# close the database connection
conn.commit()
c.close()
conn.close()
