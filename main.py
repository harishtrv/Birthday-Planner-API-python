from flask import Flask, jsonify, request
app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
  userName = db.Column(db.String(30), primary_key=True)
  contactNo = db.Column(db.Integer, unique=True, nullable=False)
  DOB = db.Column(db.Integer, unique=False, nullable=False)
  pw =  db.Column(db.String(20), unique=False, nullable=False)
  def __repr__(self):
    return f"{self.userName} - {self.contactNo} - {self.DOB}"

class Friends(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  userName = db.Column(db.String(30),unique=False, nullable=False)
  friendName = db.Column(db.String(30),unique=False, nullable=False)

@app.route("/getfriends/<userName>")
def getfriends(userName):
  friends = Friends.query.filter_by(userName=userName).all()
  output = []
  for friend in friends:
    user  = User.query.get(friend.friendName)
    if user is not None:
      user_data = {'userName':user.userName,'contactNo':user.contactNo,'DOB':user.DOB}
      output.append(user_data)
  return {'friends':output}

@app.route("/getfriendsuggestion/<userName>")
def getfriendsuggestion(userName):
  friends = Friends.query.filter(Friends.userName.like(userName))
  flist = []
  for friend in friends:
    flist.append(friend.friendName)
  output = []
  users  = User.query.all()
  for user in users:
    if flist.count(user.userName) <= 0 and user.userName!=userName:
      user_data = {'userName':user.userName,'contactNo':user.contactNo,'DOB':user.DOB}
      output.append(user_data)
  return {'suggestedfriends':output}

@app.route("/addfriend", methods=['POST'])
def addfriend():
  friend = Friends(userName=request.json['userName'],friendName=request.json['friendName'])
  db.session.add(friend)
  db.session.commit()
  return {'friendName':friend.friendName}

@app.route("/getallfriends")
def getallfriends():
  friends = Friends.query.all()
  output = []
  for friend in friends:
    user_data = {'userName':friend.userName,'friend':friend.friendName}
    output.append(user_data)
  return {'FriendsList':output}

@app.route("/getallusers")
def getallusers():
  users = User.query.all()
  output = []
  for user in users:
    user_data = {'userName':user.userName,'contactNo':user.contactNo,'DOB':user.DOB}
    output.append(user_data)
  return {'users':output}

@app.route("/getusers/<userName>")
def getusers(userName):
  user = User.query.get(userName)
  return {"userName": user.userName,"conactNo":user.contactNo, "DOB":user.DOB, "PW":user.pw}

@app.route("/adduser", methods=['POST'])
def adduser():
  user = User(userName=request.json['userName'],contactNo=request.json['contactNo'],DOB=request.json['DOB'], pw=request.json['pw'])
  db.session.add(user)
  db.session.commit()
  return {'userName':user.userName}

@app.route("/deleteuser/<userName>", methods=['DELETE'])
def deleteuser(userName):
  user  = User.query.get(userName)
  if user is None:
    return {"error":"not found"}
  db.session.delete(user)
  db.session.commit()
  return {"userName": user.userName,"conactNo":user.contactNo, "DOB":user.DOB}

@app.route("/authenticate/<userName>/<pw>")
def authenticate(userName, pw):
  user = User.query.get(userName)
  if user is None:
    return {"error":"not found"}
  if(user.pw == pw):
    return {"message":"success"}
  return {"message":"wrong password"}

@app.route("/")
def hello():
  db.create_all()
  return "<p>Hello</p>"

if __name__ == "__main__":
    app.run(debug=True)