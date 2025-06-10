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

    # Extract from first '{' to end
    snippet = raw[start:]

    # Attempt to fix common truncation issues
    snippet = snippet.strip()
    
    # Fix unterminated strings
    if snippet.count('"') % 2 != 0:
        snippet += '"'
    
    # Fix unterminated objects
    opens = snippet.count('{')
    closes = snippet.count('}')
    if closes < opens:
        snippet += '}' * (opens - closes)
    
    # Fix trailing comma issues
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
        # If it still fails, show snippet and error
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
- Only whole, unprocessed foods
- No junk or fast food
- Include fruits, vegetables, whole grains, lean proteins, healthy fats
- Home-cooked, portion-controlled meals

User Profile:
- Goal: {goal}
- Diet Preference: {diet_preference}
- Budget: {budget}
- Health Conditions: {disease}

For days 1–30, list bullet points for:
- Breakfast
- Snack
- Lunch
- Snack
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
Include warm-up, main workout, and cool-down for each day.
Format as plain text bullet points.
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(
        age=profile.age,
        gender=profile.gender,
        bmi=calculate_bmi(profile.weight, profile.height),
        goal=profile.goal,
        cuisine=profile.cuisine or "None"
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
Produce **ONLY** a complete JSON object with keys for all 7 days (Sunday through Saturday).
Each day must be an object with keys "breakfast","lunch","dinner".

RULES:
1. Ensure ALL strings are properly terminated
2. NEVER truncate output
3. Escape double quotes in meal descriptions
4. Include ALL 7 days.
5. Use whole, unprocessed foods
6. Avoid junk/fast food
7. Include fruits, vegetables, whole grains, lean proteins, healthy fats
8. Home-cooked, portion-controlled meals
9. Use local, seasonal ingredients where possible
10. Consider budget constraints
11. Forcefully focused on healthy, balanced meals, user's cuisine preference and goal.
12. If user has a Pakistani cuisine preference, include only that food that is common in Pakistan and it's healthy and fulfilled user's goal.
13. If user's goal is weight loss, include low-calorie meals (don't add with high oil consumption dishes); if muscle gain, include high-protein meals.
14. Use a variety of foods to ensure balanced nutrition.
15. If user has any disease, avoid foods that are not suitable for that condition.



Example:
{{
  "Sunday": {{
    "breakfast": "Oatmeal with berries",
    "lunch": "Quinoa salad with chickpeas",
    "dinner": "Grilled chicken salad"
  }},
  "Monday": {{
    "breakfast": "Greek yogurt with honey",
    "lunch": "Turkey wrap with veggies",
    "dinner": "Baked salmon with asparagus"
  }}
  // Continue for all days
}}

User Profile:
- Age: {age}, Gender: {gender}, BMI: {bmi}
- Goal: {goal}, Diet: {diet_preference}, Budget: {budget}, Conditions: {disease}, Cuisine: {cuisine}
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
        cuisine=profile.cuisine or "None"
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
Produce **ONLY** a complete JSON object with keys Sunday-Saturday.
Each day must have keys "warmup","main","cooldown".

RULES:
1. Ensure ALL strings are properly terminated
2. NEVER truncate output
3. Include ALL 7 days

Example:
{{
  "Sunday": {{
    "warmup": "5 min jog",
    "main": "3x12 push-ups",
    "cooldown": "5 min stretch"
  }}
  // Continue for all days
}}

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
Analyze "{food}" for:
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
    Enhanced chatbot response focused only on health topics.
    """
    current_bmi = calculate_bmi(profile.weight, profile.height)
    status = "normal"
    if current_bmi < 18.5: status = "underweight"
    elif current_bmi > 24.9: status = "overweight"

    system = f"""\
You are FitPlan AI, a health and nutrition expert. Follow these rules strictly:

1. ONLY discuss:
   - Diet & nutrition
   - Exercise & fitness
   - Weight management
   - Health conditions
   - Medical disclaimer: "Consult a doctor for medical advice"

2. For non-health topics, respond:
   "I specialize in health and nutrition. How can I assist with your wellness goals?"
3. Use a friendly, professional tone.
4. Provide evidence-based, practical advice.
5. Avoid personal opinions or unverified claims.
6. Always prioritize user safety and well-being.
7. If asked about non-health topics, redirect to health-related questions.
8. Never answer the non-health questions. Just answer health-related questions.

For example, if asked about a recipe, focus on its health benefits, ingredients, and how it fits into the user's diet plan.
if asked about exercise, provide tailored routines based on the user's profile.
if asked about a health condition, provide general information and suggest consulting a healthcare professional.
if asked about a food item, analyze its nutritional value and how it fits into the user's diet.
if asked about a health goal, provide actionable steps and resources to achieve it.
if asked about anything outside health, respond with "I specialize in health and nutrition. How can I assist with your wellness goals?"

3. User Profile:
Name:{profile.name}, Age:{profile.age}, Gender:{profile.gender}
Height:{profile.height}cm, Weight:{profile.weight}kg, BMI:{current_bmi}({status})
Goal:{profile.goal}, Diet:{profile.diet_preference}, Conditions:{profile.disease or 'None'}, Cuisine:{profile.cuisine or 'None'}.
"""
    messages = [SystemMessage(content=system)]
    for msg in history:
        messages.append(AIMessage(content=msg.content) if msg.is_bot else HumanMessage(content=msg.content))
    messages.append(HumanMessage(content=new_message))

    chat_llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key)
    response = chat_llm(messages)
    return response.content