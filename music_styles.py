class MusicStyles:
    def __init__(self):
        self.style_configs = {
            "jazz": {
                "name": "Jazz",
                "description": "Smooth, sophisticated, improvisational",
                "keywords": ["jazz", "swing", "blues", "piano", "saxophone", "smooth"],
                "tempo": "medium",
                "mood": "sophisticated"
            },
            "classical": {
                "name": "Classical",
                "description": "Orchestral, elegant, timeless",
                "keywords": ["classical", "orchestral", "symphony", "piano", "violin", "elegant"],
                "tempo": "varied",
                "mood": "elegant"
            },
            "electronic": {
                "name": "Electronic",
                "description": "Synthesized, modern, digital",
                "keywords": ["electronic", "synth", "digital", "beats", "modern", "futuristic"],
                "tempo": "fast",
                "mood": "energetic"
            },
            "rock": {
                "name": "Rock",
                "description": "Guitar-driven, energetic, powerful",
                "keywords": ["rock", "guitar", "drums", "electric", "powerful", "energetic"],
                "tempo": "fast",
                "mood": "energetic"
            },
            "ambient": {
                "name": "Ambient",
                "description": "Atmospheric, peaceful, meditative",
                "keywords": ["ambient", "atmospheric", "peaceful", "ethereal", "calm", "meditative"],
                "tempo": "slow",
                "mood": "peaceful"
            },
            "pop": {
                "name": "Pop",
                "description": "Catchy, melodic, mainstream",
                "keywords": ["pop", "catchy", "melodic", "upbeat", "mainstream", "radio-friendly"],
                "tempo": "medium-fast",
                "mood": "upbeat"
            }
        }
    
    def get_style_prompt(self, base_prompt, style):
        """Enhance prompt with style-specific keywords"""
        if style not in self.style_configs:
            return base_prompt
        
        config = self.style_configs[style]
        keywords = ", ".join(config["keywords"][:3])  # Use first 3 keywords
        
        return f"{base_prompt}, {keywords}, {config['mood']}"
    
    def get_all_styles(self):
        """Get all available styles"""
        return list(self.style_configs.keys())
    
    def get_style_info(self, style):
        """Get detailed information about a style"""
        return self.style_configs.get(style, {})
    
    def get_mood_suggestions(self):
        """Get mood-based prompt suggestions"""
        return {
            "Happy": "upbeat, joyful, cheerful, bright, positive",
            "Sad": "melancholic, emotional, slow, minor key, touching",
            "Energetic": "fast, powerful, driving, intense, dynamic",
            "Calm": "peaceful, relaxing, gentle, soft, soothing",
            "Mysterious": "dark, enigmatic, suspenseful, atmospheric",
            "Romantic": "tender, passionate, intimate, warm, loving"
        }
    
    def get_instrument_suggestions(self):
        """Get instrument-based prompt suggestions"""
        return {
            "Piano": "piano solo, keys, melodic, expressive",
            "Guitar": "guitar, strings, acoustic or electric",
            "Orchestra": "orchestral, symphony, full ensemble",
            "Electronic": "synthesizer, electronic beats, digital",
            "Drums": "percussion, rhythmic, beats, dynamic"
        }
