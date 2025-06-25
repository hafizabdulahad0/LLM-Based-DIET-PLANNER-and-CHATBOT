import os
from datetime import datetime
from io import BytesIO

import pandas as pd
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash,
    send_file, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, UserProfile, DailyRecord, ChatMessage
from utils import (
    calculate_bmi,
    get_daily_diet_plan,
    get_daily_exercise_plan,
    analyze_food,
    get_chat_response
)

load_dotenv()
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY'),
    SQLALCHEMY_DATABASE_URI='sqlite:///database.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
db.init_app(app)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

with app.app_context():
    db.create_all()


def calculate_streak(records):
    sorted_days = sorted([r.day_number for r in records if r.exercise])
    streak = 0
    for i in reversed(range(len(sorted_days))):
        if i == 0 or sorted_days[i] - sorted_days[i - 1] == 1:
            streak += 1
        else:
            break
    return streak


@app.route('/')
def home():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        error = 'Invalid email or password'
    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None

    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            pwd   = request.form.get('password', '')

            # 1) Duplicate‐email check
            if User.query.filter_by(email=email).first():
                raise ValueError("An account with that email already exists.")

            # 2) Password length
            if len(pwd) < 6:
                raise ValueError("Password must be at least 6 characters.")

            # 3) Height → cm
            feet   = int(request.form.get('height_feet', 0))
            inches = int(request.form.get('height_inches', 0))
            if not (3 <= feet <= 8 and 0 <= inches <= 11):
                raise ValueError("Height must be between 3–8 ft and 0–11 in.")
            total_inches = feet * 12 + inches
            height_cm    = round(total_inches * 2.54)

            # 4) Age & weight
            age = int(request.form.get('age', 0))
            if not (13 <= age <= 100):
                raise ValueError("Age must be between 13 and 100.")
            weight = float(request.form.get('weight', 0))
            if not (30 <= weight <= 300):
                raise ValueError("Weight must be between 30 and 300 kg.")

            # 5) Create User (note `password=` matches your model) :contentReference[oaicite:0]{index=0}
            user = User(
                email=email,
                password=generate_password_hash(pwd)
            )
            db.session.add(user)
            db.session.commit()

            # 6) Create Profile (no budget) :contentReference[oaicite:1]{index=1}
            profile = UserProfile(
                user_id=user.id,
                name=request.form.get('name', '').strip(),
                age=age,
                height=height_cm,
                weight=weight,
                gender=request.form.get('gender'),
                disease=request.form.get('disease', '').strip(),
                diet_preference=request.form.get('diet_preference'),
                goal=request.form.get('goal'),
                cuisine=request.form.get('cuisine', '').strip()
            )
            db.session.add(profile)
            db.session.commit()

            # 7) Log in & redirect
            session['user_id'] = user.id
            flash(f"Welcome, {profile.name}! Your journey starts now.", 'success')
            return redirect(url_for('dashboard'))

        except ValueError as ve:
            db.session.rollback()
            error = str(ve)

        except Exception as e:
            db.session.rollback()
            app.logger.exception("Signup failed")
            # In debug mode, show the real error
            error = f"Registration error: {e}"

    return render_template('signup.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('login'))

    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    if not profile:
        flash('Profile not found.', 'danger')
        return redirect(url_for('logout'))

    records = (DailyRecord.query
               .filter_by(user_id=profile.user_id)
               .order_by(DailyRecord.date.desc())
               .limit(10).all())

    bmi = calculate_bmi(profile.weight, profile.height)
    streak = calculate_streak(records)

    return render_template(
        'dashboard.html',
        profile=profile,
        bmi=bmi,
        daily_records=records,
        streak=streak
    )


@app.route('/update_daily_record', methods=['POST'])
def update_daily_record():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    today = datetime.utcnow().date()

    day_num = int(request.form['dayNumber'])
    did_ex = 'exercise' in request.form
    did_diet = 'dietFollowed' in request.form
    new_w = float(request.form['newWeight'])

    existing = DailyRecord.query.filter_by(
        user_id=profile.user_id,
        date=today
    ).first()

    if existing:
        existing.day_number = day_num
        existing.exercise = did_ex
        existing.diet_followed = did_diet
        existing.new_weight = new_w
    else:
        rec = DailyRecord(
            user_id=profile.user_id,
            date=today,
            day_number=day_num,
            exercise=did_ex,
            diet_followed=did_diet,
            new_weight=new_w
        )
        db.session.add(rec)

    profile.weight = new_w
    db.session.commit()
    flash('Daily record updated!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete_daily_record', methods=['POST'])
def delete_daily_record():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    rec_id = request.form.get('record_id')
    rec = DailyRecord.query.filter_by(
        id=rec_id,
        user_id=session['user_id']
    ).first()
    if rec:
        db.session.delete(rec)
        db.session.commit()
        flash('Record deleted.', 'success')
    else:
        flash('Record not found.', 'warning')
    return redirect(url_for('dashboard'))


@app.route('/export_records')
def export_records():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    recs = DailyRecord.query.filter_by(user_id=session['user_id']).order_by(DailyRecord.date).all()
    if not recs:
        flash('No records to export.', 'warning')
        return redirect(url_for('dashboard'))

    data = [{
        'Date': r.date.strftime('%Y-%m-%d'),
        'Day': r.day_number,
        'Exercise': 'Yes' if r.exercise else 'No',
        'Diet': 'Yes' if r.diet_followed else 'No',
        'Weight (kg)': r.new_weight
    } for r in recs]

    df = pd.DataFrame(data)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Records')
    buf.seek(0)

    return send_file(
        buf,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name='health_records.xlsx',
        as_attachment=True
    )


@app.route('/calorie-check', methods=['GET', 'POST'], endpoint='calorie_check')
def calorie_check():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    analysis = None
    if request.method == 'POST':
        food = request.form.get('food', '').strip()
        if food:
            try:
                analysis = analyze_food(profile, food, OPENAI_API_KEY)
            except:
                flash('Error analyzing food.', 'danger')
    return render_template('calorie_check.html', analysis=analysis, username=profile.name)


@app.route('/generate_daily_diet_plan')
def generate_daily_diet_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    try:
        plan = get_daily_diet_plan(profile, OPENAI_API_KEY)
    except Exception as e:
        flash(f'Error generating diet plan: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('daily_diet_plan.html', daily_plan=plan, username=profile.name)


@app.route('/generate_daily_exercise_plan')
def generate_daily_exercise_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    try:
        plan = get_daily_exercise_plan(profile, OPENAI_API_KEY)
    except Exception as e:
        flash(f'Error generating exercise plan: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('exercise_plan.html', exercise_plan=plan, username=profile.name)


@app.route('/chatbot')
def chatbot_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    return render_template('chatbot.html', username=profile.name)


@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'reply': 'Please log in.'}), 401

    data = request.get_json()
    text = data.get('message', '').strip()
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()

    db.session.add(ChatMessage(user_id=profile.user_id, is_bot=False, content=text))
    db.session.commit()

    history = ChatMessage.query.filter_by(user_id=profile.user_id).order_by(ChatMessage.created_at).all()
    reply = get_chat_response(profile, history, text, OPENAI_API_KEY)

    db.session.add(ChatMessage(user_id=profile.user_id, is_bot=True, content=reply))
    db.session.commit()

    return jsonify({'reply': reply})


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# at the bottom of app.py
if __name__ == '__main__':
    app.run(debug=True)