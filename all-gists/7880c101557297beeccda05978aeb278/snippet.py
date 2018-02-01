# Example of use of Afanasy's API to generate a summary of the state of the
# render farm.
# Copyright (c) 2016 rise|fx (Elie Michel) - Released under MIT License

import af

cmd = af.Cmd()

def isSysJob(job):
    return job['st'] == 0

## Jobs ##

joblist = cmd.getJobList()
job_state_counters = {}
job_count = 0

for job in joblist:
    if isSysJob(job):
        continue

    job_count += 1
    for s in job['state'].split():
        job_state_counters[s] = job_state_counters.get(s, 0) + 1


print("Out of %d jobs:" % job_count)
print(" * %d are running" % job_state_counters.get('RUN', 0))
print(" * %d have error" % job_state_counters.get('ERR', 0))
print(" * %d are skipped" % job_state_counters.get('SKP', 0))
print(" * %d are off" % job_state_counters.get('OFF', 0))
print(" * %d are ready" % job_state_counters.get('RDY', 0))
print(" * %d are done" % job_state_counters.get('DON', 0))

# Note that the sum may exceed the total number of jobs because a job can have
# several states

print("")

## Renders ##

renderlist = cmd.renderGetList()
render_state_counts = {}

for render in renderlist:
    for s in render['state'].split():
        render_state_counts[s] = render_state_counts.get(s, 0) + 1

print("Out of %d renders:" % len(renderlist))
print(" * %d are online" % render_state_counts.get('ONL', 0))
print(" * %d are offline" % render_state_counts.get('OFF', 0))
print(" * %d are nimby" % render_state_counts.get('NBY', 0))
print(" * %d are running" % render_state_counts.get('RUN', 0))
print(" * %d are dirty" % render_state_counts.get('DRT', 0))

# Note that the sum may exceed the total number of renders because a render can
# have several states

