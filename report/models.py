from report import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    username = db.Column(db.String(20), nullable = False)
    password = db.Column(db.String(20), nullable=False)
    # studentReport = db.relationship('Report',backref = 'viewer', lazy = True )
    userType = db.Column(db.String(10), nullable=False)
    theClass = db.Column(db.String())
    fileName = db.Column(db.String())
    fileData = db.Column(db.LargeBinary)

    
    def __repr__(self):
        return f"User('{self.username}','{self.id}',{self.userType}, {self.theClass}, {self.fileName})"


