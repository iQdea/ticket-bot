from entity.mongo import Mongo
from entity.personEntity import PersonEntity
check = 'MVCP,MV,CP,20'.split(',')
ans = Mongo.client.get_collection('person')
print(check[0], check[1], check[2], check[3])
print(ans.count_documents({'username' : check[0], 'first_name' : check[1], 'last_name' : check[2], 'age' : int(check[3])}))
passwd = list(ans.find({'username' : check[0], 'first_name' : check[1], 'last_name' : check[2], 'age' : int(check[3])}))
print()