from projects_repository import ProjectsRepository
from project import Project


def load_all_items_from_database(repository):
    print("Loading all items from database:")
    projects = repository.read()
    at_least_one_item = False
    for p in projects:
        at_least_one_item = True
        tmp_project = Project.build_from_json(p)
        print("ID = {} | Title = {} | Price = {}".format(tmp_project._id,tmp_project.title, tmp_project.price))
    if not at_least_one_item:
        print("No items in the database")


def test_create(repository, new_project):
    print("\n\nSaving new_project to database")
    repository.create(new_project)
    print("new_project saved to database")
    print("Loading new_project from database")
    db_projects = repository.read(project_id=new_project._id)
    for p in db_projects:
        project_from_db = Project.build_from_json(p)
        print("new_project = {}".format(project_from_db.get_as_json()))


def test_update(repository, new_project):
    print("\n\nUpdating new_project in database")
    repository.update(new_project)
    print("new_project updated in database")
    print("Reloading new_project from database")
    db_projects = repository.read(project_id=new_project._id)
    for p in db_projects:
        project_from_db = Project.build_from_json(p)
        print("new_project = {}".format(project_from_db.get_as_json()))


def test_delete(repository, new_project):
    print("\n\nDeleting new_project to database")
    repository.delete(new_project)
    print("new_project deleted from database")
    print("Trying to reload new_project from database")
    db_projects = repository.read(project_id=new_project._id)
    found = False
    for p in db_projects:
        found = True
        project_from_db = Project.build_from_json(p)
        print("new_project = {}".format(project_from_db.get_as_json()))

    if not found:
        print("Item with id = {} was not found in the database".format(new_project._id))


def main():
    repository = ProjectsRepository()

    #display all items from DB
    load_all_items_from_database(repository)

    #create new_project and read back from database
    new_project = Project.build_from_json({"title":"Wordpress website for Freelancers", 
        "description":"This should be a very simple website, based on wordpress with functionalities for Freelancers", 
        "price":250, 
        "assigned_to":"John Doe"})
    test_create(repository, new_project)

    #update new_project and read back from database
    new_project.price = 350
    test_update(repository, new_project)

    #delete new_project and try to read back from database
    test_delete(repository, new_project)

if __name__ == '__main__':
    main()