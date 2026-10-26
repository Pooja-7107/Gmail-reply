
import os
import json

from dotenv import load_dotenv

from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


API_KEY = os.getenv(
    "GOOGLE_API_KEY"
)


if not API_KEY:

    raise ValueError(
        "GOOGLE_API_KEY is missing."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY
)


MODEL = "gemini-2.5-flash"


# ============================================================
# ANALYZER AGENT
# ============================================================

def analyzer_agent(
    sender,
    subject,
    body
):

    prompt = f"""
You are an Email Analyzer Agent.

Analyze the following email.

Sender:
{sender}

Subject:
{subject}

Email:
{body}


Return JSON with:

{{
    "category": "one of: work, personal, meeting,
    support, sales, college, spam, other",

    "priority": "low, medium, high",

    "requires_reply": true or false,

    "summary": "short summary",

    "key_points": [
        "point 1",
        "point 2"
    ]
}}

Return ONLY valid JSON.
"""


    response = client.models.generate_content(

        model=MODEL,

        contents=prompt
    )


    text = response.text.strip()


    # --------------------------------------------------------
    # REMOVE MARKDOWN CODE BLOCK
    # --------------------------------------------------------

    if text.startswith(
        "```"
    ):

        text = (
            text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )


    return json.loads(
        text
    )


# ============================================================
# REPLY AGENT
# ============================================================

def reply_agent(
    sender,
    subject,
    body,
    analysis
):

    prompt = f"""
You are a professional Email Reply Agent.

Create a reply to the email below.

Sender:
{sender}

Subject:
{subject}

Original Email:
{body}


Email Analysis:
{json.dumps(analysis, indent=2)}


Instructions:

1. Be professional.
2. Be polite.
3. Keep the reply concise.
4. Directly address the sender's request.
5. Do not invent facts.
6. If information is missing, politely ask for it.
7. Do not mention that AI generated the response.
8. Do not include a subject line.
9. Return only the email body.
"""


    response = client.models.generate_content(

        model=MODEL,

        contents=prompt
    )


    return response.text.strip()


# ============================================================
# QUALITY AGENT
# ============================================================

def quality_agent(
    original_email,
    draft_reply
):

    prompt = f"""
You are an Email Quality Control Agent.

Check whether this proposed reply is safe
and appropriate.

ORIGINAL EMAIL:

{original_email}


PROPOSED REPLY:

{draft_reply}


Check:

1. Does it answer the email?
2. Is it professional?
3. Is it polite?
4. Does it invent information?
5. Does it contain inappropriate claims?
6. Is it concise?


Return ONLY JSON:

{{
    "approved": true or false,

    "score": 1 to 10,

    "reason": "explanation",

    "improvements": [
        "improvement 1"
    ]
}}
"""


    response = client.models.generate_content(

        model=MODEL,

        contents=prompt
    )


    text = response.text.strip()


    if text.startswith(
        "```"
    ):

        text = (
            text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )


    return json.loads(
        text
    )
