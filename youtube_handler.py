import yt_dlp
import os
from typing import Optional, Dict
import logging
import random
import time

class YouTubeHandler:
    def __init__(self, output_path: str):
        """Initialize the YouTube handler with output path."""
        self.output_path = output_path
        self._setup_ydl_opts()

    def _setup_ydl_opts(self) -> None:
        """Set up yt-dlp options for audio download."""
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch',
            'noplaylist': True,
            'postprocessor_args': [
                '-codec:a', 'libmp3lame',
                '-qscale:a', '2',
                '-ar', '44100',
                '-ac', '2'
            ],
            # Add these options to handle restrictions
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_color': True,
            'geo_bypass': True,
            'geo_verification_proxy': None,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }

    def search_and_download(self, track_info: Dict) -> Optional[str]:
        """Search for and download a track based on its metadata."""
        try:
            # Create search query with additional terms to improve results
            search_query = f"{track_info['title']} {track_info['artists'][0]} official audio"
            
            # Update output template for this specific track
            safe_title = "".join(c for c in track_info['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            self.ydl_opts['outtmpl'] = os.path.join(
                self.output_path,
                f"{safe_title}.%(ext)s"
            )

            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))

            # Perform search and download
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    # First, search for the video
                    search_result = ydl.extract_info(f"ytsearch:{search_query}", download=False)
                    if not search_result['entries']:
                        logging.warning(f"No results found for: {search_query}")
                        return None

                    # Get the first result
                    video_url = search_result['entries'][0]['url']
                    
                    # Download the video
                    ydl.download([video_url])
                    
                    # Return the path to the downloaded file
                    return os.path.join(
                        self.output_path,
                        f"{safe_title}.mp3"
                    )
                except Exception as e:
                    logging.error(f"Failed to download {search_query}: {str(e)}")
                    return None

        except Exception as e:
            logging.error(f"Error in search_and_download: {str(e)}")
            return None

    def verify_download(self, file_path: str) -> bool:
        """Verify that a downloaded file exists and is valid."""
        try:
            return os.path.exists(file_path) and os.path.getsize(file_path) > 0
        except Exception as e:
            logging.error(f"Error verifying download {file_path}: {str(e)}")
            return False 