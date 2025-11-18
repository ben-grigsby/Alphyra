import whisper
import os

def transcribe_mp3(input_path, output_dir):
    """
    Transcribe an MP3 audio file using OpenAI Whisper and save the text output.

    Args:
        input_path (str): Path to the MP3 file to be transcribed.
        output_dir (str): Directory where the resulting transcript (.txt) file will be saved.
                          The directory will be created if it does not already exist.

    Returns:
        str: The full file path to the saved transcript (.txt).

    Notes:
        - Uses the Whisper "base" model for transcription.
        - Output transcript is saved as a UTF-8 encoded .txt file.
    """
    model = whisper.load_model("base")
    result = model.transcribe(input_path)
    transcript = result['text']

    os.makedirs(output_dir, exist_ok=True)


    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.txt")

    with open(output_path, "w", encoding='utf-8') as f:
        f.write(transcript)
    
    print(f"Saved transcription to {output_path}")
    return output_path


if __name__ == '__main__':
    input_path = 'downloads/mp3/nvidia_test.mp3'
    output_path = 'downloads/transcriptions'
    
    print(f"Transcribing {os.path.basename(input_path)} and saving to {output_path}...")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"[WARNING] File not found: {input_path}")
    
    transcribe_mp3(input_path, output_path)
    
    print(f"Successfully saved {os.path.basename(input_path)} to {output_path}")