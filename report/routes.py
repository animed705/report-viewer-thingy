from flask import render_template,request,url_for,redirect , session, flash, send_file
from report import app, db, bcrypt
from flask_wtf.csrf import CSRFProtect
from requests import sessions
from report.models import User
import os
from io import BytesIO
from report.forms import CreateAccount, LoginForm, UploadForm, UpdateForm
from flask_login import login_user, current_user, logout_user, login_required


csrf = CSRFProtect(app)
#admin page to edit user data
@app.route("/admin", methods = ["POST", "GET"])
@login_required
def admin():
    usr = None
    form  = UpdateForm()
    if current_user.userType == "admin":
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
        if form.validate_on_submit(): #elif request.form["edit"]:
            print("valid now")
            updateUsr = User.query.filter_by(username = session['toUpdate']).first()
            print("name_in_form:", form.username.data)
            updateUsr.username = form.username.data 
            updateUsr.theClass = form.theClass.data 

            db.session.commit()
            print("after update:",updateUsr.username)
            # flash("data updated", "info")

        return render_template("admin.html", result = usr, form = form)

#we'll remove this at the end
@app.route('/create', methods= ["POST", "GET"])      
def create():
    # if current_user.is_authenticated:
    #    return redirect(url_for("home"))
    form = CreateAccount()
    if form.validate_on_submit():
        enc_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password = enc_password, userType = request.form["accountType"])
        db.session.add(user)
        db.session.commit()
        flash(f'Woohoo! Welcome {form.username.data} !', 'success')
        return  redirect(url_for("login"))
    return render_template("create.html", title='Register', form = form)


#home page  for login
@app.route("/", methods= ["POST", "GET"])        
def login():
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
            flash("you are logged in ", "success")
            if current_user.userType == "teacher":
                return redirect(url_for("uploadResult"))

            elif current_user.userType == "admin":
             return redirect(url_for("admin"))
           
            else:
                return redirect(url_for("studentReport"))
            
                    
        else:
            flash("Wrong username or password, check again.", "danger") 
    return render_template("login.html", title='Login', form = form)



#secure file upload or just make a function instead of a route
@app.route('/student_report/<getId>/<attach>', methods=["POST", "GET"])
@login_required
def download(getId, attach):
    # print( request.args.get("attach"))
    # print("download_stud-id:",request.form["student_id"])
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
    

    if current_user.userType == "student":
        report = User.query.filter_by(id = current_user.id).first()
        return render_template("student_report.html", file = report.fileName)
    elif current_user.userType == "teacher":
        return redirect(url_for("uploadResult"))
    
#function to save file 
def save_file(result_file, name):
   
    fileToSave = name + "_result." + str(result_file.filename).split('.')[1]
    
    save_path = os.path.join(app.root_path, 'student_results',fileToSave)
    result_file.save(save_path)
    return fileToSave


@app.route("/upload_result", methods=["POST", "GET"])   
@login_required     
def uploadResult():
    
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
            flash("File upload successful", "success ")
            print("file uploaded:" )
        
        else:
            flash("no file selected", "danger")
    studentList = User.query.filter_by(userType="student", theClass = current_user.theClass).all()  
    if current_user.userType == "teacher":
        return render_template("upload_result.html", title="upload result", 
                         student = studentList,form=form)#, filename=filename)
    elif current_user.userType == "student":
        flash("huhuhuh, thought you were smarter kid?", "danger")
        return redirect(url_for("studentReport"))


@app.route("/logout")        
def logout():
    logout_user()
    return redirect(url_for("login"))

    