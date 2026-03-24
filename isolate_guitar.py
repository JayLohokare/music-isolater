import os
import argparse
import subprocess
import sys

def check_dependencies():
    """Check if demucs is installed in the current environment."""
    try:
        import demucs
        return True
    except ImportError:
        # We can also check if the command line tool exists
        import shutil
        return shutil.which('demucs') is not None

def isolate_guitar(input_file, output_dir):
    """Isolate the guitar track from a given audio file using Demucs (htdemucs_6s model)."""
    
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        sys.exit(1)
        
    print(f"Analyzing and processing '{input_file}'...")
    print("This might take a few minutes depending on your computer's performance and the length of the song.")
    print("Demucs will automatically download the required AI models on its first run.")
    
    # We use htdemucs_6s for 6 sources (vocals, drums, bass, other, piano, guitar)
    # The --two-stems=guitar flag saves the guitar and a combined mix of everything else (no_guitar).
    command = [
        "demucs",
        "-n", "htdemucs_6s",
        "--two-stems=guitar",
        "-o", output_dir,
        input_file
    ]
    
    try:
        # Run Demucs via command line interface
        subprocess.run(command, check=True)
        
        # Determine the expected output path
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        guitar_file = os.path.join(output_dir, "htdemucs_6s", base_name, "guitar.wav")
        no_guitar_file = os.path.join(output_dir, "htdemucs_6s", base_name, "no_guitar.wav")
        
        print("\n\n" + "="*50)
        print("EXTRACTION COMPLETE!")
        print("="*50)
        
        if os.path.exists(guitar_file):
            print(f"Guitar track successfully isolated!")
            print(f"🎸 Isolated Guitar: {guitar_file}")
            print(f"🎧 Backing Track (No Guitar): {no_guitar_file}")
        else:
            print(f"Processing finished, but could not locate the file at {guitar_file}.")
            print(f"Check the output directory: {os.path.join(output_dir, 'htdemucs_6s', base_name)}")
            
    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred while running demucs: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\nError: Could not find 'demucs' executable.")
        print("Please ensure you have installed it via pip: pip install demucs")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Isolate guitar tracks from a song using Demucs.")
    parser.add_argument("input_file", help="Path to the audio file (e.g. mp3, wav, flac)")
    parser.add_argument("-o", "--output_dir", default="separated_stems", help="Directory where separated tracks will be saved")
    
    args = parser.parse_args()
    
    if not check_dependencies():
        print("Error: Demucs is not installed or not in PATH.")
        print("Please install the required libraries by running:")
        print("pip install -r requirements.txt")
        sys.exit(1)
        
    isolate_guitar(args.input_file, args.output_dir)
