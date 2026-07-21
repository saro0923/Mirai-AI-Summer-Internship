from gtts import gTTS
import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import json
import urllib.parse

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# -----------------------------
# Cache Gemini Client
# -----------------------------
@st.cache_resource
def get_client():
    return genai.Client(api_key=api_key)


client = get_client() if api_key else None


# -----------------------------
# Helpers
# -----------------------------
def clean_json_response(response_text):
    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()

    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()

    return cleaned


def normalize_story(raw_story):
    story_text = raw_story.get("story_text", "").strip()
    image_prompt = raw_story.get("image_prompt", "").strip()
    options = raw_story.get("options", [])

    if not story_text or not image_prompt or not isinstance(options, list):
        raise ValueError("Gemini response must include story_text, image_prompt, and options.")

    options = [str(option).strip() for option in options if str(option).strip()]

    if len(options) < 3:
        raise ValueError("Gemini response must include at least three choices.")

    return {
        "story_text": story_text,
        "image_prompt": image_prompt,
        "options": options[:3],
    }


def build_history_context():
    if not st.session_state.story_history:
        return "No previous scenes yet."

    history_lines = []
    for index, scene in enumerate(st.session_state.story_history, start=1):
        selected_choice = scene.get("selected_choice")
        if selected_choice:
            history_lines.append(f"Player choice before Scene {index}: {selected_choice}")
        history_lines.append(f"Scene {index}: {scene['story_text']}")

    return "\n".join(history_lines)


def build_story_prompt(genre, art_style, selected_choice=None):
    if selected_choice:
        story_instruction = f"""
Continue the same interactive visual novel.
The player selected this choice: {selected_choice}

Previous story history:
{build_history_context()}

Write the next scene as a direct consequence of the selected choice.
"""
    else:
        story_instruction = "Write the opening scene for a new interactive visual novel."

    return f"""
You are an AI Visual Novel Generator.

Genre: {genre}
Art Style: {art_style}

{story_instruction}

Return ONLY valid JSON.

Use exactly this format:

{{
    "story_text": "Scene text goes here.",
    "image_prompt": "Detailed prompt for image generation in the selected art style.",
    "options": [
        "Choice 1",
        "Choice 2",
        "Choice 3"
    ]
}}

Rules:
- Do not use markdown.
- Do not wrap the JSON in code fences.
- Return only JSON.
- Keep the story continuous with earlier scenes.
- Make each choice meaningfully change what can happen next.
"""


def create_audio_file(story_text, scene_number):
    audio_dir = "audio"
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, f"scene_{scene_number}.mp3")

    tts = gTTS(text=story_text, lang="en")
    tts.save(audio_path)

    return audio_path


def create_image_url(image_prompt, art_style):
    full_prompt = f"{image_prompt}, {art_style} visual novel scene, detailed, cinematic"
    encoded_prompt = urllib.parse.quote(full_prompt)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=768"


def generate_scene(genre, art_style, selected_choice=None):
    if client is None:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file before starting the story.")

    prompt = build_story_prompt(genre, art_style, selected_choice)

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    story = normalize_story(json.loads(clean_json_response(response.text)))
    scene_number = len(st.session_state.story_history) + 1

    story["scene_number"] = scene_number
    story["selected_choice"] = selected_choice
    story["image_url"] = create_image_url(story["image_prompt"], art_style)
    story["audio_path"] = create_audio_file(story["story_text"], scene_number)

    st.session_state.story_history.append(story)


def reset_story():
    st.session_state.story_history = []


def render_scene(scene):
    st.subheader(f"Scene {scene['scene_number']}")

    if scene.get("selected_choice"):
        st.caption(f"Your choice: {scene['selected_choice']}")

    st.write(scene["story_text"])

    st.image(
        scene["image_url"],
        caption="AI Generated Scene",
        use_container_width=True,
    )

    st.audio(scene["audio_path"])


# -----------------------------
# Session State
# -----------------------------
if "story_history" not in st.session_state:
    st.session_state.story_history = []


# -----------------------------
# Main Page
# -----------------------------
st.title("AI Visual Novel")
st.write("Welcome to the Multi-Modal Visual Novel")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Story Settings")

genre = st.sidebar.selectbox(
    "Choose Story Genre",
    [
        "Fantasy",
        "Sci-Fi",
        "Horror",
        "Adventure",
        "Mystery",
    ],
)

art_style = st.sidebar.selectbox(
    "Choose Art Style",
    [
        "Anime",
        "Realistic",
        "Pixel Art",
        "Oil Painting",
        "Cyberpunk",
    ],
)

if st.sidebar.button("Restart Story"):
    reset_story()
    st.rerun()

# -----------------------------
# Display Selected Settings
# -----------------------------
st.write("## Selected Settings")
st.write(f"**Genre:** {genre}")
st.write(f"**Art Style:** {art_style}")

st.divider()

# -----------------------------
# Story Controls
# -----------------------------
if not st.session_state.story_history:
    if st.button("Start Story"):
        try:
            with st.spinner("Generating the opening scene..."):
                generate_scene(genre, art_style)
            st.rerun()
        except Exception as e:
            st.error("Failed to generate the story.")
            st.exception(e)
else:
    st.write(f"Story scenes generated: **{len(st.session_state.story_history)}**")

# -----------------------------
# Story History
# -----------------------------
if st.session_state.story_history:
    st.header("Story History")

    for scene in st.session_state.story_history:
        render_scene(scene)
        st.divider()

    latest_scene = st.session_state.story_history[-1]

    st.subheader("Choices")

    for index, option in enumerate(latest_scene["options"], start=1):
        if st.button(option, key=f"choice_{latest_scene['scene_number']}_{index}"):
            try:
                with st.spinner("Continuing the story..."):
                    generate_scene(genre, art_style, selected_choice=option)
                st.rerun()
            except Exception as e:
                st.error("Failed to continue the story.")
                st.exception(e)
