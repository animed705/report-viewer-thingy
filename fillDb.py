from report import db, bcrypt
from report.models import User

db.create_all()
for i in range(1,7):
    st_pwd = bcrypt.generate_password_hash( "sss"+str(i)).decode('utf-8')
    st_usr = User (username = "student"+str(i), userType = "student",
                 theClass = str(i), password=st_pwd )
    
    te_pwd = bcrypt.generate_password_hash("ttt"+str(i)).decode('utf-8')
    te_usr = User (username = "teacher"+str(i), userType = "teacher",
                 theClass = str(i), password=te_pwd  )
    
    db.session.add(te_usr)
    db.session.add(st_usr)
    db.session.commit()



admin_pwd = bcrypt.generate_password_hash("cardinal").decode('utf-8')
admin = User (username = "cardinal", userType = "admin", password=admin_pwd  )
db.session.add(admin)
db.session.commit()
print("users: " , User.query.all())
print("dummy data created:")




# from report.models import db, User