import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict, Optional
import logging

class SpotifyHandler:
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the Spotify handler with API credentials."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.sp = None
        if client_id and client_secret:
            self._setup_spotify_client()
        
    def is_configured(self) -> bool:
        """Check if the handler is properly configured with credentials."""
        return self.sp is not None

    def configure(self, client_id: str, client_secret: str) -> bool:
        """Configure the handler with new credentials."""
        try:
            self.client_id = client_id
            self.client_secret = client_secret
            self._setup_spotify_client()
            return True
        except Exception as e:
            logging.error(f"Failed to configure Spotify client: {str(e)}")
            return False
        
    def _setup_spotify_client(self) -> None:
        """Set up the Spotify client with credentials."""
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except Exception as e:
            logging.error(f"Failed to initialize Spotify client: {str(e)}")
            raise

    def extract_playlist_id(self, playlist_url: str) -> Optional[str]:
        """Extract the playlist ID from a Spotify playlist URL."""
        try:
            # Handle different URL formats
            patterns = [
                r'spotify:playlist:([a-zA-Z0-9]+)',
                r'open\.spotify\.com/playlist/([a-zA-Z0-9]+)',
                r'playlist/([a-zA-Z0-9]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, playlist_url)
                if match:
                    return match.group(1)
            return None
        except Exception as e:
            logging.error(f"Failed to extract playlist ID: {str(e)}")
            return None

    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Retrieve all tracks from a playlist with their metadata."""
        try:
            tracks = []
            results = self.sp.playlist_tracks(playlist_id)
            
            while results:
                for item in results['items']:
                    track = item['track']
                    if track is None:
                        continue
                        
                    track_info = {
                        'title': track['name'],
                        'artists': [artist['name'] for artist in track['artists']],
                        'album': track['album']['name'],
                        'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
                        'duration_ms': track['duration_ms'],
                        'track_number': track['track_number'],
                        'disc_number': track['disc_number']
                    }
                    tracks.append(track_info)
                
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break
                    
            return tracks
        except Exception as e:
            logging.error(f"Failed to get playlist tracks: {str(e)}")
            raise

    def get_playlist_name(self, playlist_id: str) -> Optional[str]:
        """Get the name of a playlist."""
        try:
            playlist = self.sp.playlist(playlist_id)
            return playlist['name']
        except Exception as e:
            logging.error(f"Failed to get playlist name: {str(e)}")
            return None 