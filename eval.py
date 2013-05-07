# evaluation metrics
# current main script takes a subreddit name as input, outputs
#     sorted lines of users and their karma within that subreddit

import sqlite3
import sys
from scipy.stats import spearmanr

# given username and subreddit strings, find user's karma within the subreddit
def findUserKarma(username, subreddit, cursor):
    totalKarma = 0

    # select submissions where author=username and subreddit=subreddit
    cursor.execute('select score from Submission where subreddit=? and author=?', (subreddit, username))
    submissions = cursor.fetchall()
    for sub in submissions:
        totalKarma += sub[0]

    # select comments where author=username and subreddit=subreddit
    cursor.execute('select score from Comment where subreddit=? and author=?', (subreddit, username))
    comments = cursor.fetchall()
    for comment in comments:
        totalKarma += comment[0]

    return totalKarma

# return a dict of usernames:karma for a particular subreddit
def findSubKarma(subreddit, cursor):
    # retrieve usernames
    cursor.execute('select username from User')
    users = cursor.fetchall()
    
    # initialize mapping of users->karma
    userKarma = {}
    for user in users:
        userKarma[user[0]] = 0
    
    # retrieve comments
    cursor.execute('select author, score from Comment where subreddit=?', [subreddit,])
    comments = cursor.fetchall()
    for comment in comments:
        userKarma[comment[0]] += comment[1]
        
    # retrieve submissions
    cursor.execute('select author, score from Submission where subreddit=?', [subreddit,])
    submissions = cursor.fetchall()
    for sub in submissions:
        userKarma[sub[0]] += sub[1]
        
    return userKarma

# return a dict of usernames:karma for multiple subreddits
def findSubKarma(subreddits, cursor):
    # retrieve usernames
    cursor.execute('select username from User')
    users = cursor.fetchall()

    # initialize mapping of users->karma
    userKarma = {}
    for user in users:
        userKarma[user[0]] = 0

    # retrieve comments
    cursor.execute('select author, subreddit, score from Comment')
    comments = cursor.fetchall()
    for comment in comments:
        if comment[1] in subreddits:
            userKarma[comment[0]] += comment[2]

    # retrieve submissions
    cursor.execute('select author, subreddit, score from Submission')
    submissions = cursor.fetchall()
    for sub in submissions:
        if sub[1] in subreddits:
            userKarma[sub[0]] += sub[2]

    return userKarma

# uses the Kendell-Tau algorithm to compare rankings
# as input, takes sorted dicts of username:rank
# as output, prints a single float
def kendellTau(dict1, dict2):
    if len(dict1) != len(dict2):
        sys.exit("Error: cannot compare rankings of different size.")

    # naive direct computation (replace with bubble-sort alg?)
    n = 0
    for i in range(len(dict1)):
        for j in range(i):
            n += n + sign(dict1[i]-dict1[j]) * sign(dict2[i]-dict2[j])
    return n
    
# runs the Spearman algorithm on two dicts
# returns list with (correlation coeff, 2-tailed p-value)
def spearman(dict1, dict2):
    if len(dict1) != len(dict2):
        sys.exit("Error: cannot compare rankings of different size.")      
    list1 = []
    list2 = []
    for key in dict1.keys():
        list1.append(dict1[key])
        list2.append(dict2[key])
    results = spearmanr(list1, list2)
    return results
    
# retrieves a dict of username:combo_score
def get_combo_score(cursor):
    cursor.execute('select username, combo_score from Rank')
    rows = cursor.fetchall()
    combo_ranks = {}
    for row in rows:
        combo_ranks[row[0]] = row[1]
    return combo_ranks

# main script
def main():
    if len(sys.argv) < 2:
        sys.exit("Not enough args: please provide subreddit name(s)")

    conn = sqlite3.connect("merge.sqlite")
    conn.text_factory = str
    c = conn.cursor()
    
    uk = findSubKarma(sys.argv[1:], c)
    myRanks = get_combo_score(c)
    c.close()
    conn.close()
    """
    sortedList = list(sorted(uk, key=uk.__getitem__, reverse=True))
    for key in sortedList:
        print key, uk[key]
    """
    spear_results = spearman(myRanks, uk)
    print "Spearman rank:", spear_results[0]
    print "p-value:      ", spear_results[1]
        
if __name__ == "__main__":
    main()
