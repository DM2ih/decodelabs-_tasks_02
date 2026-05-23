import json
import requests

def analyze_full_transcript(full_transcript_text, api_key):
    """Sends the condensed transcript to Llama-3.3 on Groq to extract viral clips."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are an expert AI video editor and social media strategist.
Analyze the entire timestamped transcript below and select exactly 5 distinct, highly engaging viral moments.

CRITICAL RULES:
1. The 5 clips MUST be spread out across the entire timeline of the video. Look for distinct topics or shifts in energy.
2. Absolute NO OVERLAPPING or duplicate context. Each clip must stand completely on its own.
3. Each individual clip MUST be between 60 and 90 seconds (1 to 1.5 minutes) long. Ensure 'end_time' minus 'start_time' is between 60.0 and 90.0.

Transcript:
{full_transcript_text}

You MUST respond ONLY with a raw JSON object matching this schema. Do not write markdown blocks or prose outside the JSON:
{{
    "clips": [
        {{
            "start_time": 12.5,
            "end_time": 82.5,
            "headline": "Viral Clip Title",
            "caption": "Engaging social media caption text",
            "b_roll_description": "A highly detailed descriptive image generation prompt representing the context of this clip"
        }}
    ]
}}
"""
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Groq API Error: {response.text}")

    try:
        result_text = response.json()["choices"][0]["message"]["content"]
        return json.loads(result_text)
    except Exception as e:
        raise Exception(f"Parsing Error on LLM Response: {e}")

def process_full_transcript(transcript_json, api_key):
    """Condenses the structural segments into a compressed timeline format."""
    if not transcript_json or "segments" not in transcript_json:
        return {"clips": []}

    raw_segments = transcript_json.get("segments", [])
    condensed_lines = [f"[{seg.get('start', 0.0):.1f}s] {seg.get('text', '').strip()}" for seg in raw_segments]
    full_transcript_text = "\n".join(condensed_lines)

    final_result = analyze_full_transcript(full_transcript_text, api_key)
    if final_result and "clips" in final_result:
        return {"clips": final_result["clips"][:5]}
    return {"clips": []}