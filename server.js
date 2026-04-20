import express from "express";
import Anthropic from "@anthropic-ai/sdk";
import path from "node:path";
import { fileURLToPath } from "node:url";
import "dotenv/config";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const app = express();
app.use(express.json({ limit: "16kb" }));
app.use(express.static(path.join(__dirname, "public")));

const client = new Anthropic();

const SYSTEM_PROMPT = `You are StorySprout, a warm and imaginative storyteller who crafts original bedtime-quality stories for young children.

Follow these rules every time:

TONE & CONTENT
- Kind, playful, and reassuring. No scary, violent, sad-ending, or frightening content.
- Clear beginning, middle, and end. The hero faces a small problem and solves it.
- Weave the requested moral/lesson in naturally — never preachy, never a tacked-on "the moral is...".
- Use vivid sensory details (what things look, sound, smell, and feel like).

AGE TUNING
- Ages 0-3: ~75 words total. Tiny sentences. Rhythmic, repetitive, sing-songy. Lots of animal sounds and action words (splash! hop! giggle!). Very concrete, no abstract concepts.
- Ages 3-5: ~150 words total. Short, simple sentences. Lots of repetition and sound words.
- Ages 6-8: ~250 words total. Slightly richer vocabulary. Gentle humor.
- Ages 9-12: ~350 words total. More nuance, a twist or clever idea, fuller character arcs.

OUTPUT FORMAT (critical — must follow exactly)
Produce exactly 3 scenes — beginning, middle, end. Each scene MUST be formatted like this, with nothing else between them:

===SCENE===
<2 to 4 emoji that visually depict this scene, on their own line>
<the scene's paragraph(s) of story prose>

Example:
===SCENE===
🦊🌲✨
Once upon a time, deep in the whispering pines, a little fox named Pip woke up with a question in her heart...

Do NOT include a title, preamble, scene numbers, or any text before the first ===SCENE=== marker or after the last scene. Do not label the moral.`;

function sanitize(s, max = 80) {
  if (typeof s !== "string") return "";
  return s.trim().slice(0, max);
}

const VALID_AGES = new Set(["0-3", "3-5", "6-8", "9-12"]);

app.post("/story", async (req, res) => {
  const heroName = sanitize(req.body?.heroName);
  const ageRange = sanitize(req.body?.ageRange, 8);
  const theme = sanitize(req.body?.theme);
  const moral = sanitize(req.body?.moral);
  const extraContext = sanitize(req.body?.extraContext, 300);

  if (!heroName || !theme || !moral) {
    return res.status(400).json({ error: "Please fill in hero name, theme, and moral." });
  }
  if (!VALID_AGES.has(ageRange)) {
    return res.status(400).json({ error: "Please pick an age range." });
  }

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache, no-transform");
  res.setHeader("Connection", "keep-alive");
  res.flushHeaders?.();

  const userPrompt = `Please tell me a story with these ingredients:
- Hero's name: ${heroName}
- Audience age: ${ageRange}
- Theme / setting: ${theme}
- Lesson woven in: ${moral}${extraContext ? `
- Extra details to weave in: ${extraContext}` : ""}

Remember the ===SCENE=== format exactly.`;

  try {
    const stream = client.messages.stream({
      model: "claude-haiku-4-5",
      max_tokens: 2048,
      system: [
        {
          type: "text",
          text: SYSTEM_PROMPT,
          cache_control: { type: "ephemeral" },
        },
      ],
      messages: [{ role: "user", content: userPrompt }],
    });

    stream.on("text", (delta) => {
      res.write(`data: ${JSON.stringify({ delta })}\n\n`);
    });

    await stream.finalMessage();
    res.write(`event: done\ndata: {}\n\n`);
    res.end();
  } catch (err) {
    console.error("Story generation failed:", err);
    const message =
      err instanceof Anthropic.APIError
        ? `API error ${err.status}: ${err.message}`
        : "Something went wrong while writing the story.";
    res.write(`event: error\ndata: ${JSON.stringify({ message })}\n\n`);
    res.end();
  }
});

const PORT = Number(process.env.PORT) || 3000;
app.listen(PORT, () => {
  console.log(`🌱 StorySprout listening on http://localhost:${PORT}`);
});
