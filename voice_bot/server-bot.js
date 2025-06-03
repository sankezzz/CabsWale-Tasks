const express = require("express");
const fs = require("fs");
const path = require("path");
const { TextToSpeechClient } = require("@google-cloud/text-to-speech");
const { SpeechClient } = require("@google-cloud/speech");
const bodyParser = require("body-parser");
const player = require("play-sound")({}); // npm install play-sound
const cors = require("cors");
const { exec } = require("child_process");

require("dotenv").config();
process.env.GOOGLE_APPLICATION_CREDENTIALS = "cred.json";

const app = express();
const port = 3000;

const speechClient = new SpeechClient();
const ttsClient = new TextToSpeechClient();

app.use(cors());
app.use(bodyParser.json());
app.use(express.static("public"));

let bufferMemory = [""];
let bufferMemoryAIResponse = [];

function extractJsonFromResponse(text) {
  const match = text.match(/\{[\s\S]*?\}/);
  if (match) {
    try {
      return JSON.parse(match[0]);
    } catch (err) {
      console.error("JSON parse error:", err);
      return {};
    }
  }
  return {};
}

// Replace this with Gemini or OpenAI/Vertex AI
async function generateAIResponse(prompt) {
  // mock response
  return `
Perfect! How many people will be travelling with you?

###JSON
{
  "source_city": "Pune",
  "destination_city": "Goa",
  "number_of_passengers": null,
  "start_date": null,
  "end_date": null
}
  `;
}

// HTML Page
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Main route
app.get("/record_audio", async (req, res) => {
  try {
    const audioPath = path.join(__dirname, "user_audio.mp3");

    // You can replace this with mic recording logic on frontend and upload to server
    if (!fs.existsSync(audioPath)) {
      return res.status(400).send("No audio found. Please upload.");
    }

    const file = fs.readFileSync(audioPath);
    const audioBytes = file.toString("base64");

    const [sttResponse] = await speechClient.recognize({
      config: {
        encoding: "MP3",
        sampleRateHertz: 16000,
        languageCode: "hi-IN",
      },
      audio: { content: audioBytes },
    });

    const transcription = sttResponse.results?.[0]?.alternatives?.[0]?.transcript?.trim();

    if (!transcription) {
      return res.status(400).send("No speech detected.");
    }

    console.log("You said:", transcription);
    bufferMemory.push(transcription);

    const prompt = `
You are Riya, a warm and friendly female cab travel assistant from कैबस्वाले...
User said: "${transcription}"
Previous conversation: "${bufferMemory.join(" ")}"
Your previous replies: "${bufferMemoryAIResponse.join(" ")}"
`;

    const aiReply = await generateAIResponse(prompt);
    const spokenPart = aiReply.split("###JSON")[0].trim();
    const jsonOutput = extractJsonFromResponse(aiReply);

    console.log("AI:", spokenPart);
    console.log("Extracted JSON:", jsonOutput);

    bufferMemoryAIResponse.push(spokenPart);

    const [ttsResponse] = await ttsClient.synthesizeSpeech({
      input: { text: spokenPart },
      voice: {
        languageCode: "hi-IN",
        name: "hi-IN-Chirp3-HD-Aoede",
        ssmlGender: "FEMALE",
      },
      audioConfig: { audioEncoding: "LINEAR16" },
    });

    const outputPath = "response.wav";
    fs.writeFileSync(outputPath, ttsResponse.audioContent, "binary");

    // Play sound
    player.play(outputPath, (err) => {
      if (err) console.error("Audio play error:", err);
    });

    return res.json({
      message: "Conversation complete!",
      transcript: transcription,
      response: spokenPart,
      json: jsonOutput,
    });
  } catch (err) {
    console.error("Error:", err);
    res.status(500).send("Something went wrong.");
  }
});

app.listen(port, () => {
  console.log(`🚀 Server running at http://localhost:${port}`);
});
