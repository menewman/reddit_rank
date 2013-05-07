# functions that implement the PageRank algorithm
import sqlite3
import random
import numpy
import sys
from operator import itemgetter
from directed_graph import Dgraph

# Moves one step in PageRank algorithm (web g, param s).
# Applies matrix M to vector p and returns resulting vector.
# source: http://michaelnielsen.org/blog/using-your-laptop-to-
#             compute-pagerank-for-millions-of-webpages/
def step(g,p,s=0.85):
  n = max(g.nodes)+1
  v = numpy.matrix(numpy.zeros((n,1)))/len(g.nodes)
  inner_product = sum([p[j] for j in g.sinks])
  for j in xrange(n):
  	total_links = 0
  	for k, weight in g.get_edges_to(j):
  	  total_links += p[k] * weight;
  	v[j] = s * total_links
  	v[j] += s*inner_product/n+(1-s)/n
  return v/numpy.sum(v)

# Returns PageRank vector for web g, param s.
def pagerank(g,s=0.85, numSteps=10):
  n = max(g.nodes)+1
  p = numpy.matrix(numpy.ones((n,1)))/len(g.nodes)
  iteration = 1
  change = 2
  while iteration <= numSteps:
    print "Iteration: %s" % iteration
    new_p = step(g,p,s)
    change = numpy.sum(numpy.abs(p-new_p))
    p = new_p
    iteration += 1
  return p

def main():
    if len(sys.argv) < 3:
        sys.exit("Error: Not enough arguments. Please give iterations and subreddit(s).")
    max_rounds = int(sys.argv[1])
        
    # save the subreddit names
    srNames = []
    for i in range(2, len(sys.argv)):
        srNames.append(sys.argv[i])

    # setup
    conn = sqlite3.connect("merge.sqlite")
    conn.text_factory = str
    c = conn.cursor()

    # create graph
    graph = Dgraph(c, srNames)

    # execute PageRank algorithm	
    pr = pagerank(graph, 0.85, max_rounds)

    i = 0
    for node in graph.nodes:
        score = pr[i]
        c.execute("UPDATE Rank set page_score=? WHERE username=?",
                    (float(score), graph.getUsername(node)))
        i += 1

    conn.commit()
    
if __name__ == "__main__":
    main()
