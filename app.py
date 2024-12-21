from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import update

def user(name: str) -> str:
    result = name
    if(not name.isalpha()):
        result = ''.join(i for i in name if i.isalpha())
    elif(name.islower()):
        result = name.upper()
    elif(name.isupper()):
        result = name.lower()
    else:
        result = name.capitalize()
    return result

app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.config['SECRET_KEY'] = '8acdcb77674689d0da3a7be8f12608cb5283669aad4d9a351f94f4cbc0d1d577'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///course-website.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 15)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
class Grade(db.Model):
    __tablename__ = 'Grade'
    id = db.Column(db.Integer, primary_key = True)
    stud_id = db.Column(db.Integer, nullable=False)
    inst_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Double, nullable=False)
    full = db.Column(db.Double, nullable=False)
    remark = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Grade('{self.title}', '{self.score}')"

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    id = db.Column(db.Integer, primary_key = True)
    inst_id = db.Column(db.Integer, nullable=False)
    q1 = db.Column(db.String(250))
    q2 = db.Column(db.String(250))
    q3 = db.Column(db.String(250))
    q4 = db.Column(db.String(250))

    def __repr__(self):
        return f"Feedback('{self.id}')"


class Regrade(db.Model):
    __tablename__ = 'Regrade'
    id = db.Column(db.Integer, primary_key = True)
    grade_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(250))

    def __repr__(self):
        return f"Regrade('{self.id}', '{self.grade_id}', '{self.reason}')"

@app.route("/")
def index():
    return render_template("index.html",
                           page_title = "CSCB20 Course Webpage")

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html",
                            page_title = "CSCB20 Register")
    else:
        password = request.form['password']
        if password != request.form['confirm']:
            flash('Password does not match.', 'error')
            return redirect(url_for('register'))
        username = request.form['username']
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        type = request.form['identity']
        reg_details = (
            username,
            email,
            firstname,
            lastname,
            hashed_password,
            type
        )
        add_user(reg_details)
        flash('Registration Successful! Please login now:', 'notice')
        return redirect(url_for('login'))

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'name' in session:
            return redirect(url_for('home'))
        else:
            return render_template("login.html",
                                   page_title = "CSCB20 Login")
    else:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            flash('Incorrect username or password.', 'error')
            return render_template('login.html',
                                   page_title = "CSCB20 Login")
        else:
            session['name'] = username
            session.permanent = True
            return redirect(url_for('home'))

@app.route("/home")
def home():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(username = session['name']).first()
        name = user.first_name
        return render_template("home.html", 
                            message = "Welcome, %s, to my CSCB20 website!" % name,
                            page_title = "CSCB20 Course Webpage",
                            current_page_name = "HOME")

@app.route("/<username>")
def withname(username):
    name = user(username)
    return render_template("home.html", 
                           message = "Welcome, %s, to my CSCB20 website!" % name,
                           page_title = "CSCB20 Course Webpage",
                           current_page_name = "HOME")

@app.route("/calendar")
def calendar():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        return render_template("calendar.html",
                            page_title = "CSCB20 Calendar",
                            current_page_name = "CALENDAR")

@app.route("/news")
def news():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        return render_template("news.html",
                            page_title = "CSCB20 News",
                            current_page_name = "NEWS")

@app.route("/grades")
def grades():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(username = session['name']).first()
        grades = []
        if(user.type == 'student'):
            grades = stud_query_grades(user.id)
            return render_template("stud_grades.html",
                                    page_title = "CSCB20 Grades",
                                    current_page_name = "GRADES",
                                    grades = grades)
        elif(user.type == 'instructor'):
            grades = inst_query_grades(user.id)
            return render_template("inst_grades.html",
                                    page_title = "CSCB20 Grades",
                                    current_page_name = "GRADES",
                                    grades = grades)
        else:
            flash('Invalid user.', 'error')
            return redirect(url_for('login'))


@app.route("/regrade_request", methods = ['GET', 'POST'])
def regrade():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username = session['name']).first()

    if(user.type == 'student'):
        if(request.method == 'GET'):
            grades = stud_query_grades(user.id)
            return render_template("stud_regrade.html",
                                page_title = "CSCB20 Regrade Request",
                                current_page_name = "REGRADE REQUEST",
                                grades = grades)
        else:
            grade_id = request.form['title']
            reason = request.form['reason']
            rg_detail = (grade_id, reason)
            add_regrade(rg_detail, grade_id)
            return redirect(url_for('grades'))
    elif(user.type == 'instructor'):
        if(request.method == 'GET'):
            grades = inst_query_regrades(user.id)
            return render_template("inst_regrade.html",
                                page_title = "CSCB20 Regrade Request",
                                current_page_name = "REGRADE REQUEST",
                                grades = grades)
        else:
            id = request.form['id']
            score = request.form['score']
            regrade = request.form['regrade']
            rg_details = (int(id), score)
            if(regrade == "False"):
                update_grade(rg_details)
            return redirect(url_for('regrade'))

@app.route("/enter_marks", methods = ['GET', 'POST'])
def mark():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username = session['name']).first()

    if(user.type == 'student'):
        flash('Access denied.', 'error')
        return redirect(url_for('login'))

    else:
        if(request.method == 'GET'):
            return render_template("inst_marks.html",
                                page_title = "CSCB20 Enter Marks",
                                current_page_name = "ENTER MARKS")
        else:
            stud_id = request.form['stud_id']
            title = request.form['title']
            score = request.form['score']
            full = request.form['full']
            mk_details = (stud_id, user.id, title, score, full)
            add_grade(mk_details)
            return redirect(url_for('grades'))

@app.route("/lectures")
def lectures():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        return render_template("lectures.html",
                            page_title = "CSCB20 Lectures",
                            current_page_name = "LECTURES")
    
@app.route("/labs")
def labs():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        return render_template("labs.html",
                            page_title = "CSCB20 Labs",
                            current_page_name = "LABS")

@app.route("/assignments")
def assignments():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        return render_template("assignments.html",
                            page_title = "CSCB20 Assignments",
                            current_page_name = "ASSIGNMENTS")

@app.route("/tests")
def tests():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        return render_template("tests.html",
                            page_title = "CSCB20 Tests",
                            current_page_name = "TESTS")

@app.route("/resources")
def resources():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        return render_template("resources.html",
                            page_title = "CSCB20 Resources",
                            current_page_name = "RESOURCES")

@app.route("/feedback", methods = ['GET', 'POST'])
def feedback():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(username = session['name']).first()
        if(user.type == 'student'):
            if request.method == 'GET':
                instructors = User.query.filter_by(type = 'instructor').all()
                return render_template("stud_feedback.html",
                                        page_title = "CSCB20 Anonymous Feedback",
                                        current_page_name = "FEEDBACK",
                                        instructors = instructors)
            else:
                inst_id = request.form['instructor']
                q1 = request.form['q1']
                q2 = request.form['q2']
                q3 = request.form['q3']
                q4 = request.form['q4']
                fb_details = (
                    inst_id,
                    q1,
                    q2,
                    q3,
                    q4
                )
                add_feedback(fb_details)
                return redirect(url_for('home'))
        elif(user.type == 'instructor'):
            feedback = Feedback.query.filter_by(inst_id = user.id).all()
            return render_template("inst_feedback.html",
                           page_title = "CSCB20 Anonymous Feedback",
                           current_page_name = "FEEDBACK",
                           feedback = feedback)
        else:
            flash('Invalid user.', 'error')
            return redirect(url_for('login'))

@app.route("/course_team")
def courseteam():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        return render_template("courseteam.html",
                            page_title = "CSCB20 Course Team",
                            current_page_name = "COURSE TEAM")

@app.route("/profile")
def profile():
    if 'name' not in session:
        flash('Access denied.', 'error')
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(username = session['name']).first()
        return render_template("profile.html",
                               user = user,
                               page_title = "CSCB20 User Detail",
                               current_page_name = "User Detail")

@app.route('/logout')
def logout():
    session.pop('name', default = None)
    return redirect(url_for('index'))

def stud_query_grades(id):
    grades = Grade.query.filter_by(stud_id = id).all()
    return grades

def inst_query_grades(id):
    grades = db.session.query(Grade, User).join(User, Grade.stud_id == User.id).filter(Grade.inst_id == id).all()
    return grades

def inst_query_regrades(id):
    grades = db.session.query(Grade, Regrade).join(Regrade, Grade.id == Regrade.grade_id).filter(Grade.inst_id == id).filter(Grade.remark == True).all()
    return grades

def add_user(reg_details):
    user = User(username = reg_details[0], 
                email = reg_details[1], 
                first_name = reg_details[2], 
                last_name = reg_details[3], 
                password = reg_details[4], 
                type = reg_details[5])
    db.session.add(user)
    db.session.commit()

def add_feedback(fb_details):
    feedback = Feedback(inst_id = fb_details[0], 
                q1 = fb_details[1], 
                q2 = fb_details[2], 
                q3 = fb_details[3], 
                q4 = fb_details[4])
    db.session.add(feedback)
    db.session.commit()

def add_grade(mk_details):
    grade = Grade(stud_id = mk_details[0],
                  inst_id = mk_details[1],
                  title = mk_details[2],
                  score = mk_details[3],
                  full = mk_details[4],
                  remark = False)
    db.session.add(grade)
    db.session.commit()

def add_regrade(rg_details, grade_id):
    regrade = Regrade(grade_id = rg_details[0], 
                      reason = rg_details[1])
    db.session.add(regrade)
    Grade.query.filter_by(id = grade_id).update(dict(remark = True))
    db.session.commit()

def update_grade(rg_details):
    Grade.query.filter_by(id = rg_details[0]).update({'score': rg_details[1]})
    Grade.query.filter_by(id = rg_details[0]).update(dict(remark = False))
    db.session.commit()

@app.route("/syllabus.pdf")
def syllabus():
    return send_from_directory('./src/pdf', 'syllabus.pdf')

@app.route("/lectures/w1.pdf")
def w1l():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w1_handout.pdf")
def w1h():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w3.pdf")
def w3l():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w3_worksheet.pdf")
def w3w():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w3_worksheet_solution.pdf")
def w3s():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w4.pdf")
def w4l():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w4_handout.pdf")
def w4h():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w4_worksheet.pdf")
def w4w():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w5.pdf")
def w5l():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w5_handout.pdf")
def w5h():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w5_worksheet.pdf")
def w5w():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w5_worksheet_solution.pdf")
def w5s():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w6.pdf")
def w6l():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w6_worksheet.pdf")
def w6w():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w6_worksheet_solution.pdf")
def w6s():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w7.pdf")
def w7l():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w8.pdf")
def w8l():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w9.pdf")
def w9l():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w10.pdf")
def w10l():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w11.pdf")
def w11l():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w11_handout.pdf")
def w11h():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/lectures/w16_final.pdf")
def w12():
    return send_from_directory('./src/pdf', 'lecture.pdf')

@app.route("/labs/tutorial_1_handout.pdf")
def t1h():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_2_handout.pdf")
def t2h():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_3_handout.pdf")
def t3h():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_3_sql.pdf")
def t3d():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_3_solution.pdf")
def t3s():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_4_handout.pdf")
def t4h():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_4_solution.pdf")
def t4s():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_5_handout.pdf")
def t5h():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_5_solution.pdf")
def t5s():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_6_handout.pdf")
def t6h():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_7_handout.pdf")
def t7h():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_8_handout.pdf")
def t8h():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_9_handout.pdf")
def t9h():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/tutorial_10_handout.pdf")
def t10h():
    return send_from_directory('./src/pdf', 'tutorial.pdf')

@app.route("/labs/assignment_1_handout.pdf")
def a1h():
    return send_from_directory('./src/pdf', 'assignments.pdf')

@app.route("/labs/assignment_1_solution.pdf")
def a1s():
    return send_from_directory('./src/pdf', 'assignments.pdf')

@app.route("/labs/assignment_1_dumpfile")
def a1f():
    return send_from_directory('./src/pdf', 'assignments.pdf')

@app.route("/labs/assignment_2_handout.pdf")
def a2h():
    return send_from_directory('./src/pdf', 'assignments.pdf')

@app.route("/labs/assignment_2_starter_code")
def a2c():
    return send_from_directory('./src/pdf', 'assignments.pdf')

@app.route("/labs/assignment_3_mark_scheme")
def a3ms():
    return send_from_directory('./src/pdf', 'assignments.pdf')

@app.route("/labs/assignment_3_handout")
def a3h():
    return send_from_directory('./src/pdf', 'assignments.pdf')

@app.route("/tests/testA")
def midterm():
    return send_from_directory('./src/pdf', 'midterm.pdf')

if __name__ == "__main__":
    app.run(debug=True)