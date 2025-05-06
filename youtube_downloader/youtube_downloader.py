from pytube import YouTube
import os
from pathlib import Path

def download_video(url, output_path):
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Initialize YouTube object
        yt = YouTube(url)
        
        # Get video details
        print(f"\nDownloading: {yt.title}")
        print(f"Duration: {yt.length} seconds")
        
        # Get the best stream
        stream = yt.streams.get_highest_resolution()
        
        # Print file size
        print(f"File size: {stream.filesize / (1024*1024):.2f} MB")
        
        print("\nStarting download...")
        
        # Download the video
        stream.download(output_path=output_path)
        
        print("\nDownload completed successfully!")
        print(f"File saved to: {os.path.join(output_path, stream.default_filename)}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    # Default download directory
    default_path = str(Path.home() / "Downloads")
    
    # Get YouTube URL from user
    url = input("Enter the YouTube video URL: ")
    
    # Ask for custom download path
    use_default = input(f"\nUse default download path ({default_path})? (y/n): ").lower()
    if use_default != 'y':
        custom_path = input("Enter custom download path: ")
        output_path = custom_path
    else:
        output_path = default_path
    
    download_video(url, output_path)

if __name__ == "__main__":
    main()
