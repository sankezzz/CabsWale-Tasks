
import asyncio
from deepgram import DeepgramClient, LiveOptions, LiveTranscriptionEvents
import aiofiles

DEEPGRAM_API_KEY = "" 

FILE_PATH = 'response.wav'  # Can also be .mp3, .m4a etc



# Main async function
async def main():
    # Create the Deepgram client
    deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)

    # Set up transcription options
    options = LiveOptions(
        language="en-US",
        punctuate=True,
        model="general",
        tier="nova"
    )

    # Open a streaming transcription connection
    dg_connection = deepgram.listen.live.v("1")

    # Handle transcription results
    def on_transcript(transcript, **kwargs):
        sentence = transcript.channel.alternatives[0].transcript
        if sentence:
            print(f"📝 {sentence}")

    # Handle connection close
    def on_close(_):
        print("✅ Transcription complete.")

    dg_connection.on(LiveTranscriptionEvents.Transcript, on_transcript)
    dg_connection.on(LiveTranscriptionEvents.Close, on_close)

    # Start the connection
    if dg_connection.start(options) is False:
        print("❌ Failed to start Deepgram connection.")
        return

    # Read and send audio data
    async with aiofiles.open(FILE_PATH, 'rb') as f:
        while True:
            chunk = await f.read(4096)
            if not chunk:
                break
            dg_connection.send(chunk)
            await asyncio.sleep(0.01)  # Simulate real-time pacing

    # Finish the transcription
    dg_connection.finish()

# Run it
if __name__ == "__main__":
    asyncio.run(main())

