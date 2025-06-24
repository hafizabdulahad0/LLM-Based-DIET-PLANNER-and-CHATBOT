import json
import re
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

def _parse_json(raw: str) -> dict:
    """
    Extract the first '{' to end of string, then balance braces and quotes if truncated,
    and parse the result as JSON.
    """
    start = raw.find('{')
    if start == -1:
        raise ValueError(f"Could not find JSON object in output:\n{raw}")

    snippet = raw[start:].strip()

    # Fix unterminated strings
    if snippet.count('"') % 2 != 0:
        snippet += '"'

    # Fix unbalanced braces
    opens = snippet.count('{')
    closes = snippet.count('}')
    if closes < opens:
        snippet += '}' * (opens - closes)

    # Fix trailing comma
    if snippet.endswith(','):
        snippet = snippet[:-1] + '}'

    # Remove trailing incomplete keys
    if ':' in snippet and not snippet.strip().endswith('}'):
        last_colon = snippet.rfind(':')
        last_brace = snippet.rfind('}')
        if last_colon > last_brace:
            snippet = snippet[:last_colon] + '}'

    try:
        return json.loads(snippet)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON:\n{snippet}\nError: {e}")


def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculate BMI given weight (kg) and height (cm).
    """
    return round(weight / ((height / 100) ** 2), 1)


def get_diet_plan(profile, bmi: float, status: str, openai_api_key: str) -> str:
    """
    Returns a 30-day diet plan in human-readable bullet format.
    """
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    prompt = PromptTemplate(
        input_variables=[
            "age", "gender", "bmi", "status",
            "goal", "diet_preference", "budget", "disease"
        ],
        template="""
Create a comprehensive 30-day healthy diet plan for a {age}-year-old {gender} with BMI {bmi} ({status}).

Requirements:
- Only whole, unprocessed Pakistani foods and products.
- No imported or international items.
- Include fruits, vegetables, whole grains, lean proteins, healthy fats that are common in Pakistan.
- Home-cooked, portion-controlled meals using local ingredients.

User Profile:
- Goal: {goal}
- Diet Preference: {diet_preference}
- Budget: {budget}
- Health Conditions: {disease}

For days 1–30, list bullet points for:
- Breakfast
- Morning Snack
- Lunch
- Evening Snack
- Dinner
- Hydration

Format as plain text.
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(
        age=profile.age,
        gender=profile.gender,
        bmi=bmi,
        status=status,
        goal=profile.goal,
        diet_preference=profile.diet_preference,
        budget=profile.budget,
        disease=profile.disease or "None"
    )


def get_7_day_exercise_plan(profile, openai_api_key: str) -> str:
    """
    Returns a 7-day exercise plan in bullet format.
    """
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    prompt = PromptTemplate(
        input_variables=["age", "gender", "bmi", "goal"],
        template="""
Create a 7-day exercise plan for a {age}-year-old {gender} (BMI: {bmi}, goal: {goal}).
Use exercises common and accessible in Pakistan (e.g., brisk walking, bodyweight exercises).
Include warm-up, main workout, and cool-down for each day.
Format as plain text bullet points.
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(
        age=profile.age,
        gender=profile.gender,
        bmi=calculate_bmi(profile.weight, profile.height),
        goal=profile.goal
    )


def get_daily_diet_plan(profile, openai_api_key: str) -> dict:
    """
    Returns a dict mapping each weekday to a one-day meal plan (JSON).
    """
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key, max_tokens=2000)
    prompt = PromptTemplate(
        input_variables=[
            "age", "gender", "bmi", "goal",
            "diet_preference", "budget", "disease", "cuisine"
        ],
        template="""\
Produce **ONLY** a complete JSON object with keys Sunday through Saturday.
Each day must be an object with "breakfast","lunch","dinner" — all items must be Pakistani dishes or products.

RULES:
1. Only local Pakistani foods.
2. No imported or non-Pakistani ingredients.
3. Use healthy, whole-food Pakistani recipes.
4. Consider budget and dietary restrictions.

User Profile:
- Age: {age}, Gender: {gender}, BMI: {bmi}
- Goal: {goal}, Diet: {diet_preference}, Budget: {budget}, Conditions: {disease}, Cuisine Preference: Pakistani
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    raw = chain.run(
        age=profile.age,
        gender=profile.gender,
        bmi=calculate_bmi(profile.weight, profile.height),
        goal=profile.goal,
        diet_preference=profile.diet_preference,
        budget=profile.budget,
        disease=profile.disease or "None",
        cuisine="Pakistani"
    )
    return _parse_json(raw)


def get_daily_exercise_plan(profile, openai_api_key: str) -> dict:
    """
    Returns a dict mapping each weekday to a one-day exercise plan (JSON).
    """
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key, max_tokens=1500)
    prompt = PromptTemplate(
        input_variables=["age", "gender", "bmi", "goal"],
        template="""\
Produce **ONLY** a complete JSON object with keys Sunday through Saturday.
Each day must include "warmup","main","cooldown" with exercises common in Pakistan.

RULES:
1. Only use exercises accessible locally (e.g., walking, jogging, bodyweight).
2. Ensure balanced routines.

User: {age} y/o {gender}, BMI {bmi}, Goal {goal}.
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    raw = chain.run(
        age=profile.age,
        gender=profile.gender,
        bmi=calculate_bmi(profile.weight, profile.height),
        goal=profile.goal
    )
    return _parse_json(raw)


def analyze_food(profile, food: str, openai_api_key: str) -> dict:
    """
    Returns a dict with comprehensive food analysis.
    """
    llm = OpenAI(temperature=0.5, openai_api_key=openai_api_key)
    prompt = PromptTemplate(
        input_variables=["food","age","gender","bmi","goal","diet_preference","disease"],
        template="""
Analyze "{food}" solely in the context of Pakistani cuisine:
Age: {age}, Gender: {gender}, BMI: {bmi}, Goal: {goal}, Diet: {diet_preference}, Conditions: {disease}.
Return JSON with keys:
"calories","nutrients","pros","cons","recommendation","healthier_alternatives","portion_advice".
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    raw = chain.run(
        food=food,
        age=profile.age,
        gender=profile.gender,
        bmi=calculate_bmi(profile.weight, profile.height),
        goal=profile.goal,
        diet_preference=profile.diet_preference,
        disease=profile.disease or "None"
    )
    return _parse_json(raw)


def get_chat_response(profile, history, new_message: str, openai_api_key: str) -> str:
    """
    Chatbot response strictly focused on Pakistani diet, fitness, and wellness.
    """
    current_bmi = calculate_bmi(profile.weight, profile.height)
    status = "normal"
    if current_bmi < 18.5:
        status = "underweight"
    elif current_bmi > 24.9:
        status = "overweight"

    system = f"""
You are FitPlan AI — a Pakistani health assistant. Follow this rule:

🔒 **Strict Rule**:
Only recommend Pakistani foods, products, and exercises. No exceptions.

Always use:
- Local Pakistani dishes, ingredients, and brands
- Exercises accessible in Pakistan
- Profile data:
  Name: {profile.name}
  Age: {profile.age}
  Gender: {profile.gender}
  Height: {profile.height} cm
  Weight: {profile.weight} kg
  BMI: {current_bmi:.1f} ({status})
  Goal: {profile.goal}
  Diet Preference: {profile.diet_preference}
  Budget: {profile.budget}
  Known Disease: {profile.disease or "None"}

If user asks anything else, redirect: "I specialize in Pakistani diet and fitness. How can I assist?"
"""

    messages = [SystemMessage(content=system)]
    for msg in history:
        messages.append(AIMessage(content=msg.content) if msg.is_bot else HumanMessage(content=msg.content))
    messages.append(HumanMessage(content=new_message))

    chat_llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key)
    response = chat_llm(messages)
    return response.content
