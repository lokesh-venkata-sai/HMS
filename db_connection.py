import pymongo


url = 'mongodb://localhost:27017'
my_client = pymongo.MongoClient(url)
db = my_client['test_mongo']
# collist = db.list_collection_names()

