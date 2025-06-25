# LLM-Based Diet Planner and Chatbot

A Flask web application that leverages OpenAI’s Large Language Models (via LangChain) to provide personalized health and fitness guidance, focusing on Pakistani cuisine and accessible exercises. Key functionalities include:

- **BMI Calculation & Status** (Underweight, Normal, Overweight)
- **Personalized 7-Day Diet Plans** (structured daily meals: breakfast, lunch, dinner)
- **Personalized 7-Day Exercise Plans** (structured daily workouts: warmup, main, cooldown)
- **Food Analysis** (calories, nutrients, pros/cons, recommendations for Pakistani food items)
- **Daily Progress Tracking** (exercise adherence, diet compliance, weight updates)
- **Export Records** to Excel (`.xlsx`) format
- **Live Health Chatbot** with conversation history, tailored to user's profile
- **User Authentication** & Comprehensive Profile Management
- **Dark/Light Theme Toggle** for user interface customization

## 🚀 Features

-   **Authentication**: Secure email and password based signup and login system.
-   **User Profile**: Collects essential user data for personalization:
    -   Personal Details: Name, age, gender.
    -   Physical Metrics: Height (cm), weight (kg).
    -   Health Information: Existing medical conditions (disease), diet preferences (vegetarian, non-vegetarian, vegan).
    -   Fitness Goals: Lose weight, gain muscle, maintain.
    -   Preferences: Preferred cuisine style (e.g., Pakistani).
-   **Dashboard**:
    -   Real-time BMI display with a visual meter and status.
    -   Current weight, height, and target goal overview.
    -   Quick action buttons for generating diet/exercise plans, food analysis, and accessing the chatbot.
    -   Daily record form for tracking exercise, diet adherence, and current weight.
    -   Table displaying recent daily records with an option to delete entries.
    -   Workout streak counter.
-   **AI-Powered Plans**:
    -   **7-Day Diet Plans**: Generates structured daily meal plans (breakfast, lunch, dinner) tailored to the user's profile, focusing on healthy, whole-food Pakistani dishes and considering any specified medical conditions.
    -   **7-Day Exercise Plans**: Creates structured daily exercise routines (warmup, main workout, cooldown) using exercises common and accessible in Pakistan, aligned with the user's fitness level and goals.
-   **Food Analysis**: Provides a detailed analysis of user-specified food items (particularly within Pakistani cuisine context) including:
    -   Estimated calories and macronutrient breakdown.
    -   Pros and cons in relation to the user's profile.
    -   Recommendations, healthier alternatives, and portion advice.
-   **Tracking & Export**:
    -   Users can log daily exercise completion, diet adherence, and update their weight.
    -   Ability to export the entire health record history as an `.xlsx` file.
-   **Health Chatbot**:
    -   Interactive AI chatbot for personalized advice on diet, fitness, and wellness.
    -   Leverages user profile data for contextual responses.
    -   Strictly focuses on Pakistani foods, products, and exercises.
    -   Saves conversation history for continued interaction.
-   **Responsive UI**:
    -   Modern user interface built with Tailwind CSS.
    -   Supports Dark and Light mode, with user preference saved in local storage.
    -   Print-friendly layouts for diet and exercise plans.

---

## 🛠️ Tech Stack

-   **Backend**: Python, Flask, Flask-SQLAlchemy
-   **AI**: LangChain, OpenAI API (GPT models)
-   **Database**: SQLite
-   **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
-   **Data Handling**: pandas, openpyxl (for Excel export)
-   **Environment Management**: python-dotenv

---

## 📥 Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/hafizabdulahad0/LLM-Based-DIET-PLANNER-and-CHATBOT.git
    cd LLM-Based-DIET-PLANNER-and-CHATBOT
    ```

2.  **Create and activate a virtual environment**
    ```bash
    # For Python 3
    python -m venv venv
    ```
    Activate the environment:
    ```bash
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**
    Create a `.env` file in the project root directory and add your API keys:
    ```env
    SECRET_KEY=your_flask_secret_key_here
    OPENAI_API_KEY=your_openai_api_key_here
    ```
    Replace `your_flask_secret_key_here` with a strong, random string and `your_openai_api_key_here` with your actual OpenAI API key.

5.  **Initialize the database**
    The database (`instance/database.db`) will be created automatically when you first run the application, as `db.create_all()` is called within the app context.

---

## ▶️ Running the App

Execute the main application file:
```bash
python app.py
```
The application will start, typically on `http://localhost:5000`. Open this URL in your web browser.

-   Sign up for a new account or log in if you already have one.
-   Complete your user profile with accurate information for personalized plans.
-   Explore the dashboard, generate plans, track your progress, and interact with the chatbot.

---

## 📂 Project Structure

```
LLM-Based-DIET-PLANNER-and-CHATBOT/
├── app.py                  # Main Flask application: routes and core logic
├── models.py               # SQLAlchemy database models (User, UserProfile, etc.)
├── utils.py                # Utility functions: BMI calculation, LangChain prompts, AI interactions
├── requirements.txt        # Python dependencies for pip
├── .env                    # Environment variables (SECRET_KEY, OPENAI_API_KEY) - Gitignored
├── instance/
│   └── database.db         # SQLite database file
├── static/
│   ├── style.css           # Custom CSS styles (Tailwind base)
│   └── img/                # Image assets (e.g., logo)
├── templates/              # HTML templates for views
│   ├── base.html           # Base layout with header, footer, theme toggle
│   ├── login.html          # User login page
│   ├── signup.html         # User registration wizard
│   ├── dashboard.html      # User dashboard with stats and actions
│   ├── chatbot.html        # Chat interface for AI assistant
│   ├── daily_diet_plan.html # Displays 7-day diet plan
│   ├── exercise_plan.html  # Displays 7-day exercise plan
│   ├── calorie_check.html  # Food analysis input and results
│   └── partials/
│       └── home_sections.html # Reusable sections for the home page
├── tailwind.config.js      # Tailwind CSS configuration
├── vercel.json             # Vercel deployment configuration
└── wsgi.py                 # WSGI entry point for deployment
```

---

## 📝 Usage

1.  **Sign Up / Login**: Create a new account or log in with existing credentials. New users will be guided through a multi-step profile setup.
2.  **Dashboard**: After login, the dashboard provides an overview of your BMI, current stats, and quick links to features.
3.  **Generate Plans**:
    -   Click "Diet Plan" to get a 7-day personalized meal plan.
    -   Click "Exercise Plan" for a 7-day workout schedule.
    -   Use "Food Check" to analyze specific food items.
4.  **Daily Tracking**: On the dashboard, fill the "Record Daily Update" form to log your activity, diet adherence, and new weight.
5.  **Export Data**: Click "Export CSV" on the dashboard to download your health records.
6.  **Chat with AI**: Click "Chat" or navigate to the chatbot page to interact with the AI health assistant for advice and queries.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  Fork this repository.
2.  Create a new feature branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -m 'Add some feature'`).
4.  Push to your feature branch (`git push origin feature/your-feature-name`).
5.  Open a Pull Request.

---

## 📄 License

This project is released under the **MIT License**. See `LICENSE` for details.

---

## 🤖 Acknowledgments

-   [LangChain](https://github.com/langchain/langchain) for the LLM framework.
-   [OpenAI](https://openai.com) for providing the powerful language models.
-   Project created and maintained by [Hafiz Abdul Ahad](https://github.com/hafizabdulahad0).
