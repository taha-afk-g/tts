import os
from flask import Flask, request, jsonify, send_file, render_template
import uuid  # For unique filenames
from google.cloud import texttospeech

app = Flask(__name__)

# Set the output directory for audio files
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Manually set the cache directory
os.environ["XDG_CACHE_HOME"] = os.path.expanduser("~/.local/share/tts")

# Initialize the Google Cloud TTS client
client = texttospeech.TextToSpeechClient()

VOICE_NAME_MAPPING = {
    "en-US-Casual-K": "Generic American Male A",
    "en-US-Journey-D": "Journey American Male A",
    "en-US-Journey-F": "Journey American Female A",
    "en-US-Journey-O": "Journey American Female B",
    "en-US-Neural2-A": "Neural2 American Male A",
    "en-US-Neural2-C": "Neural2 American Female A",
    "en-US-Neural2-D": "Neural2 American Male B",
    "en-US-Neural2-E": "Neural2 American Female B",
    "en-US-Neural2-F": "Neural2 American Female C",
    "en-US-Neural2-G": "Neural2 American Female D",
    "en-US-Neural2-H": "Neural2 American Female E",
    "en-US-Neural2-I": "Neural2 American Male C",
    "en-US-Neural2-J": "Neural2 American Male D",
    "en-US-News-K": "News American Female A",
    "en-US-News-L": "News American Female B",
    "en-US-News-N": "News American Male A",
    "en-US-Polyglot-1": "Generic American Male B",
    "en-US-Standard-A": "Standard American Male A",
    "en-US-Standard-B": "Standard American Male B",
    "en-US-Standard-C": "Standard American Female A",
    "en-US-Standard-D": "Standard American Male C",
    "en-US-Standard-E": "Standard American Female B",
    "en-US-Standard-F": "Standard American Female C",
    "en-US-Standard-G": "Standard American Female D",
    "en-US-Standard-H": "Standard American Female E",
    "en-US-Standard-I": "Standard American Male D",
    "en-US-Standard-J": "Standard American Male E",
    "en-US-Studio-O": "Studio American Female A",
    "en-US-Studio-Q": "Studio American Male A",
    "en-US-Wavenet-A": "Wavenet American Male A",
    "en-US-Wavenet-B": "Wavenet American Male B",
    "en-US-Wavenet-C": "Wavenet American Female A",
    "en-US-Wavenet-D": "Wavenet American Male C",
    "en-US-Wavenet-E": "Wavenet American Female B",
    "en-US-Wavenet-F": "Wavenet American Female C",
    "en-US-Wavenet-G": "Wavenet American Female D",
    "en-US-Wavenet-H": "Wavenet American Female E",
    "en-US-Wavenet-I": "Wavenet American Male D",
    "en-US-Wavenet-J": "Wavenet American Male E",

    "en-AU-Journey-D": "Journey Australian Male A",
    "en-AU-Journey-F": "Journey Australian Female A",
    "en-AU-Journey-O": "Journey Australian Female B",
    "en-AU-Neural2-A": "Neural2 Australian Female A",
    "en-AU-Neural2-B": "Neural2 Australian Male A",
    "en-AU-Neural2-C": "Neural2 Australian Female B",
    "en-AU-Neural2-D": "Neural2 Australian Male B",
    "en-AU-News-E": "News Australian Female A",
    "en-AU-News-F": "News Australian Female B",
    "en-AU-News-G": "News Australian Male A",
    "en-AU-Polyglot-1": "Generic Australian Male A",
    "en-AU-Standard-A": "Standard Australian Female A",
    "en-AU-Standard-B": "Standard Australian Male A",
    "en-AU-Standard-C": "Standard Australian Female B",
    "en-AU-Standard-D": "Standard Australian Male B",
    "en-AU-Wavenet-A": "Wavenet Australian Female A",
    "en-AU-Wavenet-B": "Wavenet Australian Male A",
    "en-AU-Wavenet-C": "Wavenet Australian Female B",
    "en-AU-Wavenet-D": "Wavenet Australian Male B",

    "en-GB-Journey-D": "Journey British Male A",
    "en-GB-Journey-F": "Journey British Female A",
    "en-GB-Journey-O": "Journey British Female B",
    "en-GB-Neural2-N": "Neural2 British Female A",
    "en-GB-Neural2-O": "Neural2 British Male A",
    "en-GB-News-G": "News British Female A",
    "en-GB-News-H": "News British Female B",
    "en-GB-News-I": "News British Female C",
    "en-GB-News-J": "News British Male A",
    "en-GB-News-K": "News British Male B",
    "en-GB-News-L": "News British Male C",
    "en-GB-News-M": "News British Male D",
    "en-GB-Standard-A": "Standard British Female A",
    "en-GB-Standard-B": "Standard British Male A",
    "en-GB-Standard-C": "Standard British Female B",
    "en-GB-Standard-D": "Standard British Male B",
    "en-GB-Standard-F": "Standard British Female C",
    "en-GB-Standard-N": "Standard British Female D",
    "en-GB-Standard-O": "Standard British Male C",
    "en-GB-Studio-B": "Studio British Male A",
    "en-GB-Studio-C": "Studio British Female A",
    "en-GB-Wavenet-A": "Wavenet British Female A",
    "en-GB-Wavenet-B": "Wavenet British Male A",
    "en-GB-Wavenet-C": "Wavenet British Female B",
    "en-GB-Wavenet-D": "Wavenet British Male B",
    "en-GB-Wavenet-F": "Wavenet British Female C",
    "en-GB-Wavenet-N": "Wavenet British Female D",
    "en-GB-Wavenet-O": "Wavenet British Male C",

    "ar-XA-Standard-A": "Standard Arabic Female A",
    "ar-XA-Standard-B": "Standard Arabic Male A",
    "ar-XA-Standard-C": "Standard Arabic Male B",
    "ar-XA-Standard-D": "Standard Arabic Female B",
    "ar-XA-Wavenet-A": "Wavenet Arabic Female A",
    "ar-XA-Wavenet-B": "Wavenet Arabic Male A",
    "ar-XA-Wavenet-C": "Wavenet Arabic Male B",
    "ar-XA-Wavenet-D": "Wavenet Arabic Female B",

}

@app.route('/')
def index():
    # Filter voices to only include English and Arabic
    filtered_voices = {k: v for k, v in VOICE_NAME_MAPPING.items() if "en" in k or "ar" in k}
    return render_template("index.html", voices=filtered_voices)


@app.route('/tts', methods=['POST'])
def generate_tts():
    data = request.json
    text = data.get("text", "").strip()
    voice = data.get("voice", "en-US-Wavenet-D")  # Default voice

    if not text:
        return jsonify({"error": "No text provided"}), 400

    unique_filename = f"output_{uuid.uuid4().hex}.wav"
    output_file = os.path.join(OUTPUT_DIR, unique_filename)

    print(f"🔹 Generating TTS for text: {text}")
    print(f"🔹 Using voice model: {voice}")
    print(f"🔹 Saving output to: {output_file}")

    try:
        # Set up the voice parameters
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-US",  # Default language, change this dynamically if needed
            name=voice,  # Chosen voice
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,  # Default gender, can change based on user input
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        # Request the TTS API
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )

        # Write the response audio content to a file
        with open(output_file, "wb") as out:
            out.write(response.audio_content)

        print(f"✅ Successfully generated: {output_file}")
        return jsonify({"audioUrl": f"/output/{unique_filename}", "filename": unique_filename})

    except Exception as e:
        print(f"❌ Error generating TTS: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/output/<filename>')
def serve_audio(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return jsonify({"error": "File not found"}), 404

    print(f"✅ Serving file: {file_path}")
    return send_file(file_path, mimetype="audio/wav", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
