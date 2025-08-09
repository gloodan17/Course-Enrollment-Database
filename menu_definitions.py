from Menu import Menu, Option

menu_main = Menu('main', 'Select Option:', [
    Option("Add", "exec_menu(menu_add)"),
    Option("Select", "exec_menu(menu_select)"),
    Option("List", "exec_menu(menu_list)"),
    Option("Delete", "exec_menu(menu_delete)"),
    Option("Exit this application", "pass")
])

menu_add = Menu('add', 'Select Collection To Add:', [
    Option("Departments", "CollectionManager.GetCollection('departments').addDoc()"),
    Option("Majors", "CollectionManager.GetCollection('departments').addMajor()"),
    Option("Students", "CollectionManager.GetCollection('students').addDoc()"),
    Option("Courses", "CollectionManager.GetCollection('courses').addDoc()"),
    Option("Sections", "CollectionManager.GetCollection('sections').addDoc()"),
    Option("StudentMajors", "CollectionManager.GetCollection('students').addMajor()"),
    Option("Enrollments", "CollectionManager.GetCollection('students').addEnrollment()"),
    Option("Exit", "pass")
])

menu_select = Menu('select', 'Select Collection To Select:', [
    Option("Departments", "pprint(CollectionManager.GetCollection('departments').selectDoc())"),
    Option("Students", "pprint(CollectionManager.GetCollection('students').selectDoc())"),
    Option("Courses", "pprint(CollectionManager.GetCollection('courses').selectDoc())"),
    Option("Sections", "pprint(CollectionManager.GetCollection('sections').selectDoc())"),
    Option("Exit", "pass")
])

menu_list = Menu('list', 'Select Collection To List:', [
    Option("Departments", "CollectionManager.GetCollection('departments').listAll()"),
    Option("Majors", "CollectionManager.GetCollection('departments').listMajors()"),
    Option("Students", "CollectionManager.GetCollection('students').listAll()"),
    Option("Courses", "CollectionManager.GetCollection('courses').listAll()"),
    Option("Sections", "CollectionManager.GetCollection('sections').listAll()"),
    Option("StudentMajors", "CollectionManager.GetCollection('students').listStudentMajors()"),
    Option("Enrollments", "CollectionManager.GetCollection('students').listEnrollments()"),
    Option("Exit", "pass")
])

menu_delete = Menu('delete', 'Select Collection to Delete:', [
    Option("Departments", "CollectionManager.GetCollection('departments').deleteDoc()"),
    Option("Majors", "CollectionManager.GetCollection('departments').deleteMajor()"),
    Option("Students", "CollectionManager.GetCollection('students').deleteDoc()"),
    Option("Courses", "CollectionManager.GetCollection('courses').deleteDoc()"),
    Option("Sections", "CollectionManager.GetCollection('sections').deleteDoc()"),
    Option("StudentMajors", "CollectionManager.GetCollection('students').deleteMajor()"),
    Option("Enrollments", "CollectionManager.GetCollection('students').deleteEnrollment()"),
    Option("Exit", "pass")
])
