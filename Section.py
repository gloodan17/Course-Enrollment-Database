from typing import List, Tuple, Any
from Base import Base, AttrType


class Section(Base):

    def initCollection(self):
        self.collectionName = "sections"

        self.schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["course", "section_number", "semester", "section_year",
                             "building", "room", "schedule", "start_time", "instructor"],
                "additionalProperties": False,
                "properties": {
                    "_id": {},
                    "course": {
                        "bsonType": "objectId",
                        "description": "A reference to the associated course"
                    },
                    "section_number": {
                        "bsonType": "number",
                        "minimum": 1,
                        "description": "The identifier for this specific instance of a course"
                    },
                    "semester": {
                        "enum": ['Fall', 'Spring', 'Summer I', 'Summer II', 'Summer III', 'Winter'],
                        "description": "The academic term when the section is held"
                    },
                    "section_year": {
                        "bsonType": "number",
                        "minimum": 1636,
                        "description": "The calendar year when the section is held"
                    },
                    "building": {
                        "enum": ['ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC'],
                        "description": "The name of the building where classes are conducted"
                    },
                    "room": {
                        "bsonType": "number",
                        "minimum": 1,
                        "maximum": 999,
                        "description": "The specific room number in the building where the section meets"
                    },
                    "schedule": {
                        "enum": ['MW', 'TuTh', 'MWF', 'F', 'S'],
                        "description": "The days of the week when the section meets"
                    },
                    "start_time": {
                        "bsonType": "number",
                        "minimum": 800,
                        "maximum": 1930,
                        "description": "The starting time for the section expressed as a number"
                    },
                    "instructor": {
                        "bsonType": "string",
                        "maxLength": 80,
                        "description": "The name of the instructor teaching the section"
                    },
                    "students": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "objectId"
                        }
                    }
                }
            }
        }

        self.attributes = [("course", AttrType.FOREIGN_COURSE), ("section_number", AttrType.INTEGER),
                           ("semester", AttrType.STRING), ("section_year", AttrType.INTEGER),
                           ("building", AttrType.STRING), ("room", AttrType.INTEGER),
                           ("schedule", AttrType.STRING), ("start_time", AttrType.INTEGER),
                           ("instructor", AttrType.STRING)]
        self.uniqueCombinations = [[0, 1, 2, 3], [2, 3, 4, 5, 6, 7], [2, 3, 6, 7, 8]]

    def uniqueAttrAdds(self) -> List[Tuple[str, Any]]:
        return [("students", [])]

    def orphanCleanup(self, doc) -> bool:
        students_count = len(doc["students"])
        if students_count > 0:
            print(f"{students_count} student(s) are enrolled in this section! Remove them from this section first!")
            return False

        return True

    def onValidInsert(self, doc_id):
        print(f"Section added successfully")

    def f_appendStudent(self, sect_id, student_id) -> bool:
        try:
            self.collection.update_one({"_id": sect_id}, {"$push": {"students": student_id}})
        except Exception as e:
            print(f"\nError in {self.collectionName}: {str(e)}")
            print("\n\nFailed to append student to section!\n")
            return False

        return True

    def f_removeStudent(self, sect_id, student_id) -> bool:
        try:
            self.collection.update_one({"_id": sect_id}, {"$pull": {"students": student_id}})
        except Exception as e:
            print(f"\nError in {self.collectionName}: {str(e)}")
            print("\n\nFailed to delete student from section!\n")
            return False

        return True
