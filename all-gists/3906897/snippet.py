#!/usr/bin/env python
process_queue = []
total_wtime = 0
n = int(raw_input('Enter the total no of processes: '))
for i in xrange(n):
    process_queue.append([])#append a list object to the list
    process_queue[i].append(raw_input('Enter p_name: '))
    process_queue[i].append(int(raw_input('Enter p_arrival: ')))
    total_wtime += process_queue[i][1]
    process_queue[i].append(int(raw_input('Enter p_bust: ')))
    print ''

process_queue.sort(key = lambda process_queue:process_queue[1])

print 'ProcessName\tArrivalTime\tBurstTime'
for i in xrange(n):
    print process_queue[i][0],'\t\t',process_queue[i][1],'\t\t',process_queue[i][2]
    
print 'Total waiting time: ',total_wtime
print 'Average waiting time: ',(total_wtime/n)