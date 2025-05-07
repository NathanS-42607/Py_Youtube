import yt_dlp
import os
from pathlib import Path
import sys
import argparse
import logging
import time
from urllib.error import HTTPError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('youtube_downloader.log')
    ]
)
logger = logging.getLogger(__name__)

# Configure yt-dlp options
yt_dlp.utils.std_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Sec-Fetch-Mode': 'navigate',
}

# Add retry mechanism
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes')
        downloaded = d.get('downloaded_bytes')
        if total and downloaded:
            percent = (downloaded / total) * 100
            logger.info(f"Downloading... {percent:.1f}% complete")
    elif d['status'] == 'finished':
        logger.info("Download completed")
    elif d['status'] == 'error':
        logger.error(f"Download error: {d.get('error', 'Unknown error')}")

def download_video(url):
    """Download video using yt-dlp with enhanced error handling"""
    try:
        # Validate URL format
        if not url.startswith('https://www.youtube.com/') and not url.startswith('https://youtu.be/'):
            raise ValueError("Invalid YouTube URL format")

        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'downloads')
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Starting download for URL: {url}")
        
        # Set yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'max_filesize': None,
            'ignoreerrors': False,
            'retries': 10,
            'sleep_interval': 2,
            'max_sleep_interval': 30,
            'extract_flat': False,
            'force_generic_extractor': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'socket_timeout': 60,
            'extractor_args': {
                'youtube': {
                    'player_client': 'web',
                    'player_skip_download': False,
                    'player_from_html': True,
                    'player_skip_internal': False,
                }
            },
            'player_client': 'web',
            'player_from_html': True,
            'player_skip_internal': False,
            'age_limit': 0,
            'verbose': True,
            'progress_hooks': [progress_hook],
            'retry_on_unavailable': True,
            'retry_on_error': True,
            'sleep_interval': 2,
            'max_sleep_interval': 30,
            'fragment_retries': 10,
            'http_chunk_size': 1048576,
            'http_no_cache': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive'
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
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
                filename = f"{info['title']}.mp4"
                full_path = os.path.join(output_path, filename)
                print(f"File saved to: {full_path}")
                print(f"File exists: {os.path.exists(full_path)}")
                print(f"File size: {os.path.getsize(full_path) / (1024*1024):.2f} MB")
                print(f"Returning filename: {filename}")
                return filename
            except yt_dlp.utils.DownloadError as e:
                if 'Precondition check failed' in str(e):
                    raise ValueError("YouTube is blocking this download. Please try again later or use a different video.")
                raise ValueError(f"Failed to download video: {str(e)}")
            except yt_dlp.utils.ExtractorError as e:
                if 'Precondition check failed' in str(e):
                    raise ValueError("YouTube is blocking this download. Please try again later or use a different video.")
                raise ValueError(f"Failed to extract video information: {str(e)}")
            except Exception as e:
                raise ValueError(f"An unexpected error occurred: {str(e)}")
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

def download_video(url):
    """Download a YouTube video with error handling and retries"""
    ydl_opts = {
        'progress_hooks': [progress_hook],
        'format': 'best[ext=mp4]',
        'outtmpl': '%(title)s.%(ext)s',
        'retries': MAX_RETRIES,
        'fragment_retries': MAX_RETRIES,
        'http_headers': yt_dlp.utils.std_headers
    }

    for attempt in range(MAX_RETRIES):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Attempting to download video (attempt {attempt + 1}/{MAX_RETRIES})")
                ydl.download([url])
                return True
        except HTTPError as e:
            if e.code == 403:
                logger.warning(f"Received 403 error, retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
                continue
            raise
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            return False
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download YouTube videos')
    parser.add_argument('url', help='YouTube video URL')
    args = parser.parse_args()
    
    if not download_video(args.url):
        sys.exit(1)
    
    try:
        download_video(args.url)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
