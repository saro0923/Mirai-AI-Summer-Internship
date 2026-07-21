# AI Visual Novel Engine

Assignment 5 project: an AI-powered visual novel engine built with Streamlit, Gemini, Pollinations AI, and gTTS.

## Features

- Select a story genre and art style from the sidebar.
- Generate an opening scene with the Gemini API.
- Parse Gemini output as structured JSON.
- Display the generated scene text.
- Generate a scene image using Pollinations AI.
- Convert every scene narration to speech using gTTS.
- Show three dynamic choices for every scene.
- Continue the story when the user clicks a choice.
- Remember previous scenes using Streamlit Session State.
- Display the full story history as the adventure grows.
- Restart the story from the sidebar.

## Project Structure

```text
Visual_Novel_Engine/
|-- app.py
|-- requirements.txt
|-- README.md
`-- .gitignore
```

Generated files such as audio narration, virtual environments, cache folders, and `.env` files are ignored by Git.

## Demo Video

[Watch the demo video](https://drive.google.com/file/d/1mMR6Exmvsqh2WRoHcBhNJXxkRUWn9w_i/view?usp=sharing)

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in this folder:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

4. Open the local URL shown by Streamlit, usually:

```text
http://127.0.0.1:8501
```

## How It Works

1. The user selects a genre and art style.
2. Gemini generates a JSON scene with:
   - `story_text`
   - `image_prompt`
   - `options`
3. The app stores the scene in `st.session_state.story_history`.
4. Pollinations AI generates an image from the image prompt.
5. gTTS creates a unique narration file for the scene.
6. The user selects one of the choices.
7. The selected choice and previous story history are sent back to Gemini.
8. A new scene is generated and appended to the story history.

## Completed Requirements

| Requirement | Status |
| --- | --- |
| Streamlit UI | Completed |
| Genre and art style selection | Completed |
| Gemini API integration | Completed |
| JSON story generation | Completed |
| Story display | Completed |
| AI image generation | Completed |
| Text-to-speech narration | Completed |
| Dynamic choice buttons | Completed |
| Story continuation | Completed |
| Session State story memory | Completed |
| Story history display | Completed |

## Notes

- The Raw JSON display is hidden for a cleaner submission UI.
- Narration files are saved uniquely as `audio/scene_1.mp3`, `audio/scene_2.mp3`, and so on.
- The `Restart Story` button clears session history and starts a fresh adventure.
