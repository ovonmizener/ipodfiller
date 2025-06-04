import os
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TPOS, APIC
from typing import Dict, Optional
import logging
from PIL import Image
from io import BytesIO

class MetadataHandler:
    def __init__(self):
        """Initialize the metadata handler."""
        pass

    def download_album_art(self, url: str) -> Optional[bytes]:
        """Download album art from URL."""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            logging.error(f"Failed to download album art: {str(e)}")
            return None

    def embed_metadata(self, file_path: str, track_info: Dict) -> bool:
        """Embed metadata into an MP3 file."""
        try:
            if not os.path.exists(file_path):
                logging.error(f"File not found: {file_path}")
                return False

            # Create ID3 tag if it doesn't exist
            try:
                audio = ID3(file_path)
            except:
                audio = ID3()

            # Add basic metadata
            audio['TIT2'] = TIT2(encoding=3, text=track_info['title'])
            audio['TPE1'] = TPE1(encoding=3, text=track_info['artists'][0])
            audio['TALB'] = TALB(encoding=3, text=track_info['album'])
            audio['TRCK'] = TRCK(encoding=3, text=str(track_info['track_number']))
            audio['TPOS'] = TPOS(encoding=3, text=str(track_info['disc_number']))

            # Add album art if available
            if track_info.get('album_art'):
                art_data = self.download_album_art(track_info['album_art'])
                if art_data:
                    try:
                        # Convert image to JPEG if needed
                        image = Image.open(BytesIO(art_data))
                        if image.format != 'JPEG':
                            output = BytesIO()
                            image.convert('RGB').save(output, format='JPEG')
                            art_data = output.getvalue()

                        audio['APIC'] = APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,
                            desc='Cover',
                            data=art_data
                        )
                    except Exception as e:
                        logging.error(f"Failed to process album art: {str(e)}")

            # Save the metadata
            audio.save(file_path)
            return True

        except Exception as e:
            logging.error(f"Failed to embed metadata: {str(e)}")
            return False

    def verify_metadata(self, file_path: str) -> bool:
        """Verify that metadata was properly embedded."""
        try:
            audio = ID3(file_path)
            required_tags = ['TIT2', 'TPE1', 'TALB']
            return all(tag in audio for tag in required_tags)
        except Exception as e:
            logging.error(f"Failed to verify metadata: {str(e)}")
            return False 