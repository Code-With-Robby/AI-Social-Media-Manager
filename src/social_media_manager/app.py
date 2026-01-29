# app.py - Render deployment entry point (generalized + disclaimer + rate limiting + progress + final DM in UI)
from flask import Flask, request, render_template_string, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .crew import SocialMediaManager
import os
import asyncio
from datetime import datetime

app = Flask(__name__)

# Rate limiting: 5 requests per minute per IP (adjust as needed)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"],
    storage_uri="memory://"  # in-memory for simplicity (Render free tier)
)

# Disclaimer text (visible on UI)
DISCLAIMER = """
<p style="color: #ff6b6b; text-align: center; margin: 1rem 0; font-size: 0.95rem;">
    <strong>Disclaimer:</strong> This is a personal demo tool for learning agentic AI. 
    Not intended for unsolicited or bulk messaging. Use responsibly and ethically.
</p>
"""

# Inline HTML template (no f-string - pure string for Jinja2 compatibility)
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personalized DM Generator</title>
    <style>
        :root { --bg: #0f0f0f; --card: #1a1a1a; --text: #e0e0e0; --accent: #3b82f6; --accent-hover: #60a5fa; --border: #333; }
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; padding: 2rem 1rem; }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { text-align: center; color: var(--accent); margin-bottom: 1rem; font-size: 2.2rem; }
        .disclaimer { background: #2d1a1a; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border: 1px solid #5c2d2d; text-align: center; color: #ff6b6b; font-size: 0.95rem; }
        form { background: var(--card); padding: 2rem; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #aaa; }
        input { width: 100%; padding: 0.9rem; margin-bottom: 1.2rem; background: #222; border: 1px solid var(--border); border-radius: 6px; color: var(--text); font-size: 1rem; }
        input:focus { outline: none; border-color: var(--accent); }
        button { width: 100%; padding: 1rem; background: var(--accent); color: white; border: none; border-radius: 6px; font-size: 1.1rem; cursor: pointer; transition: background 0.3s; }
        button:hover { background: var(--accent-hover); }
        .result-section { margin-top: 2.5rem; display: none; }
        .result-card { background: var(--card); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border); }
        h3 { color: var(--accent); margin-bottom: 1rem; }
        pre { white-space: pre-wrap; background: #111; padding: 1.2rem; border-radius: 8px; font-family: 'Consolas', monospace; font-size: 0.95rem; line-height: 1.5; }
        #progress { margin-top: 1.5rem; padding: 1rem; background: #222; border-radius: 8px; }
        .status { margin: 0.5rem 0; color: #aaa; }
        .spinner { display: inline-block; width: 1rem; height: 1rem; border: 3px solid #ccc; border-top-color: var(--accent); border-radius: 50%; animation: spin 1s linear infinite; margin-right: 0.5rem; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>Personalized Interview DM Generator</h1>
        <div class="disclaimer">""" + DISCLAIMER + """</div>

        <form id="dm-form" method="POST">
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

        <div id="progress">
            <div class="status"><span class="spinner"></span>Starting research...</div>
            <div id="status-messages"></div>
        </div>

        <div class="result-section" id="result-section">
            <div class="result-card">
                <h3>Generated DM</h3>
                <pre id="dm-result"></pre>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('dm-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const progress = document.getElementById('progress');
            const status = document.getElementById('status-messages');
            const resultSection = document.getElementById('result-section');
            const dmResult = document.getElementById('dm-result');

            progress.style.display = 'block';
            status.innerHTML = '';
            resultSection.style.display = 'none';
            dmResult.textContent = '';

            const formData = new FormData(form);
            const data = Object.fromEntries(formData);

            const eventSource = new EventSource(`/stream_dm?${new URLSearchParams(data)}`);

            eventSource.onmessage = (event) => {
                const message = event.data.replace('data: ', '').trim();

                if (message === '[DONE]') {
                    eventSource.close();
                    progress.style.display = 'none';
                    resultSection.style.display = 'block';
                } else if (message.includes('DM generated successfully')) {
                    // Wait for the next chunk with actual DM content
                } else if (!message.includes('Starting') && !message.includes('Researching') && !message.includes('complete') && message !== '[DONE]') {
                    // This is the final DM - display it
                    dmResult.textContent = message;
                } else {
                    // Progress message
                    const msg = document.createElement('div');
                    msg.className = 'status';
                    msg.textContent = message;
                    status.appendChild(msg);
                    status.scrollTop = status.scrollHeight;
                }
            };

            eventSource.onerror = () => {
                status.innerHTML += '<div class="status">Error: Connection lost. Please try again.</div>';
                eventSource.close();
            };
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(INDEX_HTML, result=None)

@app.route('/stream_dm')
@limiter.limit("5 per minute")
def stream_dm():
    person_name = request.args.get('person_name', '').strip()
    niche = request.args.get('niche', '').strip()
    youtube_channel = request.args.get('youtube_channel', '').strip()
    name = request.args.get('name', '').strip()

    if not all([person_name, niche, youtube_channel, name]):
        return Response("Missing required fields", status=400)

    def generate_sync():
        yield "data: Starting research...\n\n"

        inputs = {
            "person_name": person_name,
            "niche": niche,
            "youtube_channel": youtube_channel,
            "name": name,
            "current_year": str(datetime.now().year)
        }

        try:
            yield "data: Researching person and niche...\n\n"

            # Run async crew synchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                crew_result = loop.run_until_complete(
                    asyncio.to_thread(SocialMediaManager().crew().kickoff, inputs=inputs)
                )
            finally:
                loop.close()

            yield "data: Research complete. Generating DM...\n\n"
            yield "data: DM generated successfully!\n\n"
            # Send the full DM as one chunk
            yield f"data: {crew_result}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    return Response(generate_sync(), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
