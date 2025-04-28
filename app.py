from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_file, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os, pandas as pd
from io import BytesIO
from dotenv import load_dotenv
from models import (
    db, User, UserProfile, DailyRecord,
    DietPlan, ChatMessage
)
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

@app.route('/')
def home():
    return redirect(url_for('dashboard')) if 'user_id' in session else redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        try:
            if User.query.filter_by(email=request.form['email']).first():
                raise ValueError("Email already exists")
            user = User(
                email=request.form['email'],
                password=generate_password_hash(request.form['password'])
            )
            db.session.add(user); db.session.commit()
            profile = UserProfile(
                user_id=user.id,
                name=request.form['name'],
                age=int(request.form['age']),
                height=float(request.form['height']),
                weight=float(request.form['weight']),
                gender=request.form['gender'],
                disease=request.form.get('disease',''),
                diet_preference=request.form['diet_preference'],
                budget=request.form['budget'],
                goal=request.form['goal'],
                cuisine=request.form['cuisine']
            )
            db.session.add(profile); db.session.commit()
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            return render_template('signup.html', error=str(e))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    if not profile:
        return redirect(url_for('logout'))
    # Records & stats
    records = DailyRecord.query.filter_by(user_id=profile.user_id)\
               .order_by(DailyRecord.date.desc()).all()
    bmi = calculate_bmi(profile.weight, profile.height)
    # target weight
    mn = round(18.5*(profile.height/100)**2,1)
    mx = round(24.9*(profile.height/100)**2,1)
    target = mn if profile.weight>mx else (mx if profile.weight<mn else profile.weight)
    return render_template(
        'dashboard.html',
        profile=profile,
        bmi=bmi,
        daily_records=records,
        target_weight=target
    )

@app.route('/calorie-check', endpoint='calorie_check', methods=['GET','POST'])
def calorie_check():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    if request.method == 'POST':
        analysis = analyze_food(profile, request.form['food'], OPENAI_API_KEY)
        return render_template('calorie_check.html', analysis=analysis)
    return render_template('calorie_check.html')

@app.route('/generate_daily_diet_plan')
def generate_daily_diet_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    daily_plan = get_daily_diet_plan(profile, OPENAI_API_KEY)
    return render_template('daily_diet_plan.html', daily_plan=daily_plan)

@app.route('/generate_daily_exercise_plan')
def generate_daily_exercise_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    exercise_plan = get_daily_exercise_plan(profile, OPENAI_API_KEY)
    return render_template('exercise_plan.html', exercise_plan=exercise_plan)

@app.route('/update_daily_record', methods=['POST'])
def update_daily_record():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    prof = UserProfile.query.filter_by(user_id=session['user_id']).first()
    rec = DailyRecord(
        user_id=prof.user_id,
        date=datetime.utcnow().date(),
        day_number=int(request.form['dayNumber']),
        exercise='exercise' in request.form,
        diet_followed='dietFollowed' in request.form,
        new_weight=float(request.form['newWeight'])
    )
    prof.weight = rec.new_weight
    db.session.add(rec)
    db.session.commit()
    flash("Daily record updated!")
    return redirect(url_for('dashboard'))

@app.route('/export_records')
def export_records():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    recs = DailyRecord.query.filter_by(user_id=session['user_id']).all()
    data = [{
        'Date': r.date.strftime('%Y-%m-%d'),
        'Day': r.day_number,
        'Exercise': 'Yes' if r.exercise else 'No',
        'Diet': 'Yes' if r.diet_followed else 'No',
        'Weight (kg)': r.new_weight
    } for r in recs]
    df = pd.DataFrame(data)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as w:
        df.to_excel(w, index=False, sheet_name='Records')
    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name='daily_records.xlsx',
        as_attachment=True
    )

@app.route('/chatbot')
def chatbot_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'reply':'Please log in.'}), 401
    data = request.get_json()
    text = data.get('message','').strip()
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    # save user msg
    db.session.add(ChatMessage(user_id=profile.user_id, is_bot=False, content=text))
    db.session.commit()
    history = ChatMessage.query.filter_by(user_id=profile.user_id)\
               .order_by(ChatMessage.created_at).all()
    bot_reply = get_chat_response(profile, history, text, OPENAI_API_KEY)
    db.session.add(ChatMessage(user_id=profile.user_id, is_bot=True, content=bot_reply))
    db.session.commit()
    return jsonify({'reply':bot_reply})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
