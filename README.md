# Video Splitter

A simple Python command-line tool that extracts multiple clips from a video file based on timestamp ranges and combines them into a single output video.

## Features

- Extract multiple clips from a video using timestamp ranges
- Combine all extracted clips into one output video
- Support for common video formats (MP4, AVI, MOV, etc.)
- Automatic validation of timestamps and video duration
- Clean error handling and user feedback

## Requirements

- Python 3.7+
- moviepy library

## Installation

1. Clone or download this project
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Usage (Recommended)

The easiest way to use the video splitter is directly from the command line:

```bash
python video_splitter.py <path_to_video> <timestamp_ranges> <output_path>
```

**Examples:**
```bash
# Extract clips from 0-10s, 20-30s, and 45-60s
python video_splitter.py input.mp4 "[(0,10), (20,30), (45,60)]" output.mp4

# Extract highlights from a longer video
python video_splitter.py movie.avi "[(120,180), (300,360), (600,660)]" highlights.mp4

# With full paths
python video_splitter.py "/path/to/input.mp4" "[(5,15), (30,45)]" "/path/to/output.mp4"
```

**Important Notes:**
- Timestamp ranges must be enclosed in quotes: `"[(start,end), (start,end)]"`
- Times are in seconds (not minutes:seconds)
- Use decimal numbers for precise timing: `"[(10.5, 25.3)]"`

### Python API Usage

You can also import and use the function in your Python scripts:

```python
from video_splitter import split_and_combine_video

# Define your video path and timestamp ranges
input_video = "path/to/your/video.mp4"
timestamp_ranges = [
    (10.0, 20.0),   # Extract seconds 10-20
    (30.0, 45.0),   # Extract seconds 30-45
    (60.0, 75.0)    # Extract seconds 60-75
]
output_file = "combined_clips.mp4"

# Process the video
result = split_and_combine_video(input_video, timestamp_ranges, output_file)
print(f"Combined video saved as: {result}")
```

### Creating a Custom Script

Create a new Python file (e.g., `my_video_processor.py`):

```python
from video_splitter import split_and_combine_video

# Your specific video and clips
input_video = "my_video.mp4"
clips_to_extract = [
    (0, 30),      # First 30 seconds
    (60, 120),    # 1 minute to 2 minutes
    (180, 240)    # 3 minutes to 4 minutes
]

try:
    output = split_and_combine_video(
        input_video_path=input_video,
        timestamp_ranges=clips_to_extract,
        output_path="my_highlights.mp4"
    )
    print(f"✅ Success! Video saved as: {output}")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Function Parameters

### `split_and_combine_video(input_video_path, timestamp_ranges, output_path)`

- **`input_video_path`** (str): Path to your input video file
- **`timestamp_ranges`** (List[Tuple[float, float]]): List of (start_time, end_time) pairs in seconds
- **`output_path`** (str): Output file path for the combined video

**Returns:** Path to the created output video file

## Supported Video Formats

The tool supports most common video formats including:
- MP4
- AVI
- MOV
- MKV
- WMV
- FLV

## Error Handling

The tool includes comprehensive error handling for:
- Missing input files
- Invalid timestamp ranges
- Timestamps exceeding video duration
- Video processing errors

## Examples

### Extract Highlights from a Long Video
```bash
# Extract the best moments from a 2-hour video
python video_splitter.py long_video.mp4 "[(300,360), (1800,1920), (3600,3720)]" highlights.mp4
```

### Create a Trailer from Multiple Scenes
```bash
# Create a 30-second trailer
python video_splitter.py full_movie.mp4 "[(10,15), (120,125), (300,310), (450,455)]" trailer.mp4
```

### Extract Tutorial Segments
```bash
# Extract key parts from a tutorial
python video_splitter.py tutorial.mp4 "[(30,120), (300,480), (720,900)]" condensed_tutorial.mp4
```

## Troubleshooting

### Common Issues

1. **"Input video file not found"**
   - Check that the file path is correct
   - Ensure the file exists and is readable

2. **"Start time must be less than end time"**
   - Verify your timestamp ranges have start < end
   - Check that times are in seconds (not minutes:seconds format)

3. **Memory issues with large videos**
   - Try processing shorter clips
   - Ensure you have sufficient disk space for temporary files

### Performance Tips

- Use shorter timestamp ranges for better performance
- Ensure sufficient disk space (output can be large)
- Close other applications when processing large videos

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.