from pprint import pprint
import pymongo
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Tuple, Any, List
from CollectionManager import CollectionManager


class AttrType(Enum):
    STRING = 1
    INTEGER = 2
    TIME = 3
    FOREIGN_ARRAY = 4
    FOREIGN_DEPT = "departments"
    FOREIGN_COURSE = "courses"


class Base(ABC):
    def __init__(self, db):
        self._db = db
        self._collectionName = "Invalid"
        self._collection = None
        self.schema = {"invalid"}
        self.attributes = []
        self.uniqueCombinations = []
        self.initCollection()
        self.setupCollection()

    @abstractmethod
    def initCollection(self):
        pass

    def setupCollection(self):
        try:
            self.db.create_collection(self.collectionName)
        except Exception as e:
            print(f'Using existing "{self.collectionName}" collection.')

        self.db.command("collMod", self.collectionName, validator=self.schema)

        for combo in self.uniqueCombinations:
            index_fields = [(self.attributes[index][0], pymongo.ASCENDING) for index in combo]
            self.collection.create_index(index_fields, unique=True)

    def addDoc(self):
        success: bool = False
        new_doc_id = None

        while not success:
            try:
                new_doc = {}
                for attr, attrType in self.attributes:
                    match attrType:
                        case AttrType.STRING:
                            new_doc[attr] = input(f"{str(self.schema['$jsonSchema']['properties'][attr])}"
                                                  f"\nEnter {attr} --> ")
                        case AttrType.INTEGER:
                            new_doc[attr] = int(input(f"{str(self.schema['$jsonSchema']['properties'][attr])}"
                                                      f"\nEnter {attr} --> "))
                        case AttrType.TIME:
                            hour = int(input(f"{str(self.schema['$jsonSchema']['properties'][attr])}"
                                             f"\nEnter {attr}'s hour [0-23] --> "))
                            minutes = int(input(f"\nEnter {attr}'s minutes [0-59] --> "))
                            new_doc[attr] = datetime(2024, 5, 7, hour, minutes, 0)
                        case _:
                            if not isinstance(attrType, AttrType):
                                print("\nEnsure that attributes are defined using the correct AttrType values")
                                return

                            if attrType == AttrType.FOREIGN_ARRAY:
                                continue

                            print(f"Select {attrType.value}")
                            new_doc[attr] = CollectionManager.GetCollection(attrType.value).selectDoc()["_id"]

                new_attrs = self.uniqueAttrAdds()
                if len(new_attrs) > 0:
                    for attr, attrType in new_attrs:
                        new_doc[attr] = attrType

                new_doc_id = self.collection.insert_one(new_doc).inserted_id

            except Exception as e:
                print(f"\nError in {self.collectionName}: {str(e)}")

                print("Try Again? [y/n]")
                user_inp = input("--> ")
                while user_inp != 'y' and user_inp != 'n':
                    print("\nInvalid input. Enter 'y' for Yes or 'n' for No.")
                    user_inp = input("--> ")
                print("")

                if user_inp == 'n':
                    break

                continue

            success = True
        self.onValidInsert(new_doc_id)

    @abstractmethod
    def uniqueAttrAdds(self) -> List[Tuple[str, Any]]:
        pass

    @abstractmethod
    def onValidInsert(self, doc_id):
        pass

    def deleteDoc(self):
        doc = self.selectDoc()
        if doc is None:
            print("Document selection failed, aborting deletion.")
            return

        if self.orphanCleanup(doc):
            delete_result = self.collection.delete_one({"_id": doc["_id"]})
            print(f"Deleted {delete_result.deleted_count} document(s).")
        else:
            print(f"Orphan CleanUp Failed in {self.collectionName} collection!")
            return

    @abstractmethod
    def orphanCleanup(self, doc) -> bool:
        pass

    def listAll(self) -> List:
        pipeline = []
        for attr, attr_type in self.attributes:
            if isinstance(attr_type, AttrType) and attr_type in [AttrType.FOREIGN_DEPT, AttrType.FOREIGN_COURSE]:
                ref_collection = CollectionManager.GetCollection(attr_type.value).collection.name
                pipeline.append({
                    '$lookup': {
                        'from': ref_collection,
                        'localField': attr,
                        'foreignField': '_id',
                        'as': attr + '_info'
                    }
                })
                pipeline.append({
                    '$unwind': {
                        'path': f'${attr}_info',
                        'preserveNullAndEmptyArrays': True
                    }
                })
                pipeline.append({
                    '$addFields': {
                        attr: f'${attr}_info.name'
                    }
                })

        projection = {attr: 1 for attr, _ in self.attributes}
        pipeline.append({'$project': projection})

        doc_list = list(self.collection.aggregate(pipeline))
        for doc in doc_list:
            pprint(doc)
        return doc_list

    def getAll(self) -> List:
        return self.collection.find({})

    def selectDoc(self):
        ways = len(self.uniqueCombinations)
        print("Choose a way to select:")
        for idx, combination in enumerate(self.uniqueCombinations, start=1):
            attribute_names = [self.attributes[i][0] for i in combination]
            formatted_attributes = ', '.join(attribute_names)
            print(f"{idx}. [{formatted_attributes}]")

        while True:
            try:
                user_input = int(input("--> ")) - 1
                if 0 <= user_input <= (ways - 1):
                    break
                else:
                    print("Invalid input. Try Again")
            except ValueError:
                print(f"Invalid input. Enter from 1 to {ways}.")

        combo = self.uniqueCombinations[user_input]
        doc_filter = {}
        while True:
            for index in combo:
                attr = self.attributes[index]
                match attr[1]:
                    case AttrType.STRING:
                        doc_filter[attr[0]] = input(f"Enter {attr[0]} --> ")
                    case AttrType.INTEGER:
                        doc_filter[attr[0]] = int(input(f"Enter {attr[0]} --> "))
                    case AttrType.TIME:
                        hour = int(input(f"Enter {attr[0]}'s hour [0-23] -->  "))
                        minutes = int(input(f"Enter {attr[0]}'s minutes [0-59] --> "))
                        doc_filter[attr[0]] = datetime(2024, 5, 7, hour, minutes, 0)
                    case _:
                        if not isinstance(attr[1], AttrType):
                            print("Ensure that attributes are defined using the correct AttrType values")
                            return

                        print(f"\nSelect {attr[1].value}")
                        doc_filter[attr[0]] = CollectionManager.GetCollection(attr[1].value).selectDoc()["_id"]

            if self.collection.count_documents(doc_filter) != 0:
                break
            else:
                print("Couldn't find a document with attributes: " + str(doc_filter) + "!")

                print("Try Again? [y/n]")
                user_inp = input("--> ")
                while user_inp != 'y' and user_inp != 'n':
                    print("\nInvalid input. Enter 'y' for Yes or 'n' for No.")
                    user_inp = input("--> ")
                print("")

                if user_inp == 'n':
                    return None
        doc = self.collection.find_one(doc_filter)
        if not doc:
            print("No document found with the specified attributes. Try again?")
            user_input = input("--> ")
            if user_input.lower() != 'y':
                return None

        if 'course' in doc:
            course = self.collection.database['courses'].find_one({'_id': doc['course']})
            doc['course'] = course['course_name'] if course else "Unknown Course"

        if 'students' in doc and isinstance(doc['students'], list):
            students = self.collection.database['students'].find({'_id': {'$in': doc['students']}})
            doc['students'] = [f"{student['last_name']}, {student['first_name']}" for student in students]

        if 'courses' in doc:
            course_ids = doc['courses'] if isinstance(doc['courses'], list) else [doc['courses']]
            courses = self.collection.database['courses'].find({'_id': {'$in': course_ids}})
            doc['courses'] = [course['course_name'] for course in courses] if courses else []

        if 'department' in doc:
            department = self.collection.database['departments'].find_one({'_id': doc['department']})
            doc['department'] = department['name'] if department else "Unknown Department"

        return doc

    def buildSelectionCriteria(self):
        print("Available search methods:")
        for i, combo in enumerate(self.uniqueCombinations, start=1):
            fields = ', '.join(self.attributes[idx][0] for idx in combo)
            print(f"{i}. [{fields}]")

        choice = int(input("Choose a method (number): ")) - 1
        if 0 <= choice < len(self.uniqueCombinations):
            return {self.attributes[idx][0]: input(f"Enter {self.attributes[idx][0]}: ") for idx in self.uniqueCombinations[choice]}
        else:
            print("Invalid choice.")
        return None

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, val):
        self._db = val
        self.collection = self.db[self.collectionName]

    @property
    def collectionName(self) -> str:
        return self._collectionName

    @collectionName.setter
    def collectionName(self, value: str):
        self._collectionName = value
        self.collection = self.db[self._collectionName]

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        self._collection = value
