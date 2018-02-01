"""
A simple script to copy a Basecamp classic todo list
over to Blimp as a goal with tasks

@author: Dave Jeffery

@requirements:
pip install git+git://github.com/nowherefarm/basecamp.git
pip install blimp
"""

import blimp
from basecamp import Basecamp
import elementtree.ElementTree as ET

bc = Basecamp('https://MYCOMPANY.basecamphq.com', 'username', 'password')
bl = blimp.Client('username', 'api_key', 'app_id', 'app_secret')

def _get_todo_list(id):
    xml = bc.todo_list(id)
        
    todo_list = {
        'name': ET.fromstring(xml).find('name').text,
        'items': []
    }
    
    items = ET.fromstring(xml).findall('todo-items/todo-item')
    for item in items:
        todo_list['items'].append(item.find("content").text)
        
    return todo_list
    
        
def _iterate_and_print(obj):
    for obj in obj['objects']:
        print str(obj['id']) + ': ' + obj['name']
        
        
def _create_task_list(todo_list, project_id):
    project_uri = '/api/v2/project/' + str(project_id) + '/'
    
    goal_data = {
        'project': project_uri,
        'title': todo_list['name'],
    }
    goal = bl.goal.create(goal_data)
    
    print "Populating the task list..."
    
    i = 0
    for todo in todo_list['items']:
        task_data = {
            'goal': goal['resource_uri'],
            'title': todo
        }
        bl.task.create(task_data)
        i = i + 1
         
    print "Added " + str(i) + " tasks."
    

if __name__ == "__main__":
    print "Enter the id of the Basecamp todo list you want to copy over:"   
    bc_todo_id = int(raw_input("> "))
    print "Fetching todos..."
    todo_list = _get_todo_list(bc_todo_id)
    print "Done!"
    
    print "\nOk, lets find the Blimp project that you wish to copy this todo list to..."
    
    companies = bl.company()
    print "\nEnter the `id` of the *company* (or just press enter to choose the first option):"
    _iterate_and_print(companies)
    company_id = raw_input("> ") or companies['objects'][0]['id']
    
    projects = bl.project(params={'company': company_id})
    print "\nEnter the `id` of the *project* (or just press enter to choose the first option):"
    _iterate_and_print(projects)
    project_id = raw_input("> ") or projects['objects'][0]['id']
    
    print "\nOk, creating the task list..."
    _create_task_list(todo_list, project_id)
    print "Aww yeah, we're done! Exiting."