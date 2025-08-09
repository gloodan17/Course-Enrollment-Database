class CollectionManager:
    _collections = {}

    @staticmethod
    def AddCollection(collection_name, collection):
       CollectionManager._collections[collection_name] = collection

    @staticmethod
    def GetCollection(collection_name):
        return CollectionManager._collections[collection_name]
