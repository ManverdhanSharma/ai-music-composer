import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
import io
import os

class AudioProcessor:
    def __init__(self):
        self.sample_rate = 32000
        
    def save_audio(self, audio_array, filename, sample_rate=None):
        """Save audio array to file"""
        if sample_rate is None:
            sample_rate = self.sample_rate
            
        try:
            # Ensure audio is in correct format
            if audio_array.ndim > 1:
                audio_array = audio_array[0]  # Take first channel if stereo
            
            # Normalize audio
            audio_array = audio_array / np.max(np.abs(audio_array))
            
            # Save as WAV file
            sf.write(filename, audio_array, sample_rate)
            return True
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
    
    def convert_to_mp3(self, wav_file, mp3_file):
        """Convert WAV to MP3"""
        try:
            audio = AudioSegment.from_wav(wav_file)
            audio.export(mp3_file, format="mp3")
            return True
        except Exception as e:
            print(f"Error converting to MP3: {e}")
            return False
    
    def add_fade_effects(self, audio_array, fade_in_duration=1.0, fade_out_duration=2.0):
        """Add fade in and fade out effects"""
        try:
            fade_in_samples = int(fade_in_duration * self.sample_rate)
            fade_out_samples = int(fade_out_duration * self.sample_rate)
            
            # Create fade curves
            fade_in = np.linspace(0, 1, fade_in_samples)
            fade_out = np.linspace(1, 0, fade_out_samples)
            
            # Apply fade in
            if len(audio_array) > fade_in_samples:
                audio_array[:fade_in_samples] *= fade_in
            
            # Apply fade out
            if len(audio_array) > fade_out_samples:
                audio_array[-fade_out_samples:] *= fade_out
            
            return audio_array
            
        except Exception as e:
            print(f"Error adding fade effects: {e}")
            return audio_array
    
    def adjust_volume(self, audio_array, volume_factor=1.0):
        """Adjust audio volume"""
        return audio_array * volume_factor
    
    def get_audio_info(self, audio_array):
        """Get information about audio"""
        duration = len(audio_array) / self.sample_rate
        max_amplitude = np.max(np.abs(audio_array))
        
        return {
            "duration": round(duration, 2),
            "sample_rate": self.sample_rate,
            "max_amplitude": round(max_amplitude, 3),
            "samples": len(audio_array)
        }
    
    def create_audio_buffer(self, audio_array):
        """Create audio buffer for download"""
        buffer = io.BytesIO()
        sf.write(buffer, audio_array, self.sample_rate, format='WAV')
        buffer.seek(0)
        return buffer
