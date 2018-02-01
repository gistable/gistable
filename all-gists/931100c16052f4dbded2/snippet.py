#!/usr/bin/python
import csv, sys, os
import numpy as np

# Get the top X non-fork projects for the GHTorrent dump (without using SQL)
# The dumps should be available at http://ghtorrent.org/downloads.html

if len(sys.argv) < 5:
        print "Usage <dir> <language> <topX> <outcsv>"
        sys.exit(-1)

dump_directory = sys.argv[1]
target_language = sys.argv[2]
num_top = int(sys.argv[3])
output_file = sys.argv[4]

print "Retrieving the top %s %s projects from %s" % (num_top, target_language, dump_directory)

print "Loading data..."

projects = {}  # project_id -> project_data
with open(os.path.join(dump_directory, 'projects.csv')) as f:
        data = csv.reader(f, doublequote=False, escapechar='\\', quotechar='"')
        for project in data:
                project_id = int(project[0])
                project_url = project[1]
                project_language = project[5]
                try:
                    	is_fork = int(project[7]) >= 0
                except:
                       	is_fork = False
                if is_fork or project_language != target_language:
                        continue
                projects[project_id] = {"url":project_url, "forks":0, "watchers":0}

print "Collected %s projects" % len(projects)
with open(os.path.join(dump_directory, 'projects.csv')) as f:
        data = csv.reader(f, doublequote=False, escapechar='\\', quotechar='"')
        for project in data:
                try:
                    	forked_from = int(project[7])
                except:
                        forked_from = -1
                if forked_from in projects:
                         projects[forked_from]["forks"] += 1

with open(os.path.join(dump_directory, 'watchers.csv')) as f:
        data = csv.reader(f, doublequote=False, escapechar='\\', quotechar='"')
        for project in data:
                project_id = int(project[0])
                if project_id in projects:
                         projects[project_id]["watchers"] += 1

print "Computing scores..."
forks_elements = [d["forks"] for d in projects.values()]
forks_elements = np.array(forks_elements)
fork_mean, fork_std = np.mean(forks_elements), np.std(forks_elements)
print "Fork stats avg=%s std=%s" % (fork_mean, fork_std)

watchers_elements = [d["watchers"] for d in projects.values()]
watchers_elements = np.array(watchers_elements)
watchers_mean, watchers_std = np.mean(watchers_elements), np.std(watchers_elements)
print "Watcher stats avg=%s std=%s" % (watchers_mean, watchers_std)

zscore = lambda element, mean, std: (element - mean) /std

for project, project_data in projects.iteritems():
        project_data["score"] = zscore(project_data["forks"], fork_mean, fork_std) + zscore(project_data["watchers"], watchers_mean, watchers_std)

top_projects = sorted(projects.keys(), key=lambda p:projects[p]["score"], reverse=True)

with open(output_file, 'w') as f:
        writer = csv.writer(f)
        for i in xrange(num_top):
                project_id = top_projects[i]
                project_data = projects[project_id]
                row = [project_data["url"], project_data["forks"], project_data["watchers"], project_data["score"]]
                writer.writerow(row)