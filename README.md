# 🌱 StorySprout

Bedtime stories, dreamed up on the spot. Give it a hero, an age, a setting, and a lesson — StorySprout streams back an illustrated, narrated children's story.

## What you get

- **Live streaming** — words appear as they're written (no loading spinner).
- **Emoji illustrations** — each scene opens with a large emoji banner picked to match the scene.
- **Read aloud** — one-click narration using your browser's built-in voices (pause/resume supported).
- **Age-tuned** — vocabulary and length adjust for 3–5, 6–8, or 9–12.

## Running it

1. Install dependencies:
   ```bash
   npm install
   ```
2. Create a `.env` file in this folder with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
   (You can copy `.env.example` and fill it in.)
3. Start the server:
   ```bash
   npm start
   ```
4. Open <http://localhost:3000> in your browser.

## How it works

- **Backend** (`server.js`) — a tiny Express server that streams from Claude Haiku 4.5 via `client.messages.stream(...)` and forwards each text delta to the browser as Server-Sent Events. The system prompt is cached (`cache_control: ephemeral`) so repeat stories are faster and cheaper.
- **Frontend** (`public/index.html`) — a single HTML file. Parses the SSE stream, splits the story on `===SCENE===` markers, and renders each scene as a card with an emoji banner above the paragraph.
- **Narration** — uses the browser's built-in `SpeechSynthesis` API. No extra services, no extra API key.

## Files

| File | What it does |
| --- | --- |
| `server.js` | Express server, Claude streaming, SSE endpoint |
| `public/index.html` | UI, SSE parsing, scene rendering, narration |
| `package.json` | Dependencies and `npm start` script |
| `.env.example` | Template for your API key |

## Tweaking

- Want longer stories? Raise `max_tokens` in `server.js`.
- Want a different voice? Edit the `prefer` list in `pickVoice()` inside `index.html`.
- Want a different model? Change `model: "claude-haiku-4-5"` in `server.js` (e.g. to `claude-sonnet-4-6` for richer prose at higher cost).
