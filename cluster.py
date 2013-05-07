# performs clustering on the subreddits in our database
from subreddits import getSubredditCounts
from sim import findOverlap
import csv
import sys

MAX_ITERATIONS = 20

# find proximity matrix
# returns (and prints) matrix of subreddit similarity scores
def find_proximity_matrix():
    subreddits = sorted(getSubredditCounts().keys())
    prox = {}
    for sub in subreddits:
        prox[sub] = {}
    for i in range(len(subreddits)):
        for j in range(i, len(subreddits)):
            sub1 = subreddits[i]
            sub2 = subreddits[j]
            simScore = 1.0
            if sub1 != sub2:
                simScore = findOverlap(sub1, sub2)
                print sub1, sub2, simScore
            prox[sub1][sub2] = simScore
            prox[sub2][sub1] = simScore
    print
    return prox

# reads in a proximity matrix from a file, returns dict
def read_proximity(filename):
    prox = {}
    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=' ')
        for row in csvreader:
            if len(row) == 0:
                continue
            sr1 = row[0]
            sr2 = row[1]
            if sr1 not in prox:
                prox[sr1] = {}
            if sr2 not in prox:
                prox[sr2] = {}
            prox[sr1][sr2] = float(row[2])
            prox[sr2][sr1] = float(row[2])
    return prox

# returns a list of clusters (which are themselves lists of subreddits)
#     using complete-linkage or furthest-neighbor clustering
def complete_link_cluster(prox, iterations=MAX_ITERATIONS):
    # list containing all clusters
    clusters = []
    for sub in prox.keys():
        clusters.append([sub])
    for i in range(iterations):
        if len(clusters) == 1:
            return clusters
        print "Iteration:", i+1
        # find most similar pair of clusters in current clustering
        c1index = -1
        c2index = -1
        maxClusterSim = 0.0
        for c1 in clusters:
            for c2 in clusters:
                if clusters.index(c1) == clusters.index(c2):
                    continue
                # find the least sim between elements of c1 and c2
                minSim = 1.0
                c1index2 = -1
                c2index2 = -1
                for sub1 in c1:
                    for sub2 in c2:
                        if minSim > prox[sub1][sub2]:
                            minSim = prox[sub1][sub2]
                            c1index2 = clusters.index(c1)
                            c2index2 = clusters.index(c2)
                if minSim > maxClusterSim:
                    maxClusterSim == minSim
                    c1index = c1index2
                    c2index = c2index2
        # merge those clusters
        if (c1index == -1) and (c2index == -1):
            return clusters
        for sub in clusters[c2index]:
            clusters[c1index].append(sub)
        clusters.pop(c2index)
    return clusters
    
# returns a list of clusters (which are themselves lists of subreddits)
#     using single-linkage or nearest-neighbor clustering
# CURRENTLY DOES NOT WORK PROPERLY
def single_link_cluster(prox, iterations=MAX_ITERATIONS):
    # list containing all clusters
    clusters = []
    for sub in prox.keys():
        clusters.append([sub])
    for i in range(iterations):
        if len(clusters) == 1:
            return clusters
        print "Iteration:", i+1
        # find most similar pair of clusters in current clustering
        c1index = -1
        c2index = -1
        maxClusterSim = 0.0
        for c1 in clusters:
            for c2 in clusters:
                if clusters.index(c1) == clusters.index(c2):
                    continue
                # find the max sim between elements of c1 and c2
                maxSim = 0.0
                c1index2 = -1
                c2index2 = -1
                for sub1 in c1:
                    for sub2 in c2:
                        if maxSim < prox[sub1][sub2]:
                            maxSim = prox[sub1][sub2]
                            c1index2 = clusters.index(c1)
                            c2index2 = clusters.index(c2)
                if maxSim > maxClusterSim:
                    maxClusterSim == maxSim
                    c1index = c1index2
                    c2index = c2index2
        # merge those clusters
        for sub in clusters[c2index]:
            clusters[c1index].append(sub)
        clusters.pop(c2index)
    return clusters
    
# takes list of clusters, prints objective score
def complete_link_objective(clusters, prox):
    objective = 0.0
    numCompares = 0
    # find similarity between c1 and all other clusters
    for c1 in clusters:
        for c2 in clusters:
            if clusters.index(c1) == clusters.index(c2):
                continue
            # find the least sim between elements of c1 and c2
            minSim = 1.0
            c1index2 = -1
            c2index2 = -1
            for sub1 in c1:
                for sub2 in c2:
                    if minSim > prox[sub1][sub2]:
                        minSim = prox[sub1][sub2]
            objective += minSim
            numCompares += 1
    objective /= numCompares
    return objective

# takes list of clusters, prints
def print_cluster_list(clusters, prox):
    srCount = 0
    for cluster in clusters:
        for sr in sorted(cluster):
            print sr
            srCount += 1
        print
    print "Subreddits:", srCount
    print "Clusters:", len(clusters)
    #print "Objective:", complete_link_objective(clusters, prox)

def main():
    iterations = MAX_ITERATIONS
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    #prox = find_proximity_matrix()
    prox = read_proximity("prox2.txt")
    clusters = complete_link_cluster(prox, iterations)
    #clusters = single_link_cluster(prox, iterations)
    print_cluster_list(clusters, prox)
        
if __name__ == "__main__":
    main()
