from typing import List, Tuple, Any
from Base import Base, AttrType
from CollectionManager import CollectionManager


class Course(Base):

    def initCollection(self):
        self.collectionName = "courses"

        self.schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["course_number", "course_name", "description", "units"],
                "additionalProperties": False,
                "properties": {
                    "_id": {},
                    "department": {
                        "bsonType": "objectId",
                        "description": "A reference to the associated department"
                    },
                    "course_number": {
                        "bsonType": "number",
                        "minimum": 100,
                        "maximum": 699,
                        "description": "A unique identifier that differentiates courses within a department"
                    },
                    "course_name": {
                        "bsonType": "string",
                        "maxLength": 80,
                        "description": "The title of the course"
                    },
                    "description": {
                        "bsonType": "string",
                        "maxLength": 120,
                        "description": "A detailed text description of the course"
                    },
                    "units": {
                        "bsonType": "number",
                        "minimum": 1,
                        "maximum": 5,
                        "description": "Units or credits represent the value of the course"
                    }
                }
            }
        }

        self.attributes = [("department", AttrType.FOREIGN_DEPT), ("course_number", AttrType.INTEGER),
                           ("course_name", AttrType.STRING), ("description", AttrType.STRING),
                           ("units", AttrType.INTEGER)]
        self.uniqueCombinations = [[0, 1], [0, 2]]

    def uniqueAttrAdds(self) -> List[Tuple[str, Any]]:
        return []

    def orphanCleanup(self, doc) -> bool:
        success = CollectionManager.GetCollection("departments").f_removeCourse(doc["department"], doc["_id"])
        if not success:
            return False

        sections = CollectionManager.GetCollection("sections")
        sect_count = sections.collection.count_documents({"course": doc["_id"]})
        if sect_count > 0:
            print(f"\n{sect_count} sections are in this course! Delete those first!")
            return False

        return True

    def onValidInsert(self, doc_id):
        dept_id = self.collection.find_one({"_id": doc_id})["department"]

        success = CollectionManager.GetCollection("departments").f_appendCourse(dept_id, doc_id)
        if not success:
            self.collection.delete_one({"_id": doc_id})
        print(f"Course added successfully")

