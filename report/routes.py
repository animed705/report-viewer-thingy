import json
from multiprocessing import dummy
from re import S
from flask import jsonify, render_template, render_template_string,request,url_for,redirect , session, flash, send_file
from sqlalchemy import null
from report import app, db, bcrypt
from flask_wtf.csrf import CSRFProtect
from requests import sessions
from report.models import User
import os
from io import BytesIO
from report.forms import CreateAccount, LoginForm, UploadForm, UpdateForm
from flask_login import login_user, current_user, logout_user, login_required
from fillDb import createDb

csrf = CSRFProtect(app)
# create student dummy data json file

student_dummy_data = {
   "class_1":{ "students": [
               
                    {"admission_no": 1, "name": "tewo", "marks": {
                                                    "test_1":{"maths": null, "english": null, "science": null},
                                                    "test_2":{"maths": null, "english": null, "science": null},}
                    },
                    
                    {"admission_no": 2, "name": "naruto", "marks": {
                                                    "test_1":{"maths": null, "english": null, "science": null},
                                                    "test_2":{"maths": null, "english": null, "science": null},}
                    },
         ]
   },
   
   
     "class_2":{"students": [
         
                    {"admission_no": 1, "name": "tewo", "marks": {
                                                    "test_1":{"maths": null, "english": null, "science": null},
                                                    "test_2":{"maths": null, "english": null, "science": null},}
                    },
                    
                    {"admission_no": 2, "name": "naruto", "marks": {
                                                    "test_1":{"maths": null, "english": null, "science": null},
                                                    "test_2":{"maths": null, "english": null, "science": null},}
                    },
                
                    {"admission_no": 3, "name": "thre", "marks": {
                                                    "test_1":{"maths": null, "english": null, "science": null},
                                                    "test_2":{"maths": null, "english": null, "science": null},}
                    },
                
                    {"admission_no": 4, "name": "four", "marks": {
                                                    "test_1":{"maths": null, "english": null, "science": null},
                                                    "test_2":{"maths": null, "english": null, "science": null},}
                    },                   
                ]
   },
   
   
}
                    
teacher_dummy_data={
    "teacher_1":{
                "teacher_id": 1,
                "password":"pass#teacher_1",
                "classes":["class_1-english",                              
                         ]      
                },
    
    "teacher_2":{
                "teacher_id": 2,
                "password":"pass#teacher_2",
                 "classes":["class_1-english", 
                            "class_2-science",              
                         ]                     
                }  
}
    
    
@app.route('/')
def class_test():
    username="teacher_2" #get from login id
    teacher_subjects=teacher_dummy_data[username]["classes"]
    test_list=["test_1","test_2", "test_3", "test_4"]	
    
    return render_template('class_navigation.html', classes=teacher_subjects, test_list=test_list)
        
     

@app.route('/marks_entry/<grade>/<subject>/<test_name>', methods=['GET', 'POST'])
def upload_marks_page(grade, subject, test_name):
    # grade = "class_2" #get it from teacher's user data
    # subject="maths" #get it from nav page
    # test_name = "test_1" #get it from nav page
    # # student_list=student_dummy_data[grade-1]["class_2"]
    student_list  = student_dummy_data[grade]["students"]
    # print(student_list)
    if request.method == 'POST':
        for student in student_dummy_data[grade]["students"]:
            # print(f"Name:{student['name']}, Marks_from:{request.form[str(student['admission_no'])]}")
            student['marks'][test_name][subject] = request.form[str(student['admission_no'])] 

        return redirect(url_for('class_result', grade=grade))
        # for student in student_dummy_data[grade]["students"]:
        #     print("---------------------")
        #     print(f"Name: {student['name']} Score:{student['marks'][test_name][subject]}")            
        #     print("---------------------")
            
    return render_template('upload_marks.html', subject=subject, test_name=test_name, grade=grade, student_list=student_list)
    #return render_template('class_test.html')

@app.route('/class_result/<grade>')
def class_result(grade):
    student_list = student_dummy_data[grade]["students"]
    print(student_list)
    return render_template('class_result.html')
    # return  jsonify(student_dummy_data[grade]["students"])
    # return(jsonify({student_list}))
    # return (student_dummy_data)
    





#admin page to edit user data
@app.route("/admin", methods = ["POST", "GET"])
@login_required
def admin():
    usr = None
    form  = UpdateForm()
    if current_user.userType == "admin":
        try:
            if request.method == "POST":
                if request.form["admin"]:
                    session['toUpdate'] = request.form["admin"]
                    usr = User.query.filter_by(username = session['toUpdate']).first()
                    print(request.form["admin"])
                    if usr:
                        form.username.data = usr.username
                        form.theClass.data = usr.theClass
                        form.userType = usr.userType
                    else:
                        return render_template("admin.html", result = usr, form = form)
                    # return url_for("admin")
            
                elif form.validate_on_submit(): 
                    print("valid now")
                    updateUsr = User.query.filter_by(username = session['toUpdate']).first()
                    print("name_in_form:", form.username.data)
                    updateUsr.username = form.username.data 
                    updateUsr.theClass = form.theClass.data 

                    db.session.commit()
                    print("after update:",updateUsr.username)
                    # print("got user admission_no:", request.form["userId"])
                    flash("Data Updated Successfully", "success")
        except:
            return render_template("error.html")
    else:
        return redirect(url_for("login"))


    return render_template("admin.html", result = usr, form = form)


#admin can ad dnew user
@app.route('/create', methods= ["POST", "GET"])      
def create():
    form = CreateAccount()
    if current_user.userType == "admin":
        if form.validate_on_submit():
            try:
                pwd = "pass#" +form.username.data.split(' ')[0]
                enc_password = bcrypt.generate_password_hash(pwd).decode('utf-8')
                user = User(username=form.username.data, password = enc_password,
                userType = request.form["accountType"], theClass = form.theClass.data)
                db.session.add(user)
                db.session.commit()
                flash("New User added to the Database", 'success')
                # print(f"pass: {pwd}, name:{form.username.data}, class:{form.theClass.data}, type:{request.form['accountType']}")
                return  redirect(url_for("create"))
            except:
                return render_template("error.hmtl")
        return render_template("create.html", title='Register', form = form)
    
    else:
        return redirect(url_for("login"))

       


#home page  for login
@app.route("/login", methods= ["POST", "GET"])        
def login():
    try:
        if current_user.is_authenticated:
            if current_user.userType == "teacher":
                return redirect(url_for("uploadResult"))

            elif current_user.userType == "student":
                    return redirect(url_for("studentReport"))

            elif current_user.userType == "admin":
                return redirect(url_for("admin"))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            # theClass = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):# and theClass.theClass == request.form["theClass"]:
                login_user(user,remember = form.remember.data)
                flash("Logged in Successfully", "success")
                if current_user.userType == "teacher":
                    return redirect(url_for("uploadResult"))

                elif current_user.userType == "admin":
                    return redirect(url_for("admin"))
            
                else:
                    return redirect(url_for("studentReport"))
                
                        
            else:
                flash("Wrong username or password, check again.", "danger") 
    except:
        return render_template("error.html")
  
    return render_template("login.html", title='Login', form = form)



#secure file upload or just make a function instead of a route
@app.route('/student_report/<getId>/<attach>', methods=["POST", "GET"])
@login_required
def download(getId, attach):
    # print( request.args.get("attach"))
    # print("download_stud-admission_no:",request.form["student_id"])
    user = User.query.filter_by(id = getId).first() 
    print(attach)
    print(user)
    return send_file(BytesIO(user.fileData), attachment_filename=user.fileName, as_attachment= attach )




@app.route("/student_report", methods=["GET"])   
@login_required     
def studentReport():
    # saving in file system
    # if current_user.fileName:
    #     with open(os.getcwd()+'/report/student_results/'+ f"{current_user.fileName}" ,'wb') as pen:
    #         pen.write(current_user.fileData)
    
    try:
        if current_user.userType == "student":
            report = User.query.filter_by(id = current_user.id).first()
            return render_template("student_report.html", file = report.fileName)
        elif current_user.userType == "teacher":
            return redirect(url_for("uploadResult"))
    except:
        return render_template("error.html")

    


@app.route("/upload_result", methods=["POST", "GET"])   
@login_required     
def uploadResult():
    try:
        form = UploadForm()
        if form.validate_on_submit():
            print("form submit validated")
            if form.resultFile.data:
                print("file has data rn")
                studentReport = User.query.filter_by(id = request.form["student_id"]).first()
                # resultFile = save_file(form.resultFile.data, name = studentReport.username )
                print("kid Id:", request.form["student_id"])
                studentReport.fileName = studentReport.username+"_result." + str(form.resultFile.data.filename).split('.')[1]#resultFile
                studentReport.fileData = form.resultFile.data.read()
                db.session.commit()
                flash("File Successfully Uploaded.", "success ")
                print("file uploaded:" )
            else:
                flash("Please select a file.", "danger")
        studentList = User.query.filter_by(userType="student", theClass = current_user.theClass).all()  
        if current_user.userType == "teacher":
            return render_template("upload_result.html", title="upload result", 
                            student = studentList,form=form)#, filename=filename)
        elif current_user.userType == "student":
            flash("huhuhuh, thought you were smarter kid?", "danger")
            return redirect(url_for("studentReport"))
        else:
            studentList = User.query.filter_by(userType="student").all()
            return render_template("upload_result.html", title="upload result", 
                            student = studentList,form=form)
    except:
        return render_template("error.html")



#function to save file 
def save_file(result_file):
    fileToSave = "all_data.csv"
    save_path = os.path.join(app.root_path, 'school_data',fileToSave)
    result_file.save(save_path)
    return fileToSave

#need to add steps to maake sure proper entry
#make sure admin data is mentioned
@app.route("/updateDb", methods=["POST", "GET"])   
@login_required     
def updateDatabase():
    form = UploadForm()
    if current_user.userType == "admin":
        # try:
        if form.validate_on_submit():
            save_file(form.resultFile.data)
            # flash("Please wait till we comeplete adding everything...", "success")
            createDb()
            flash("Database Creation Complete ! ", "success")
            print("file uploaded:" )
            return redirect(url_for("admin"))
        
        else:
            flash("Please select the file. After uploading it takes a while, So please wait...", "danger")   
        # except:
        #     return render_template("error.html")
        return render_template("updateDatabase.html", form = form)
    


@app.route("/logout")        
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/delete/<id>")   
@login_required     
def delete(id):
    if current_user.userType == "admin":
        User.query.filter_by(id=id).delete()
        db.session.commit()
        # print("usr deleted")
        flash("User deleted from the Database", "danger")
    return redirect(url_for("admin"))

    
    

    