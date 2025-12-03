import whisper
import os
import subprocess

def transcribe_mp3(input_path, output_dir, model_size="base", timeout_sec=1200):
    """
    Transcribe audio using subprocess call to Whisper CLI (installed via whisper package).
    """

    # Make sure output dir exists
    os.makedirs(output_dir, exist_ok=True)

    command = [
        "whisper",
        input_path,
        "--model", model_size,
        "--output_dir", output_dir,
        "--output_format", "txt"
    ]

    try:
        print(f"[DEBUG] Transcribing via subprocess: {input_path}")
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout_sec)

        if result.returncode != 0:
            print(f"[ERROR] Whisper failed: {result.stderr}")
            raise RuntimeError("Whisper subprocess failed")

        print(f"[INFO] Subprocess transcription completed: {input_path}")
        
        # Determine the expected output file path
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.txt")

        return output_path

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Whisper transcription exceeded {timeout_sec} seconds for file: {input_path}")
        if os.path.exists(input_path):
            os.remove(input_path)
            print(f"[CLEANUP] Deleted input file due to timeout: {input_path}")
        raise


    except Exception as e:
        print(f"[ERROR] Subprocess transcription failed: {e}. File: {input_path}")
        if os.path.exists(input_path):
            os.remove(input_path)
            print(f"[CLEANUP] Deleted input file due to failure: {input_path}")
        raise


if __name__ == '__main__':
    input_path = 'downloads/mp3/nvidia_test.mp3'
    output_path = 'downloads/transcriptions'
    
    print(f"Transcribing {os.path.basename(input_path)} and saving to {output_path}...")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"[WARNING] File not found: {input_path}")
    
    transcribe_mp3(input_path, output_path)
    
    print(f"Successfully saved {os.path.basename(input_path)} to {output_path}")