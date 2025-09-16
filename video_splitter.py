"""
Video Splitter - A simple tool to extract clips from a video and combine them into one output.

This module provides functionality to:
1. Take a video file path
2. Extract multiple clips based on timestamp ranges
3. Combine all clips into a single output video

Usage:
    python video_splitter.py <path_to_video> <[(start1,end1), (start2,end2), ...]> <output_path>
    
Example:
    python video_splitter.py input.mp4 "[(0,10), (20,30), (45,60)]" output.mp4
"""

import os
import sys
import re
import argparse
from typing import List, Tuple
from moviepy.editor import VideoFileClip, concatenate_videoclips


def validate_input_path(input_path: str) -> None:
    """Validate input video file path."""
    if not input_path or not input_path.strip():
        raise ValueError("Input video path cannot be empty")
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input video file not found: {input_path}")
    
    if not os.path.isfile(input_path):
        raise ValueError(f"Input path is not a file: {input_path}")
    
    if not os.access(input_path, os.R_OK):
        raise PermissionError(f"No read permission for input file: {input_path}")
    
    # Check if it's likely a video file
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp'}
    file_ext = os.path.splitext(input_path)[1].lower()
    if file_ext not in video_extensions:
        print(f"⚠️  Warning: Input file extension '{file_ext}' is not a common video format")
    
    # Check file size (warn if very large or very small)
    file_size = os.path.getsize(input_path)
    if file_size == 0:
        raise ValueError(f"Input video file is empty: {input_path}")
    elif file_size < 1024:  # Less than 1KB
        print(f"⚠️  Warning: Input file is very small ({file_size} bytes). May not be a valid video.")
    elif file_size > 5 * 1024 * 1024 * 1024:  # 5GB
        print(f"⚠️  Warning: Large input file ({file_size / (1024**3):.1f}GB). Processing may be slow.")


def validate_output_path(output_path: str) -> None:
    """Validate output video file path."""
    if not output_path or not output_path.strip():
        raise ValueError("Output video path cannot be empty")
    
    # Get directory of output file
    output_dir = os.path.dirname(os.path.abspath(output_path))
    
    # Check if directory exists
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    
    # Check if directory is writable
    if not os.access(output_dir, os.W_OK):
        raise PermissionError(f"No write permission for output directory: {output_dir}")
    
    # Check if output file already exists (warn but don't fail)
    if os.path.exists(output_path):
        print(f"⚠️  Warning: Output file already exists and will be overwritten: {output_path}")
    
    # Validate file extension
    valid_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    file_ext = os.path.splitext(output_path)[1].lower()
    if file_ext not in valid_extensions:
        print(f"⚠️  Warning: Unusual output file extension '{file_ext}'. Recommended: {', '.join(valid_extensions)}")


def split_and_combine_video(
    input_video_path: str,
    timestamp_ranges: List[Tuple[float, float]],
    output_path: str = "output_combined.mp4"
) -> str:
    """
    Extract clips from a video based on timestamp ranges and combine them into one video.
    
    Args:
        input_video_path (str): Path to the input video file
        timestamp_ranges (List[Tuple[float, float]]): List of (start_time, end_time) tuples in seconds
        output_path (str): Path for the output combined video file
        
    Returns:
        str: Path to the created output video file
        
    Raises:
        FileNotFoundError: If the input video file doesn't exist or output directory doesn't exist
        ValueError: If timestamp ranges or paths are invalid
        PermissionError: If no read/write permissions
        Exception: For other video processing errors
    """
    
    # Validate input and output paths
    validate_input_path(input_video_path)
    validate_output_path(output_path)
    
    # Validate timestamp ranges
    if not timestamp_ranges:
        raise ValueError("At least one timestamp range must be provided")
    
    # Basic type validation (detailed validation done in parse_timestamp_ranges for CLI)
    for i, (start, end) in enumerate(timestamp_ranges):
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise ValueError(f"Timestamp range {i+1}: Times must be numbers")
    
    try:
        # Load the input video
        print(f"Loading video: {input_video_path}")
        video = VideoFileClip(input_video_path)
        
        # Extract clips based on timestamp ranges
        clips = []
        total_duration = video.duration
        
        for i, (start_time, end_time) in enumerate(timestamp_ranges):
            # Validate timestamps against video duration
            if start_time >= total_duration:
                print(f"Warning: Clip {i+1} start time ({start_time}s) exceeds video duration ({total_duration}s). Skipping.")
                continue
            
            # Adjust end time if it exceeds video duration
            if end_time > total_duration:
                print(f"Warning: Clip {i+1} end time adjusted from {end_time}s to {total_duration}s")
                end_time = total_duration
            
            print(f"Extracting clip {i+1}: {start_time}s to {end_time}s")
            clip = video.subclip(start_time, end_time)
            clips.append(clip)
        
        if not clips:
            raise ValueError("No valid clips were extracted from the video")
        
        # Combine all clips into one video
        print(f"Combining {len(clips)} clips...")
        final_video = concatenate_videoclips(clips)
        
        # Write the output video
        print(f"Writing output video: {output_path}")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Clean up
        video.close()
        final_video.close()
        for clip in clips:
            clip.close()
        
        print(f"Successfully created combined video: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        raise


def parse_timestamp_ranges(ranges_str: str) -> List[Tuple[float, float]]:
    """
    Parse timestamp ranges from string format like "[(0,10), (20,30), (45,60)]"
    
    Args:
        ranges_str (str): String representation of timestamp ranges
        
    Returns:
        List[Tuple[float, float]]: List of (start_time, end_time) tuples
        
    Raises:
        ValueError: If the format is invalid
    """
    # Input validation
    if not isinstance(ranges_str, str):
        raise ValueError("Timestamp ranges must be a string")
    
    # Remove whitespace and validate basic format
    ranges_str = ranges_str.strip()
    
    if not ranges_str:
        raise ValueError("Timestamp ranges cannot be empty")
    
    if not ranges_str.startswith('[') or not ranges_str.endswith(']'):
        raise ValueError("Timestamp ranges must be enclosed in square brackets: [(start,end), ...]")
    
    # Remove outer brackets
    inner = ranges_str[1:-1].strip()
    
    if not inner:
        raise ValueError("At least one timestamp range must be provided inside brackets")
    
    # Enhanced pattern to match numbers (including integers and floats)
    # Supports: 123, 123.45, .5, but not just "." or "-"
    pattern = r'\(\s*(-?(?:[0-9]+\.?[0-9]*|\.[0-9]+))\s*,\s*(-?(?:[0-9]+\.?[0-9]*|\.[0-9]+))\s*\)'
    matches = re.findall(pattern, inner)
    
    if not matches:
        raise ValueError("Invalid timestamp format. Use: [(start,end), (start,end), ...] with valid numbers")
    
    # Check if we found all expected tuples (no malformed ones)
    # Count opening parentheses to verify all tuples were parsed
    open_parens = inner.count('(')
    if len(matches) != open_parens:
        raise ValueError("Malformed timestamp ranges. Each range must be in format (start,end)")
    
    # Convert to tuples of floats and validate values
    timestamp_ranges = []
    for i, (start_str, end_str) in enumerate(matches):
        try:
            start = float(start_str)
            end = float(end_str)
            
            # Validate individual timestamp values
            if start < 0:
                raise ValueError(f"Range {i+1}: Start time ({start}) cannot be negative")
            if end < 0:
                raise ValueError(f"Range {i+1}: End time ({end}) cannot be negative")
            if start >= end:
                raise ValueError(f"Range {i+1}: Start time ({start}) must be less than end time ({end})")
            
            timestamp_ranges.append((start, end))
            
        except ValueError as e:
            raise ValueError(f"Range {i+1}: Invalid timestamp values ({start_str}, {end_str}). Must be valid numbers.")
    
    return timestamp_ranges


def main():
    """
    Command-line interface for the video splitter.
    """
    parser = argparse.ArgumentParser(
        description="Extract and combine video clips based on timestamp ranges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python video_splitter.py input.mp4 "[(0,10), (20,30), (45,60)]" output.mp4
  python video_splitter.py /path/to/video.mp4 "[(5,15), (30,45)]" highlights.mp4
  python video_splitter.py movie.avi "[(120,180), (300,360), (600,660)]" trailer.mp4

Note: Timestamp ranges should be in seconds and enclosed in quotes.
        """
    )
    
    parser.add_argument(
        "input_video",
        help="Path to the input video file"
    )
    
    parser.add_argument(
        "timestamp_ranges",
        help="Timestamp ranges in format: [(start1,end1), (start2,end2), ...] in seconds"
    )
    
    parser.add_argument(
        "output_path",
        help="Output file path for the combined video"
    )
    
    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    try:
        # Parse timestamp ranges
        timestamp_ranges = parse_timestamp_ranges(args.timestamp_ranges)
        
        # Process the video
        print(f"Input video: {args.input_video}")
        print(f"Timestamp ranges: {timestamp_ranges}")
        print(f"Output file: {args.output_path}")
        print("-" * 50)
        
        result = split_and_combine_video(
            input_video_path=args.input_video,
            timestamp_ranges=timestamp_ranges,
            output_path=args.output_path
        )
        
        print(f"\n✅ Success! Combined video saved as: {result}")
        
    except ValueError as e:
        print(f"\n❌ Invalid input: {e}")
        print("\nExample usage:")
        print('python video_splitter.py input.mp4 "[(0,10), (20,30), (45,60)]" output.mp4')
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"\n❌ Permission denied: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("This may be due to:")
        print("- Corrupted video file")
        print("- Unsupported video format")
        print("- Insufficient system resources")
        print("- MoviePy processing error")
        sys.exit(1)


if __name__ == "__main__":
    main()
