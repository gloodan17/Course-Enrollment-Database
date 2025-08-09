from Connect import Connect
from menu_definitions import menu_main, menu_add, menu_select, menu_list, menu_delete
from CollectionManager import CollectionManager
from Department import Department
from Student import Student
from Course import Course
from Section import Section
from pprint import pprint


def exec_menu(menu):
    user_action: str = ""
    while user_action != menu.last_action():
        user_action = menu.menu_prompt()
        print("")
        exec(user_action)
        print("")


if __name__ == "__main__":
    clientMgr = Connect()
    clientMgr.connectClient()
    db = clientMgr.client["Enrollment"]
    CollectionManager.AddCollection("departments", Department(db))
    CollectionManager.AddCollection("students", Student(db))
    CollectionManager.AddCollection("courses", Course(db))
    CollectionManager.AddCollection("sections", Section(db))

    exec_menu(menu_main)
