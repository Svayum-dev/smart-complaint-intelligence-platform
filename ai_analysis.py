"""
ai_analysis.py — Gemini AI integration for SCIP
Analyzes complaint text and returns structured classification results.
Uses the google-genai SDK (google.genai).
"""

import os
import json
import re

# Load .env if present (optional convenience for local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from google import genai
from google.genai import types

VALID_CATEGORIES = [
    'Roads & Infrastructure', 'Water Supply', 'Electricity',
    'Sanitation', 'Public Safety', 'Noise Pollution',
    'Parks & Recreation', 'Drainage',
]

VALID_PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

DEPARTMENT_MAP = {
    'Roads & Infrastructure': 'Civil & Maintenance Dept.',
    'Water Supply':           'Water & Utilities Dept.',
    'Electricity':            'Electrical Maintenance Dept.',
    'Sanitation':             'Sanitation & Hygiene Dept.',
    'Public Safety':          'Security & Safety Dept.',
    'Noise Pollution':        'Community Relations Dept.',
    'Parks & Recreation':     'Parks & Amenities Dept.',
    'Drainage':               'Drainage & Civil Works Dept.',
}

SYSTEM_PROMPT = """You are an AI assistant for a Smart Society Complaint Intelligence Platform.
Your job is to analyze resident complaints and classify them accurately.

You MUST respond with ONLY valid JSON — no markdown, no explanation, no extra text.

Return exactly this structure:
{
  "category": "<one of the valid categories>",
  "priority": "<Low|Medium|High|Critical>",
  "department": "<responsible department name>",
  "summary": "<2-3 sentence insight: what the issue is, why this priority level, and what action is needed>"
}

Valid categories: Roads & Infrastructure, Water Supply, Electricity, Sanitation, Public Safety, Noise Pollution, Parks & Recreation, Drainage

Priority guidelines:
- Critical: Immediate safety risk, water/power outage affecting many, health hazard
- High: Significant inconvenience, infrastructure damage, security concern
- Medium: Moderate nuisance, affects some residents, not urgent
- Low: Minor cosmetic/administrative issues, low impact"""


def analyze_complaint(title: str, description: str, location: str = '') -> dict | None:
    """
    Analyze a complaint using Gemini and return classification results.

    Returns a dict with keys: category, priority, department, summary
    Returns None if the API call fails or key is missing.
    """
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        print('[AI] GEMINI_API_KEY not set — skipping AI analysis.')
        return None

    user_text = f"Title: {title}"
    if description:
        user_text += f"\nDescription: {description}"
    if location:
        user_text += f"\nLocation: {location}"

    try:
        if api_key.startswith('sk-or-v1-'):
            import requests
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://127.0.0.1:5000",
                "X-Title": "SCIP"
            }
            model = os.environ.get('OPENROUTER_MODEL', 'google/gemini-2.5-flash')


            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.2,
                "max_tokens": 1000
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            if response.status_code != 200:
                print(f'[AI] OpenRouter error {response.status_code}: {response.text}')
                return None
            data = response.json()
            raw = data['choices'][0]['message']['content'].strip()
        else:
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=user_text,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                ),
            )
            raw = response.text.strip()

        # Strip markdown code fences if Gemini wraps output in them
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)

        result = json.loads(raw)


        # Validate & sanitize fields
        category   = result.get('category', '').strip()
        priority   = result.get('priority', '').strip()
        department = result.get('department', '').strip()
        summary    = result.get('summary', '').strip()

        if category not in VALID_CATEGORIES:
            category = _best_match(category, VALID_CATEGORIES)
        if priority not in VALID_PRIORITIES:
            priority = 'Medium'

        department = department or DEPARTMENT_MAP.get(category, 'General Administration')

        return {
            'category':   category,
            'priority':   priority,
            'department': department,
            'summary':    summary,
        }

    except json.JSONDecodeError as e:
        print(f'[AI] JSON parse error: {e} | Raw: {raw[:200]}')
        return None
    except Exception as e:
        print(f'[AI] Gemini API error: {e}')
        return None


def _best_match(value: str, options: list[str]) -> str:
    """Return the closest option by case-insensitive substring match."""
    v = value.lower()
    for opt in options:
        if v in opt.lower() or opt.lower() in v:
            return opt
    return options[0]
