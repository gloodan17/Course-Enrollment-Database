from bson import ObjectId
from typing import List, Tuple, Any
from Base import Base, AttrType
from CollectionManager import CollectionManager


class Department(Base):
    def initCollection(self):
        self.collectionName = "departments"

        self.schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "abbreviation", "chair_name", "building", "office", "description"],
                "properties": {
                    "name": {
                        "bsonType": "string",
                        "minLength": 10,
                        "maxLength": 50,
                        "description": "The full name of the department"
                    },
                    "abbreviation": {
                        "bsonType": "string",
                        "maxLength": 6,
                        "description": "A shortened form of the department name"
                    },
                    "chair_name": {
                        "bsonType": "string",
                        "maxLength": 80,
                        "description": "The full name of the individual leading the department"
                    },
                    "building": {
                        "enum": ['NAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC'],
                        "description": "The name of the building where the department's main office is located"
                    },
                    "office": {
                        "bsonType": "number",
                        "description": "The specific office number within the building where the department's main "
                                       "administrative activities occur"
                    },
                    "description": {
                        "bsonType": "string",
                        "maxLength": 200,
                        "description": "A brief statement summarizing the department’s focus and responsibilities "
                                       "within the university"
                    },

                    "majors": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["name", "description"],
                            "properties": {
                                "name": {
                                    "bsonType": "string",
                                    "maxLength": 80,
                                    "description": "Name of the major"
                                },
                                "description": {
                                    "bsonType": "string",
                                    "maxLength": 200,
                                    "description": "Description of the major"
                                }
                            }
                        },
                        "description": "List of majors offered by the department",
                        "uniqueItems": True
                    },

                    "courses": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "objectId"
                        }
                    }
                }
            }
        }

        self.attributes = [("name", AttrType.STRING), ("abbreviation", AttrType.STRING), ("chair_name", AttrType.STRING),
                           ("building", AttrType.STRING), ("office", AttrType.INTEGER),
                           ("description", AttrType.STRING), ("majors", AttrType.FOREIGN_ARRAY)]
        self.uniqueCombinations = [[0], [1], [2], [3, 4]]

    def uniqueAttrAdds(self) -> List[Tuple[str, Any]]:
        return [("majors", [])]

    def orphanCleanup(self, doc) -> bool:
        courses_count = len(doc["courses"])
        if courses_count > 0:
            print(f"{courses_count} course(s) belonging to this department must be deleted first.")
            return False
        majors_count = len(doc["majors"])
        if majors_count > 0:
            print(f"{majors_count} major(s) belonging to this department must be deleted first.")
            return False
        return True

    def onValidInsert(self, doc_id):
        print(f"Department added successfully")

    def addMajor(self):
        print("Select a department to add the major to")
        department = self.selectDoc()
        if not department:
            print("Department selection failed. Exiting operation.")
            return

        while True:
            new_major_name = input("Enter a name for the major --> ")
            existing_major = self.db.departments.find_one({"majors.name": new_major_name}, {"_id": 1})
            if existing_major:
                print("Major with this name already exists. Try again.\n")
                continue

            new_major_description = input("Enter a description for the major --> ")
            new_major = {'name': new_major_name, 'description': new_major_description}

            try:
                result = self.collection.update_one(
                    {"_id": department["_id"]},
                    {'$push': {'majors': new_major}}
                )
                if result.modified_count > 0:
                    print(f"{new_major_name} added to {department['name']}")
                else:
                    print("Failed to add major. No changes were made.")
                break
            except Exception as e:
                print(f"\nError adding major: {str(e)}")
                if input("Try again? [y/n]: ").lower() != 'y':
                    print("Operation cancelled.")
                    break

    def deleteMajor(self):
        major_name  = input("Name of the major to delete --> ")
        result = self.collection.update_one({}, {"$pull": {"majors": {"name": major_name}}})
        if result.modified_count > 0:
            print(f"{major_name} deleted.")
        else:
            print("No majors with that name found.")

    def listMajors(self):
        all_departments = self.getAll()
        for dept in all_departments:
            print(dept["name"])
            for major in dept["majors"]:
                print(f"  Major: {major['name']}, Description: {major['description']}")

    def f_appendCourse(self, dept_id, course_id) -> bool:
        try:
            result = self.collection.update_one({"_id": dept_id}, {"$push": {"courses": course_id}})
            return result.modified_count > 0
        except Exception as e:
            print(f"Failed to append course: {str(e)}")
            return False

    def f_removeCourse(self, dept_id, course_id) -> bool:
        try:
            result = self.collection.update_one({"_id": dept_id}, {"$pull": {"courses": course_id}})
            return result.modified_count > 0
        except Exception as e:
            print(f"Failed to delete course: {str(e)}")
            return False

