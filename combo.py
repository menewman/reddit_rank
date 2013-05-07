# calculates a weighted interpolation of PageRank, HITS scores and
#     saves it back to the database
import sqlite3
import sys

# can take an argument for alpha, the weight of PageRank vs HITS
alpha = 0.5
if len(sys.argv) == 2:
    alpha = float(sys.argv[1])

conn = sqlite3.connect("merge.sqlite")
conn.text_factory = str
c = conn.cursor()

c.execute("select * from Rank")
rows = c.fetchall()
for row in rows:
    combo_score = alpha*row[1] + (1-alpha)*row[3]
    c.execute("UPDATE Rank set combo_score=? WHERE username=?",
        (float(combo_score), row[0]))
    
conn.commit()
c.close()
conn.close()

print "combo_score updated: alpha=" + str(alpha)
