import os
import json
from datetime import datetime
import shutil

class ExportManager:
    def __init__(self, export_path="generated_music"):
        self.export_path = export_path
        self.metadata_file = os.path.join(export_path, "music_metadata.json")
        self.ensure_export_directory()
        
    def ensure_export_directory(self):
        """Create export directory if it doesn't exist"""
        if not os.path.exists(self.export_path):
            os.makedirs(self.export_path)
    
    def save_music_file(self, audio_array, prompt, metadata=None):
        """Save generated music with metadata"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"music_{timestamp}.wav"
            filepath = os.path.join(self.export_path, filename)
            
            # Save audio file using audio processor
            from audio_processor import AudioProcessor
            processor = AudioProcessor()
            
            if processor.save_audio(audio_array, filepath):
                # Save metadata
                music_metadata = {
                    "filename": filename,
                    "prompt": prompt,
                    "timestamp": timestamp,
                    "filepath": filepath,
                    "file_size": os.path.getsize(filepath)
                }
                
                if metadata:
                    music_metadata.update(metadata)
                
                self.save_metadata(music_metadata)
                return filepath
            else:
                return None
                
        except Exception as e:
            print(f"Error saving music file: {e}")
            return None
    
    def save_metadata(self, music_metadata):
        """Save music metadata to JSON file"""
        try:
            # Load existing metadata
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    all_metadata = json.load(f)
            else:
                all_metadata = []
            
            # Add new metadata
            all_metadata.append(music_metadata)
            
            # Save updated metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(all_metadata, f, indent=2)
                
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def load_music_library(self):
        """Load all generated music with metadata"""
        try:
            if not os.path.exists(self.metadata_file):
                return []
            
            with open(self.metadata_file, 'r') as f:
                metadata_list = json.load(f)
            
            # Filter out files that no longer exist
            valid_metadata = []
            for metadata in metadata_list:
                if os.path.exists(metadata['filepath']):
                    valid_metadata.append(metadata)
            
            return valid_metadata
            
        except Exception as e:
            print(f"Error loading music library: {e}")
            return []
    
    def delete_music_file(self, filepath):
        """Delete music file and its metadata"""
        try:
            # Delete file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Remove from metadata
            all_metadata = self.load_music_library()
            updated_metadata = [m for m in all_metadata if m['filepath'] != filepath]
            
            with open(self.metadata_file, 'w') as f:
                json.dump(updated_metadata, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error deleting music file: {e}")
            return False
    
    def get_recent_music(self, limit=10):
        """Get most recent generated music"""
        all_music = self.load_music_library()
        return sorted(all_music, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def export_playlist(self, selected_files, playlist_name):
        """Export selected files as a playlist"""
        try:
            playlist_dir = os.path.join(self.export_path, f"playlist_{playlist_name}")
            os.makedirs(playlist_dir, exist_ok=True)
            
            for file_metadata in selected_files:
                src = file_metadata['filepath']
                dst = os.path.join(playlist_dir, file_metadata['filename'])
                shutil.copy2(src, dst)
            
            # Create playlist metadata
            playlist_metadata = {
                "name": playlist_name,
                "created": datetime.now().isoformat(),
                "files": selected_files
            }
            
            with open(os.path.join(playlist_dir, "playlist.json"), 'w') as f:
                json.dump(playlist_metadata, f, indent=2)
            
            return playlist_dir
            
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return None
