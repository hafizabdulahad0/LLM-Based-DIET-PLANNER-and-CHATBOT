```markdown
# LLM-Based BMI Diet Planner

A Flask web application that leverages OpenAI’s ChatGPT (via LangChain) to provide personalized health and fitness guidance:

- **BMI Calculation & Status** (Underweight, Normal, Overweight)  
- **7-Day Diet Plan** (bullet format)  
- **Food Analysis** (calories, nutrients, pros/cons, recommendation)  
- **Daily Tracking** (exercise ✔️, diet ✔️, weight update)  
- **Export Records** to Excel  
- **Live Health Chatbot** with conversation history  
- **User Authentication** & Profile Management  
- **Dark/Light Theme Toggle**  

---

## 🚀 Features

- **Authentication**: Email/password signup & login  
- **User Profile**: Name, age, height, weight, gender, medical conditions, diet preferences, budget, goal, cuisine style  
- **Dashboard**:  
  - Real-time BMI display & meter  
  - Current weight, height & target weight  
  - Action buttons for plans, food analysis & chatbot  
  - Daily record form & table of history  
- **AI-Powered Plans**:  
  - 7-day diet plan (bullet list)  
- **Food Analysis**: Caloric breakdown, nutritional highlights, pros/cons, recommendation  
- **Tracking & Export**: Update daily record; export history as `.xlsx`  
- **Health Chatbot**: Live conversation, personalized advice, saved chat history  
- **Responsive UI**: Modern CSS with animations, dark/light mode, print-friendly  

---

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask, Flask-SQLAlchemy (SQLite)  
- **AI**: LangChain, OpenAI API (ChatGPT)  
- **Database**: SQLite (via SQLAlchemy)  
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)  
- **Data**: pandas, openpyxl (for Excel export)  

---

## 📥 Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/yourusername/llm-bmi-diet-planner.git
   cd llm-bmi-diet-planner
   ```

2. **Create & activate virtual env**  
   ```bash
   python -m venv venv
   # macOS / Linux
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**  
   Write your keys in `.env` file in project root:
   ```
   SECRET_KEY=your_flask_secret_key
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Initialize database**  
   ```bash
   python app.py
   ```
   This will auto-create `instance/database.db`.

---

## ▶️ Running the App

```bash
python app.py
```

- Open your browser at `http://localhost:5000`  
- Sign up, complete your profile, and explore the dashboard!

---

## 📂 Project Structure

```
llm-bmi-diet-planner/
├── app.py                  # Flask application & routes
├── models.py               # SQLAlchemy models
├── utils.py                # BMI calc, LangChain prompts, chatbot logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── instance/
│   └── database.db         # SQLite database
├── static/
│   └── style.css           # Main stylesheet
└── templates/
    ├── base.html
    ├── login.html
    ├── signup.html
    ├── dashboard.html
    ├── chatbot.html
    ├── daily_diet_plan.html
    ├── exercise_plan.html
    └── calorie_check.html
```

---

## 📝 Usage

1. **Sign up** and fill out your profile.  
2. **Dashboard** shows your BMI, targets, and quick-action buttons.  
3. **Generate Plans**:  
   - Click “7-Day Diet Plan” or “Food Analysis”  
   - For single-day plans, use the respective buttons.  
4. **Track** each day’s exercise, diet ✓/✗ and update your weight.  
5. **Export** all records to Excel for your archives.  
6. **Chat**: Click “Chat with Bot” to open the live advisor in a new tab.  

---

## 🤝 Contributing

1. Fork this repository  
2. Create a feature branch (`git checkout -b feature/xyz`)  
3. Commit your changes (`git commit -m 'Add xyz'`)  
4. Push to branch (`git push origin feature/xyz`)  
5. Open a Pull Request  

---

## 📄 License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 🤖 Acknowledgments

- [LangChain](https://github.com/langchain/langchain)  
- [OpenAI](https://openai.com)  
- Inspired by modern health & fitness web apps  
```
