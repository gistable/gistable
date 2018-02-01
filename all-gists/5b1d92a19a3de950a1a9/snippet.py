#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

"""
usage:
    python wunderlist2workflowy.py >> wunderlist.txt

    Go to Wunderlist web interface, backup data (JSON file), use this script and paste the output into Workflowy.
"""

with open('wunderlist.json') as f:
    wunderlist = json.load(f)['data']

for my_list in wunderlist['lists']:
    print(my_list['title'])
    for task_position in wunderlist['task_positions']:
        if task_position['list_id'] == my_list['id']:
            task_ids_list = task_position['values']
            if len(task_ids_list) == 0:
                for task in wunderlist['tasks']:
                    if task['list_id'] == my_list['id']:
                        task_ids_list.append(task['id'])
            for task_id in task_ids_list:
                for task in wunderlist['tasks']:
                    if task['id'] == task_id:
                        if 'due_date' in task:
                            workflowy_task = task['title'] + ' #d-' + task['due_date']
                        else:
                            workflowy_task = task['title']
                        print('\t' + workflowy_task)
                        for note in wunderlist['notes']:
                            if note['task_id'] == task_id:
                                if len(note['content']) != 0:
                                    print('\t\t' + note['content'].strip())
                        for subtask_position in wunderlist['subtask_positions']:
                            if subtask_position['task_id'] == task['id']:
                                for subtask_id in subtask_position['values']:
                                    for subtask in wunderlist['subtasks']:
                                        if subtask['id'] == subtask_id:
                                            print('\t\t' + subtask['title'])
