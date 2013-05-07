import sqlite3
import sys

#####################################################################
# Retrieves the subreddits we have submissions for in the database
# ###################################################################

# returns a dict of subreddit names -> num of submissions
def getSubredditCounts():
    conn = sqlite3.connect("merge.sqlite")
    c = conn.cursor()
    c.execute("select subreddit from Submission")
    submissions = c.fetchall()
    c.close()
    conn.close()
    
    srCount = {} # hash of subreddit names to number of submissions
    for sub in submissions:
        if sub[0] not in srCount:
            srCount[sub[0]] = 1
        else:
            srCount[sub[0]] += 1
    return srCount
    
# main script
def main():
    srCount = getSubredditCounts()
    for key in sorted(srCount.keys()):
        print key, srCount[key]
        
    print "Total subreddits:", len(srCount.keys())
        
if __name__ == "__main__":
    main()
