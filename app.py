# app.py - Flask version with agent + research tool
# Generates personalized BJJ/MMA DMs via UI, JSON API, and streaming

import os
import asyncio
from flask import Flask, request, jsonify, render_template, Response
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool
from agents import OpenAIChatCompletionsModel

load_dotenv(override=True)

# ────────────────────────────────────────────────
# Gemini client & model
# ────────────────────────────────────────────────
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

gemini_model = OpenAIChatCompletionsModel(
    model=os.getenv("MODEL", "gemini-1.5-flash"),
    openai_client=client,
)

# ────────────────────────────────────────────────
# RESEARCH AGENT – used as a tool
# ────────────────────────────────────────────────
research_instructions = """
You are a knowledgeable MMA/BJJ/UFC/Wrestler researcher.

When given an athlete's name, provide a concise, factual summary (4–8 sentences) of their career background and most relevant/recent accomplishments, fights, titles, rankings, or milestones.

Prioritize events and results from 2024–2026 if available.
Include specific details: dates, opponents, results, titles won/lost, rankings, notable techniques, or career highlights.
Be accurate and neutral — no hype or speculation.

Output only the summary paragraph(s). No introductions, no questions, no bullet points unless it improves clarity.
"""

research_agent = Agent(
    name="Athlete Researcher",
    instructions=research_instructions,
    model=gemini_model,
)

@function_tool
async def get_athlete_info(name: str) -> str:
    """
    Retrieve a concise summary of a BJJ/MMA/UFC/Wrestler athlete's background and recent accomplishments.
    Use this BEFORE writing any outreach message.
    Input: full name of the athlete.
    """
    query = f"Provide a detailed career summary and recent highlights for: {name}"
    
    with trace(f"Researching {name}"):
        result = await Runner.run(research_agent, query)
    
    return result.final_output.strip()

# ────────────────────────────────────────────────
# SOCIAL MEDIA MANAGER AGENT – uses the research tool
# ────────────────────────────────────────────────
manager_instructions = """
You are a Social Media Manager for a BJJ/MMA/Wrestling-focused YouTube channel: https://www.youtube.com/@Rob-J-BJJ

Your task is to write a concise, respectful, personalized direct message (Instagram or Twitter/X DM) inviting a BJJ, MMA, or UFC athlete for an interview.

Step 1: ALWAYS use the get_athlete_info tool first to get accurate background and recent accomplishments for the named athlete.
Step 2: Select 2–3 of the most impressive or recent highlights from the summary and mention them naturally at the beginning to show genuine awareness and respect.
   - Be very specific (dates, opponents, results, titles, etc.).
   - Keep the opening natural — never overly flattering.

Step 3: Transition smoothly into introducing the channel: it creates authentic, technical breakdowns, educational insights, and short-form content about grappling, MMA, Wrestling, and high-level combat sports — made for serious fans and practitioners.

Step 4: Clearly invite them for an interview/conversation about their journey, mindset, experience, and insights into BJJ/MMA. Emphasize that scheduling is flexible — whenever is convenient for them.

Rules:
- Tone: friendly, professional, brief, authentic — like a real fan who respects the sport
- First person only ("I"), name: Robert
- No hashtags, minimal/no emojis, no corporate/spammy language
- Max 1000 characters
- Output ONLY the final polished DM — nothing else
"""

social_media_manager = Agent(
    name="Social Media Manager",
    instructions=manager_instructions,
    model=gemini_model,
    tools=[get_athlete_info],
)

# ────────────────────────────────────────────────
# Flask app
# ────────────────────────────────────────────────
app = Flask(__name__)

# ────────────────────────────────────────────────
# Sync wrapper for agent (non-streaming)
# ────────────────────────────────────────────────
def generate_dm(athlete_name: str) -> str:
    user_message = f"Send a personalized interview invitation DM to {athlete_name}"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        with trace("DM Generation"):
            result = loop.run_until_complete(Runner.run(social_media_manager, user_message))
        return result.final_output.strip()
    finally:
        loop.close()

# ────────────────────────────────────────────────
# Streaming generator (word-by-word simulation)
# ────────────────────────────────────────────────
async def generate_dm_stream(athlete_name: str):
    user_message = f"Send a personalized interview invitation DM to {athlete_name}"

    full_result = await Runner.run(social_media_manager, user_message)
    text = full_result.final_output.strip()

    # Simulate streaming by yielding word by word
    words = text.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words)-1 else "")
        await asyncio.sleep(0.05)  # typing effect

# ────────────────────────────────────────────────
# Routes (exactly like your example)
# ────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', dm='', athlete_name='')

@app.route('/generate_dm_ui', methods=['POST'])
def generate_dm_ui():
    athlete_name = request.form.get('athlete_name', '').strip()
    if not athlete_name:
        return render_template('index.html', dm="Please provide an athlete name.", athlete_name='')
    
    dm = generate_dm(athlete_name)
    return render_template('index.html', dm=dm, athlete_name=athlete_name)

@app.route('/generate_dm', methods=['POST'])
def generate_dm_endpoint():
    data = request.get_json()
    if not data or 'athlete_name' not in data:
        return jsonify({"error": "Missing 'athlete_name' in request body"}), 400
    
    athlete_name = data['athlete_name'].strip()
    dm = generate_dm(athlete_name)
    return jsonify({"dm": dm})

@app.route('/stream_dm', methods=['POST'])
def stream_dm():
    data = request.get_json()
    if not data or 'athlete_name' not in data:
        return jsonify({"error": "Missing 'athlete_name' in request body"}), 400
    
    athlete_name = data['athlete_name'].strip()

    async def stream_response():
        yield "data: Generating personalized DM...\n\n"
        async for chunk in generate_dm_stream(athlete_name):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        stream_response(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
