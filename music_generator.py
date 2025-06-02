from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy.io.wavfile
import numpy as np
import torch
import time

class MusicGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = None
        self.model = None
        self.model_loaded = False
        self.sample_rate = 32000
        
    def load_model(self, model_size="small"):
        """Load the MusicGen model from Hugging Face"""
        try:
            print(f"Loading facebook/musicgen-{model_size}...")
            
            self.processor = AutoProcessor.from_pretrained(f"facebook/musicgen-{model_size}")
            self.model = MusicgenForConditionalGeneration.from_pretrained(f"facebook/musicgen-{model_size}")
            
            if self.device == "cuda":
                self.model = self.model.to(self.device)
            
            self.model_loaded = True
            print("Model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def generate_music(self, prompt, duration=30, temperature=1.0, top_k=250):
        """Generate music from text prompt"""
        
        if not self.model_loaded:
            if not self.load_model():
                return None, "Failed to load model"
        
        try:
            start_time = time.time()
            
            # Calculate tokens for duration (roughly 50 tokens per second)
            num_tokens = int(duration * 50)
            
            # Process the prompt
            inputs = self.processor(
                text=[prompt],
                padding=True,
                return_tensors="pt"
            )
            
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate audio with parameters
            audio_values = self.model.generate(
                **inputs, 
                max_new_tokens=num_tokens,
                temperature=temperature,
                top_k=top_k,
                do_sample=True
            )
            
            # Convert to numpy array
            audio_array = audio_values[0, 0].cpu().numpy()
            
            generation_time = time.time() - start_time
            
            return audio_array, f"Generated in {generation_time:.2f} seconds"
            
        except Exception as e:
            return None, f"Error generating music: {str(e)}"
    
    def generate_with_style(self, prompt, style="general", duration=30, temperature=1.0, top_k=250):
        """Generate music with specific style enhancement"""
        
        style_prompts = {
            "jazz": f"{prompt}, jazz style, smooth, sophisticated, piano, saxophone",
            "classical": f"{prompt}, classical music, orchestral, elegant, symphonic",
            "electronic": f"{prompt}, electronic music, synthesizer, beats, modern",
            "rock": f"{prompt}, rock music, guitar, drums, energetic",
            "ambient": f"{prompt}, ambient music, atmospheric, peaceful, ethereal",
            "pop": f"{prompt}, pop music, catchy, melodic, upbeat",
            "blues": f"{prompt}, blues music, soulful, guitar, emotional",
            "folk": f"{prompt}, folk music, acoustic, traditional, storytelling"
        }
        
        enhanced_prompt = style_prompts.get(style, prompt)
        return self.generate_music(enhanced_prompt, duration, temperature, top_k)
    
    def generate_multiple(self, prompt, num_images=4, **kwargs):
        """Generate multiple variations of the same prompt"""
        results = []
        for i in range(num_images):
            audio, message = self.generate_music(prompt, **kwargs)
            if audio is not None:
                results.append(audio)
        return results
    
    def get_available_models(self):
        """Get list of available MusicGen models"""
        return ["small", "medium", "large"]
    
    def get_music_styles(self):
        """Get available music styles"""
        return ["general", "jazz", "classical", "electronic", "rock", "ambient", "pop", "blues", "folk"]
