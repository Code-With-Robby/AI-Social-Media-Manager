# app.py - Render deployment entry point (generalized for any niche)
from flask import Flask, request, render_template_string
from .crew import SocialMediaManager
import os

app = Flask(__name__)

# Modern, clean inline HTML form
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personalized DM Generator</title>
    <style>
        :root {
            --bg: #0f0f0f;
            --card: #1a1a1a;
            --text: #e0e0e0;
            --accent: #3b82f6;
            --accent-hover: #60a5fa;
            --border: #333;
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem 1rem;
        }
        .container { max-width: 700px; margin: 0 auto; }
        h1 {
            text-align: center;
            color: var(--accent);
            margin-bottom: 2rem;
            font-size: 2.2rem;
        }
        form {
            background: var(--card);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #aaa;
        }
        input {
            width: 100%;
            padding: 0.9rem;
            margin-bottom: 1.2rem;
            background: #222;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            font-size: 1rem;
        }
        input:focus { outline: none; border-color: var(--accent); }
        button {
            width: 100%;
            padding: 1rem;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover { background: var(--accent-hover); }
        .result-section {
            margin-top: 2.5rem;
        }
        .result-card {
            background: var(--card);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
        }
        h3 { color: var(--accent); margin-bottom: 1rem; }
        pre {
            white-space: pre-wrap;
            background: #111;
            padding: 1.2rem;
            border-radius: 8px;
            font-family: 'Consolas', monospace;
            font-size: 0.95rem;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Personalized Interview DM Generator</h1>
        <form method="POST">
            <label>Person/Expert Name</label>
            <input type="text" name="person_name" placeholder="e.g. Andrej Karpathy" required>

            <label>Niche / Field</label>
            <input type="text" name="niche" placeholder="e.g. AI and Machine Learning" required>

            <label>Your YouTube Channel Handle</label>
            <input type="text" name="youtube_channel" placeholder="e.g. @Code-With-Robby" required>

            <label>Your First Name (for DM signature)</label>
            <input type="text" name="name" placeholder="e.g. Robby" required>

            <button type="submit">Generate DM</button>
        </form>

        {% if result %}
        <div class="result-section">
            <div class="result-card">
                <h3>Generated DM</h3>
                <pre>{{ result }}</pre>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    form_data = {}  # Preserve form values on error or refresh

    if request.method == 'POST':
        person_name = request.form.get('person_name', '').strip()
        niche = request.form.get('niche', '').strip()
        youtube_channel = request.form.get('youtube_channel', '').strip()
        name = request.form.get('name', '').strip()

        form_data = {
            'person_name': person_name,
            'niche': niche,
            'youtube_channel': youtube_channel,
            'name': name
        }

        if all([person_name, niche, youtube_channel, name]):
            inputs = {
                "person_name": person_name,
                "niche": niche,
                "youtube_channel": youtube_channel,
                "name": name,
                "current_year": "2026"  # or use datetime.now().year
            }
            try:
                crew_result = SocialMediaManager().crew().kickoff(inputs=inputs)
                result = str(crew_result)
            except Exception as e:
                result = f"Error generating DM: {str(e)}"
        else:
            result = "Please fill in all fields."

    return render_template_string(INDEX_HTML, result=result, **form_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
