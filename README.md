# Guitar Isolator

This Python script uses [Demucs](https://github.com/adefossez/demucs) (specifically the `htdemucs_6s` model) to isolate the guitar track from any given audio file.

## Prerequisites

You need Python installed on your system. It's recommended to use a virtual environment.

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: This will install `demucs` and `PyTorch`.*

## Usage

Run the script from the terminal and provide the path to your audio file (e.g., MP3, WAV, FLAC).

```bash
python isolate_guitar.py path/to/your/song.mp3
```

### Options

You can specify a custom output directory using the `-o` or `--output_dir` flag:

```bash
python isolate_guitar.py path/to/your/song.mp3 -o my_custom_folder
```

### What to Expect

The first time you run the script, Demucs will automatically download the required AI model (`htdemucs_6s`). This might take a few minutes depending on your internet connection.

Once processing is complete, you will find two files in the output directory:
1. `guitar.wav` - The isolated guitar track.
2. `no_guitar.wav` - The rest of the song with the guitar removed (ideal for backing tracks).
