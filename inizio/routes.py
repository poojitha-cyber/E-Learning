from inizio import app
from flask import render_template,redirect,url_for,flash,request
from inizio.models import Item,User
from inizio.forms import RegisterForm,LoginForm,EnrollCourseForm
from inizio import db
from flask_login import login_user,logout_user,login_required,current_user
from inizio.models import Enrollment
from pytz import timezone
import pytz
from inizio.models import Question
from inizio.models import TestResult
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html') 
@app.route('/courses',methods=['GET','POST'])
@login_required
def courses_page():
    enroll_form=EnrollCourseForm()
    if request.method=="POST":
        enrolled_course=request.form.get('enrolled_course')
        e_course_object=Item.query.filter_by(name=enrolled_course).first()
        if e_course_object:
            existing_enrollment=Enrollment.query.filter_by(user_id=current_user.id,course_id=e_course_object.id).first()
            if not existing_enrollment:
                enrollment=Enrollment(user_id=current_user.id,course_id=e_course_object.id)
                db.session.add(enrollment)
                current_user.courses_enrolled+=1
                db.session.commit()
                flash(f"You have successfully enrolled in {enrolled_course}!", category='success')
            else:
                flash(f"You are already enrolled in {enrolled_course}.", category='info')
        else:
            flash("Course not found!", category='danger')
        return redirect(url_for('dashboard'))
    all_courses=Item.query.all()
    enrolled_course_ids=[enrollment.course_id for enrollment in Enrollment.query.filter_by(user_id=current_user.id).all()]
    avaliable_courses=[course for course in all_courses if course.id not in enrolled_course_ids]
    return render_template('courses.html',items=avaliable_courses,enroll_form=enroll_form)
@app.route('/register',methods=['GET','POST'])
def register_page():
    form=RegisterForm()
    if form.validate_on_submit():
        user_to_create=User(username=form.username.data,email_address=form.email_address.data,password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully and you are logged in as: {user_to_create.username}",category='success')
        return redirect(url_for('courses_page'))
    if form.errors!={}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user:{err_msg}',category='danger')
    return render_template('register.html', form=form)
@app.route('/login',methods=['GET','POST'])
def login_page():
    form=LoginForm()
    if form.validate_on_submit():
        attempted_user=User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f"Success! You are logged in as: {attempted_user.username}",category="success")
            return redirect(url_for('courses_page'))
        else:
            flash("Username and password are not match! Please try again.",category='danger')
    return render_template('login.html',form=form)
@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!",category='info')
    return redirect(url_for('home_page'))
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    enrolled_courses = []
    user_timezone = timezone('Asia/Kolkata')

    for enrollment in enrollments:
        # Convert UTC time to user local time
        utc_dt = enrollment.date_enrolled.replace(tzinfo=pytz.utc)
        local_dt = utc_dt.astimezone(user_timezone)

        # Get course information once
        course = Item.query.get(enrollment.course_id)

        # Check if the user already has a test result
        existing_result = TestResult.query.filter_by(user_id=current_user.id, course_id=enrollment.course_id).first()

        # Build course info dictionary
        enrolled_courses.append({
            'course_id': enrollment.course_id,
            'name': course.name,
            'course_code': course.code,
            'date_enrolled': local_dt.strftime('%d-%m-%Y %I:%M %p'),
            'result_exists': True if existing_result else False   # <- correct spelling
        })

    return render_template('dashboard.html', enrollments=enrolled_courses)
@app.route('/take_test/<int:course_id>', methods=['GET', 'POST'])
@login_required
def take_test(course_id):
    course = Item.query.get_or_404(course_id)

    # Check if user already attempted the test
    existing_result = TestResult.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    if existing_result:
        # If already taken, redirect to view result
        return redirect(url_for('view_result', course_id=course.id))

    questions = Question.query.filter_by(course_id=course_id).all()

    if request.method == 'POST':
        answers = {}
        for question in questions:
            selected_option = request.form.get(f'q{question.id}')
            answers[question.id] = selected_option

        correct = incorrect = unattempted = 0
        for question in questions:
            selected_option = answers.get(question.id)
            
            # Get the actual correct answer text
            correct_answer_text = getattr(question, question.correct_option)

            if selected_option is None or selected_option.strip() == '':
                unattempted += 1
            elif selected_option.strip().lower() == correct_answer_text.strip().lower():
                correct += 1
            else:
                incorrect += 1

        # Save the test result to the database
        result = TestResult(
            user_id=current_user.id,
            course_id=course.id,
            correct=correct,
            incorrect=incorrect,
            unattempted=unattempted,
            total=len(questions)
        )
        db.session.add(result)
        db.session.commit()

        return redirect(url_for('view_result', course_id=course.id))
    return render_template('take_test.html', course=course, questions=questions)
@app.route('/view_result/<int:course_id>')
@login_required
def view_result(course_id):
    course = Item.query.get_or_404(course_id)
    result = TestResult.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    if not result:
        flash('You have not attempted the test yet!', 'warning')
        return redirect(url_for('take_test', course_id=course.id))
    marks_per_question = 4
    total_marks = result.correct * marks_per_question
    return render_template('view_result.html', course=course, result=result, total_marks=total_marks)
@app.route('/view_overall_progress')
@login_required
def view_overall_progress():
    # Fetch all test results for the current user
    results = TestResult.query.filter_by(user_id=current_user.id).all()

    # Prepare data for the bar graph
    course_names = []
    marks = []
    marks_per_question = 4  # Each correct answer carries 4 marks

    for result in results:
        course = Item.query.get(result.course_id)
        course_names.append(course.name)
        marks.append(result.correct * marks_per_question)

    return render_template('view_overall_progress.html', course_names=course_names, marks=marks)

