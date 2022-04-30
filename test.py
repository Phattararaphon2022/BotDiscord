import db

data = db.getallUser()
for i in data:
    print(i['username'])