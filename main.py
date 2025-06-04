import os
import sys
import logging
from typing import Optional
from spotify_handler import SpotifyHandler
from youtube_handler import YouTubeHandler
from metadata_handler import MetadataHandler
from gui import SpotifyDownloaderGUI
import json

class SpotifyDownloader:
    def __init__(self):
        """Initialize the Spotify downloader application."""
        self.setup_logging()
        self.setup_handlers()
        self.setup_gui()

    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_handlers(self):
        """Set up all necessary handlers."""
        # Try to load credentials from config file first
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    client_id = config.get('client_id')
                    client_secret = config.get('client_secret')
            except Exception as e:
                logging.error(f"Error loading config file: {str(e)}")
                client_id = None
                client_secret = None
        else:
            client_id = None
            client_secret = None

        # If no config file, try environment variables
        if not client_id:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
        if not client_secret:
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

        # If still no credentials, use None (will be handled by GUI)
        self.spotify = SpotifyHandler(
            client_id=client_id,
            client_secret=client_secret
        )
        self.metadata = MetadataHandler()

    def setup_gui(self):
        """Set up the GUI and connect it to the download process."""
        self.gui = SpotifyDownloaderGUI()
        self.gui.download_process = self.download_process
        self.gui.set_spotify_handler(self.spotify)

    def download_process(self, url: str, directory: str):
        """Main download process."""
        try:
            # Check if we have valid credentials
            if not self.spotify.is_configured():
                self.gui.queue.put("Error: Spotify credentials not configured")
                self.gui.queue.put("ERROR")
                return

            # Extract playlist ID
            playlist_id = self.spotify.extract_playlist_id(url)
            if not playlist_id:
                self.gui.queue.put("Error: Invalid Spotify playlist URL")
                self.gui.queue.put("ERROR")
                return

            # Get playlist name
            playlist_name = self.spotify.get_playlist_name(playlist_id)
            if not playlist_name:
                self.gui.queue.put("Error: Could not retrieve playlist information")
                self.gui.queue.put("ERROR")
                return

            self.gui.queue.put(f"Processing playlist: {playlist_name}")

            # Get all tracks
            tracks = self.spotify.get_playlist_tracks(playlist_id)
            if not tracks:
                self.gui.queue.put("Error: No tracks found in playlist")
                self.gui.queue.put("ERROR")
                return

            self.gui.queue.put(f"Found {len(tracks)} tracks")

            # Create playlist directory
            playlist_dir = os.path.join(directory, playlist_name)
            os.makedirs(playlist_dir, exist_ok=True)

            # Initialize YouTube handler
            youtube = YouTubeHandler(playlist_dir)

            # Download each track
            for i, track in enumerate(tracks, 1):
                if self.gui.is_cancelled():
                    self.gui.queue.put("Download cancelled by user.")
                    self.gui.queue.put("DONE")
                    return
                try:
                    self.gui.queue.put(f"\nProcessing track {i}/{len(tracks)}: {track['title']}")

                    # Download track
                    file_path = youtube.search_and_download(track)
                    if not file_path:
                        self.gui.queue.put(f"Failed to download: {track['title']}")
                        continue

                    # Verify download
                    if not youtube.verify_download(file_path):
                        self.gui.queue.put(f"Download verification failed: {track['title']}")
                        continue

                    # Embed metadata
                    if not self.metadata.embed_metadata(file_path, track):
                        self.gui.queue.put(f"Failed to embed metadata: {track['title']}")
                        continue

                    # Verify metadata
                    if not self.metadata.verify_metadata(file_path):
                        self.gui.queue.put(f"Metadata verification failed: {track['title']}")
                        continue

                    self.gui.queue.put(f"Successfully processed: {track['title']}")

                except Exception as e:
                    logging.error(f"Error processing track {track['title']}: {str(e)}")
                    self.gui.queue.put(f"Error processing track: {track['title']}")

                # Update progress
                progress = i / len(tracks)
                self.gui.queue.put(progress)

            self.gui.queue.put("\nDownload completed!")
            self.gui.queue.put("DONE")

        except Exception as e:
            logging.error(f"Download process error: {str(e)}")
            self.gui.queue.put(f"Error: {str(e)}")
            self.gui.queue.put("ERROR")

    def run(self):
        """Start the application."""
        self.gui.run()

def main():
    try:
        app = SpotifyDownloader()
        app.run()
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 