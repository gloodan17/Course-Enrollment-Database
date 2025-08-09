from pymongo import MongoClient
import certifi


class Connect:
    def __init__(self):
        self.m_client = None
        self.m_cluster = self.generateConnectionString()

    def generateConnectionString(self):
        username = input("Username--> ")
        password = input("Password--> ")
        project = input("Project--> ")
        hash_name = input("Hash name--> ")

        return f"mongodb+srv://{username}:{password}@{project}.{hash_name}.mongodb.net/?retryWrites=true&w=majority"

    def connectClient(self):
        self.m_client = MongoClient(self.m_cluster, tlsCAFile=certifi.where())

    @property
    def client(self):
        return self.m_client
