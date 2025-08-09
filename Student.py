from pprint import pprint
from typing import List, Tuple, Any
from Base import Base, AttrType
from Section import Section
from CollectionManager import CollectionManager
from datetime import datetime


class Student(Base):
    def initCollection(self):
        self.collectionName = "students"
        self.schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["last_name", "first_name", "email", "majors"],
                "additionalProperties": False,
                "properties": {
                    "_id": {},
                    "last_name": {
                        "bsonType": "string",
                        "maxLength": 80,
                        "description": "The string value of the student's surname"
                    },
                    "first_name": {
                        "bsonType": "string",
                        "maxLength": 80,
                        "description": "The string value of the student's given name"
                    },
                    "email": {
                        "bsonType": "string",
                        "maxLength": 180,
                        "description": "A string value representing the email through which the student can be contacted"
                    },
                    "majors": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["name", "declaration_date"],
                            "properties": {
                                "name": {
                                    "bsonType": "string",
                                    "minLength": 5,
                                    "maxLength": 50,
                                    "description": "Name of the major"
                                },
                                "declaration_date": {
                                    "bsonType": "date",
                                    "description": "The calendar day on which the student joined the major"
                                }
                            }
                        },
                        "description": "List of the majors that the student is pursuing"
                    },
                    "sections": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["section_id", "enrollment"],
                            "properties": {
                                "section_id": {
                                    "bsonType": "objectId",
                                    "description": "Section ID"
                                },
                                "enrollment": {
                                    "oneOf": [
                                        {
                                            "bsonType": "object",
                                            "required": ["type", "application_date"],
                                            "properties": {
                                                "type": {
                                                    "enum": ["PassFail"],
                                                    "description": "PassFail type"
                                                },
                                                "application_date": {
                                                    "bsonType": "date",
                                                    "description": "The application date"
                                                }
                                            }
                                        },
                                        {
                                            "bsonType": "object",
                                            "required": ["type", "min_satisfactory"],
                                            "properties": {
                                                "type": {
                                                    "enum": ["LetterGrade"],
                                                    "description": "LetterGrade type"
                                                },
                                                "min_satisfactory": {
                                                    "enum": ["A", "B", "C"],
                                                    "description": "Minimum satisfactory grade that this student feels "
                                                                   "would be satisfactory for them"
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }

        self.attributes = [("last_name", AttrType.STRING), ("first_name", AttrType.STRING), ("email", AttrType.STRING),
                           ("majors", AttrType.FOREIGN_ARRAY), ("sections", AttrType.FOREIGN_ARRAY)]
        self.uniqueCombinations = [[0, 1], [2]]

    def uniqueAttrAdds(self) -> List[Tuple[str, Any]]:
        return [("majors", []), ("sections", [])]

    def orphanCleanup(self, doc) -> bool:
        for sect in doc["sections"]:
            section = sect["section_id"]
            if not CollectionManager.GetCollection("sections").f_removeStudent(section, doc["_id"]):
                return False

        return True

    def onValidInsert(self, doc_id):
        print(f"Student added successfully")

    def addMajor(self):
        print("Select a student to add the major to")
        student = self.selectDoc()

        all_departments = CollectionManager.GetCollection("departments").collection.find({})
        valid_majors = {major['name'] for department in all_departments for major in department['majors']}

        print("Available Majors:")
        for idx, major in enumerate(sorted(valid_majors), 1):
            print(f"{idx}. {major}")
        major_indices = {str(i): name for i, name in enumerate(sorted(valid_majors), 1)}

        seen = set()

        while True:
            maj_index = input("Select a Major by number (or type 'done' to finish) --> ")
            if maj_index.lower() == 'done':
                break

            if maj_index not in major_indices:
                print("Invalid selection. Please try again.")
                continue

            maj_name = major_indices[maj_index]

            if maj_name in seen:
                print("You've already added this major. Try another.")
                continue

            dec_date = self.get_declaration_date()
            if dec_date is None:
                continue

            seen.add(maj_name)

            if self.update_student_major(student["_id"], maj_name, dec_date):
                print("Major added successfully!")
            else:
                print("Failed to add major. Please try again.")

            if input("Add another major? [y/n] --> ").lower() != 'y':
                break

    def get_declaration_date(self):
        today = datetime.today()
        while True:
            date_input = input("Enter the declaration date (YYYY-MM-DD) --> ")
            try:
                declaration_date = datetime.strptime(date_input, "%Y-%m-%d")
                if declaration_date > today:
                    print("The declaration date cannot be in the future. Please enter a valid date.")
                else:
                    return declaration_date
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

    def update_student_major(self, student_id, major_name, declaration_date):
        try:
            self.collection.update_one(
                {"_id": student_id},
                {'$push': {'majors': {"name": major_name, "declaration_date": declaration_date}}}
            )
            return True
        except Exception as e:
            print(f"Error updating student record: {e}")
            return False

    def deleteMajor(self):
        print("Select a student to delete a major from")
        student = self.selectDoc()
        if student is None:
            return

        valid_maj = []
        print("Which major do you want to delete?")
        for majors in student["majors"]:
            valid_maj.append(majors["name"])
            print(majors["name"])

        maj_name = input("Major Name --> ")
        while maj_name not in valid_maj:
            print("That's not a valid major!\nTry Again\n\n")
            maj_name = input("Major Name --> ")

        try:
            self.collection.update_one({}, {"$pull": {"majors": {"name": {"$in": [maj_name]}}}})
        except Exception as e:
            print(f"\nError in {self.collectionName}: {str(e)}")
            print("Failed to remove major from student")

    def listStudentMajors(self):
        for student in self.collection.find({}):
            print("Student:", student["first_name"], student["last_name"], "has major(s):")
            for major in student["majors"]:
                pprint(major)

    def addEnrollment(self):
        while True:
            print("Select a student")
            student = self.selectDoc()
            if student is None:
                print("No student selected. Aborting Enrollment.")
                return

            print("Select a section")
            section = CollectionManager.GetCollection("sections").selectDoc()
            if section is None:
                print("No section selected. Aborting Enrollment.")
                return

            course_id = section["course"]
            semester = section["semester"]
            year = section["section_year"]
            for section_obj in student["sections"]:
                sect = CollectionManager.GetCollection("sections").collection.find_one(
                    {"_id": section_obj["section_id"]})
                if course_id == sect["course"] and semester == sect["semester"] and year == sect["section_year"]:
                    print("You cannot enroll in multiple sections of the same course during the same semester!")
                    return

            enrollment = None
            prop_type = ""
            prop_name = ""
            print("\nEnroll with PassFail or LetterGrade?"
                  "\n1. PassFail"
                  "\n2. LetterGrade")
            user_inp = input("--> ")
            while user_inp != "1" and user_inp != "2":
                user_inp = input("Invalid input. Try Again.")
            if user_inp == "1":
                prop_type = "PassFail"
                prop_name = "application_date"
                while True:
                    try:
                        date_input = input("Enter the application date (YYYY-MM-DD) --> ")
                        date = datetime.strptime(date_input, "%Y-%m-%d")
                        return date
                    except ValueError:
                        print("Invalid date format. Please use YYYY-MM-DD.")
            else:
                prop_type = "LetterGrade"
                prop_name = "min_satisfactory"
                valid_letters = ['A', 'B', 'C']
                print("Select A Minimum Satisfactory Grade: ", valid_letters)
                grade = input("--> ")
                while grade not in valid_letters:
                    print("Invalid grade. Please choose from " + ", ".join(valid_letters))
                    grade = input("--> ")
                enrollment = grade

            try:
                self.collection.update_one({"_id": student["_id"]}, {'$push': {'sections': {"section_id": section["_id"]
                    , "enrollment": {"type": prop_type, prop_name: enrollment}}}})
                success = CollectionManager.GetCollection("sections").f_appendStudent(section["_id"], student["_id"])
                if not success:
                    raise Exception
            except Exception as e:
                print(f"\nError in {self.collectionName}: {str(e)}")
                print("Failed to enroll in section\n")

            print("Add another Enrollment? [y/n]")
            y_n_input = input("> ")
            while y_n_input != 'y' and y_n_input != 'n':
                print("\nPlease only enter either 'y' or 'n'")
                y_n_input = input("> ")
            print("")

            if y_n_input == 'n':
                break

    def deleteEnrollment(self):
        while True:
            print("Select the student to unenroll")
            student = self.selectDoc()
            if student is None:
                print("No student is selected. Aborting Enrollment")
                return

            print("\nSelect the section the student wants to unenroll from")
            section = CollectionManager.GetCollection("sections").selectDoc()
            if section is None:
                print("No section is selected. Aborting Enrollment")
                return

            print("Are you sure you want to unenroll from this section? [y/n]")
            user_input = input("--> ").strip().lower()
            while user_input not in ['y', 'n']:
                print("\nInvalid input. Enter 'y' for Yes or 'n' for No.")
                user_input = input("--> ").strip().lower()

            if user_input == 'y':
                try:
                    update_result = self.collection.update_one(
                        {"_id": student["_id"]},
                        {"$pull": {"sections": {"section_id": section["_id"]}}}
                    )
                    if update_result.modified_count == 0:
                        print("No updates made, possibly the student was not enrolled in the section.")
                        return

                    success = CollectionManager.GetCollection("sections").f_removeStudent(section["_id"],
                                                                                          student["_id"])
                    if not success:
                        raise Exception("Failed to remove student from section in section collection.")

                    print("Student unenrolled successfully!")
                except Exception as e:
                    print(f"\nError in {self.collectionName}: {str(e)}")
                    print("Failed to un-enroll in section.")

    def listEnrollments(self):
        for stu in self.collection.find({}):
            print("Student:", stu["first_name"], stu["last_name"], "has enrollments:")
            for enr in stu["sections"]:
                pprint(enr)
