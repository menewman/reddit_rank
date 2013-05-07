# implements a directed graph as a dictionary where each key:value
# pair represents a node and a list of nodes to which it has edges

# it is possible for a node to have multiple edges running to
# a single other node (edges are not unique)
import sqlite3
import sys

# normalizes the edges in list 'a' of [node, score] pairs
def normalize(a):
    total = 0.0
    for pair in a:
        total += pair[1]
    try:
        for i in range(len(a)):
            a[i][1] = float(a[i][1]) / total
    except Exception as e: # occasionally, the total is 0
        a[0][1] = 1.0
    return a

class Dgraph:
    # initialize an empty graph
    # params: database cursor, list of subreddits to consider
    def __init__(self, cursor, srNames):
        self.edges_in = {}
        self.edges_out = {}
        self.usernameMap = {}
        self.nodeMap = {}
        
        # keep a list of node IDs, a dict of node IDs to usernames
        self.nodes = set()
        cursor.execute('select username from User')
        counter = 0
        for row in cursor.fetchall():
            self.nodes.add(counter)
            self.usernameMap[counter] = row[0]
            self.nodeMap[row[0]] = counter
            counter += 1
            
        # add edges
        cursor.execute('select author, level, parent, submissionID, subreddit, score from Comment')
        rows = cursor.fetchall()
        for row in rows:
            # skip this row if it's not in the approved list of subreddits
            if row[4] not in srNames:
                continue
            # if not a top-level comment, find the parent's author
            if row[1] != 0:
                # make sure that parent authors exists
                #if row[0] is not None and row[2] is not None:
                if (row[0] != "None") and (row[2] != "None"):
                    parentComment = row[2][3:]
                    cursor.execute('select author from Comment where id=?', [parentComment,])
                    parentRow = cursor.fetchone()
                    if parentRow is not None:
                        parentAuthor = parentRow[0]
                        if (parentAuthor != "None"):
                            self.add_edge(self.nodeMap[row[0]], self.nodeMap[parentAuthor], row[5])
            # for a top-level comment, add edge to submission's author
            elif row[1] == 0:
                cursor.execute('select author from Submission where id=?', [row[3],])
                subAuthor = cursor.fetchone()[0]
                if subAuthor is not None and row[0] != "None":
                    self.add_edge(self.nodeMap[row[0]], self.nodeMap[subAuthor], row[5])
                
        self.sinks = set()
        for node in self.nodes:
            if not self.has_outgoing(node):
                self.sinks.add(node)        

    # print the graph as a column of ordered pairs
    def __str__( self ):
        s = ""
        for key in self.edges_out:
            for i in range(len(self.edges_out[key])):
                s += "(" + str(key) + ", " + str(self.edges_out[key][i]) + ")\n"
        return s

    def getUsername( self, node ):
        return self.usernameMap[node]
    
    # adds a new edge to the graph
    def add_edge( self, node1, node2, score ):
        self.edges_out.setdefault(node1, [])
        self.edges_out[node1].append([node2, score])
        
        self.edges_in.setdefault(node2, [])
        self.edges_in[node2].append([node1, score])

    # return a list of edges from node
    def get_edges_from( self, node ):
        if self.edges_out.get(node):            
            return normalize(self.edges_out.get(node))
        else:
            return []

    # return a list of edges into node
    def get_edges_to( self, node ):
        if self.edges_in.get(node):            
            return normalize(self.edges_in.get(node))
        else:
            return []

    # true if there is an edge from node1 to node2
    def edge_exists( self, node1, node2 ):
        if is_sink( node1 ) or not has_incoming( node2 ):
            return 0
        for i in range(len(self.edges_out[node1])):
            if self.edges_out[node1][i] == node2:
                return 1
        return 0

    # true if node has outgoing edges
    def has_outgoing( self, node ):
        if self.edges_out.get(node) != None:
            if len(self.edges_out[node]) != 0:
                return 1
        return 0

    # true if node has incoming edges
    def has_incoming( self, node ):
        if self.edges_in.get(node) != None:
            if len(self.edges_in[node]) != 0:
                return 1
        return 0
