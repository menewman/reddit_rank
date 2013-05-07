# functions that implement the HITS algorithm
#
# current command-line args: iterations, beta, subreddit1, subreddit2...
from directed_graph import Dgraph
import sqlite3
import sys
from math import sqrt

auth = {} # authority scores
hub = {}  # hub scores

# initialize authority and hub scores
def initialize_scores(d_graph):
    for i in range(max(d_graph.nodes)+1):
        auth[i] = 1
        hub[i] = 1

# authority update rule
def update_authority(d_graph):
    sum_squares = 0
    for node in d_graph.nodes:
        edges_in = d_graph.get_edges_to(node)
        auth[node] = 0
        for e in edges_in:
            auth[node] += hub[e]
        sum_squares += auth[node] * auth[node]
    n = sqrt(sum_squares) # normalizing factor
    for node in d_graph.nodes:
        auth[node] /= n

# hub update rule
def update_hub(d_graph):
    sum_squares = 0
    for node in d_graph.nodes:
        edges_out = d_graph.get_edges_from(node)
        hub[node] = 0
        for e in edges_out:
            hub[node] += auth[e]
        sum_squares += hub[node] * hub[node]
    n = sqrt(sum_squares) # normalizing factor
    for node in d_graph.nodes:
        hub[node] /= n

# run HITS on the given graph for the given number of steps
def run_hits(d_graph, T):
    initialize_scores(d_graph)
    for t in range(T):
       update_authority(d_graph) 
       update_hub(d_graph)
       #print "Iteration:", t+1

def main():
    if len(sys.argv) < 4:
        sys.exit("Error: Not enough arguments. Please give iterations and subreddit(s).")

    # beta is used to weigh the values of authority/hub scores
    #beta = 0.0
    beta = float(sys.argv[2])
    print 'beta: ', beta
    
    srNames = []
    for i in range(2, len(sys.argv)):
        srNames.append(sys.argv[i])

    conn = sqlite3.connect("merge.sqlite")
    conn.text_factory = str
    c = conn.cursor()
    d_graph = Dgraph(c, srNames)

    run_hits(d_graph, int(sys.argv[1]))

    # update table
    for node in d_graph.nodes:
        score = (1.0 - beta)*auth[node] + beta*hub[node]
        #score = (1.0 - beta)*auth[node] - beta*hub[node]
        c.execute("UPDATE Rank set hits_score=? WHERE username=?",
            (float(score), d_graph.getUsername(node)))
            
    conn.commit()
    c.close()
    conn.close()
    
if __name__ == "__main__":
    main()
