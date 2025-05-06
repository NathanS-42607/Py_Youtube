import yt_dlp
import os
from pathlib import Path

def download_video(url, output_path):
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': False,
            'no_warnings': False,
            'merge_output_format': 'mp4'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"\nDownloading: {info['title']}")
            print(f"Duration: {info['duration']} seconds")
            
            # Try to get file size if available
            file_size = info.get('filesize')
            if file_size:
                print(f"File size: {file_size / (1024*1024):.2f} MB")
            else:
                print("File size: Not available")
            
            print("\nStarting download...")
            ydl.download([url])
            
        print("\nDownload completed successfully!")
        print(f"File saved to: {os.path.join(output_path, info['title'] + '.mp4')}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes')
        downloaded = d.get('downloaded_bytes')
        if total and downloaded:
            percent = (downloaded / total) * 100
            print(f"Download progress: {percent:.1f}%", end='\r')

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
