import gradio as gr
import json
from google import genai
from google.genai import types

# ========== TOOL FUNCTIONS (same as your code, shortened here for clarity) ==========

def provide_crisis_support(user_location: str):
    location_key = user_location.upper() if user_location else "GENERAL"
    crisis_resources = {
        "US": "988 Suicide & Crisis Lifeline (Text or Call)",
        "UK": "Samaritans (Call 116 123)",
        "INDIA": "KIRAN Mental Health Helpline (1800-599-0019)",
        "GENERAL": "Please reach out to a trusted adult or local crisis line immediately."
    }
    return json.dumps({
        "status": "Crisis detected",
        "resource": crisis_resources.get(location_key, crisis_resources["GENERAL"]),
        "advice": "Please connect with a human professional immediately."
    })

def get_cyber_safety_checklist(topic: str):
    topic_key = topic.lower() if topic else "default"
    checklists = {
        "privacy": ["Enable 2FA", "Review privacy settings", "Check app permissions"],
        "phishing": ["Avoid clicking suspicious links", "Check sender's email"],
        "default": ["Choose a topic like privacy or phishing."]
    }
    return json.dumps({"topic": topic_key, "checklist": checklists.get(topic_key, checklists["default"])})

def guide_coping_exercise(emotion: str):
    emotion_key = emotion.lower() if emotion else "general"
    exercises = {
        "anxiety": "Try 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s.",
        "stressed": "Grounding: 5 things you see, 4 touch, 3 hear, 2 smell, 1 taste.",
        "general": "Take three deep breaths and relax."
    }
    return json.dumps({"emotion": emotion_key, "exercise": exercises.get(emotion_key, exercises["general"])})

def provide_legal_reporting_info(crime_type: str):
    crime_key = crime_type.lower() if crime_type else "general"
    reporting_info = {
        "scam": ["Report to platform", "Contact your bank", "File complaint on cybercrime.gov.in"],
        "bullying": ["Block offender", "Save evidence", "Inform trusted adult"],
        "general": ["Document incident", "Report platform", "Inform authority"]
    }
    return json.dumps({"crime_type": crime_key, "reporting_steps": reporting_info.get(crime_key, reporting_info["general"])})

tool_functions = {
    "provide_crisis_support": provide_crisis_support,
    "get_cyber_safety_checklist": get_cyber_safety_checklist,
    "guide_coping_exercise": guide_coping_exercise,
    "provide_legal_reporting_info": provide_legal_reporting_info,
}

# ========== MAIN CHATBOT LOGIC FOR GRADIO ==========

api_key = "AIzaSyCLKbW3EMbJu3yQiK1kjH4YFqJnDzGOUjg"  # replace with your key
client = genai.Client(api_key=api_key)
model_name = "gemini-2.5-flash"

system_instruction = (
    "You are a compassionate cyber-resilience chatbot. "
    "Offer safety advice, mental health coping exercises, and legal reporting info when needed."
)

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    tools=list(tool_functions.values())
)

chat = client.chats.create(model=model_name, config=config)

def chatbot(user_input, history):
    try:
        response = chat.send_message(user_input)
        if response.function_calls:
            for fc in response.function_calls:
                if fc.name in tool_functions:
                    func = tool_functions[fc.name]
                    args = {k: fc.args.get(k) for k in fc.args}
                    output = func(**args)
                    part = types.Part.from_function_response(
                        name=fc.name, response={"result": output}
                    )
                    final = chat.send_message(part)
                    return final.text
        return response.text
    except Exception as e:
        return f"⚠️ Error: {e}"

# ========== GRADIO CHAT INTERFACE ==========

demo = gr.ChatInterface(
    chatbot,
    title="🛡️ Cyber-Resilience Chatbot",
    description="A supportive chatbot for cybercrime awareness, coping exercises, and legal help.",
    theme="soft",
    examples=[
        ["How do I report cyberbullying?"],
        ["Give me a checklist for phishing prevention."],
        ["I feel anxious after an online threat."],
    ],
)

demo.launch()
