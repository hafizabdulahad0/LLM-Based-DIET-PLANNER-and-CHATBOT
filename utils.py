import json
import re
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

def _parse_json(raw: str) -> dict:
    """
    Extract the first {...} JSON block from raw text and parse it.
    """
    match = re.search(r'(\{.*\})', raw, re.DOTALL)
    if not match:
        raise ValueError(f"Could not find JSON in model output:\n{raw}")
    return json.loads(match.group(1))

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
Create a concise 30-day diet plan for a {age}-year-old {gender} with BMI {bmi} ({status}).
Focus on goal: {goal}. Preferences: {diet_preference} cuisine, {budget} budget.
Health concerns: {disease}. For each day include breakfast, lunch, dinner, and a snack.
Respond in bullet format only.
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
For each day include warm-up, main workout (sets/reps), and cooldown.
Respond in bullet format per day.
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
    Returns a dict mapping each weekday to a one-day meal plan.
    """
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    prompt = PromptTemplate(
        input_variables=[
            "age", "gender", "bmi", "goal",
            "diet_preference", "budget", "disease"
        ],
        template="""
Produce ONLY a JSON object whose keys are the days of the week:
Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday.
Each value must be an object with keys:
  - breakfast
  - lunch
  - dinner
and appropriate meal descriptions.
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
        disease=profile.disease or "None"
    )
    return _parse_json(raw)

def get_daily_exercise_plan(profile, openai_api_key: str) -> dict:
    """
    Returns a dict mapping each weekday to a one-day exercise plan.
    """
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    prompt = PromptTemplate(
        input_variables=["age", "gender", "bmi", "goal"],
        template="""
Produce ONLY a JSON object whose keys are the days of the week:
Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday.
Each value must be an object with keys:
  - warmup
  - main
  - cooldown
and appropriate exercise descriptions.
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
    Returns a dict with keys:
      calories, nutrients, pros, cons, recommendation.
    """
    llm = OpenAI(temperature=0.5, openai_api_key=openai_api_key)
    prompt = PromptTemplate(
        input_variables=[
            "food", "age", "gender", "bmi", 
            "goal", "diet_preference", "disease"
        ],
        template="""
Produce ONLY a JSON object with the following keys:
- calories: a string like "350 kcal"
- nutrients: an array of strings
- pros: an array of strings
- cons: an array of strings
- recommendation: a string

Now analyze the following food:
Food: "{food}"
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

# ——— Chatbot logic ———

def get_chat_response(profile, history, new_message: str, openai_api_key: str) -> str:
    """
    Given the user profile, ChatMessage history list, and a new user message,
    return the bot's reply.
    """
    system_content = (
        f"You are a friendly health advisor. "
        f"User info: age={profile.age}, gender={profile.gender}, "
        f"height={profile.height}cm, weight={profile.weight}kg, "
        f"goal={profile.goal}, diet_pref={profile.diet_preference}, "
        f"disease={profile.disease or 'None'}."
    )
    messages = [SystemMessage(content=system_content)]
    for msg in history:
        if msg.is_bot:
            messages.append(AIMessage(content=msg.content))
        else:
            messages.append(HumanMessage(content=msg.content))
    messages.append(HumanMessage(content=new_message))

    chat_llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key)
    response = chat_llm(messages)
    return response.content
