import streamlit as st
import torch
import time
import io
from music_generator import MusicGenerator
from audio_processor import AudioProcessor
from music_styles import MusicStyles
from export_manager import ExportManager

# Page configuration
st.set_page_config(
    page_title="AI Music Composer & Producer",
    page_icon="🎵",
    layout="wide"
)

@st.cache_resource
def load_music_generator():
    return MusicGenerator()

@st.cache_resource
def load_audio_processor():
    return AudioProcessor()

@st.cache_resource
def load_music_styles():
    return MusicStyles()

@st.cache_resource
def load_export_manager():
    return ExportManager()

def main():
    st.title("🎵 AI Music Composer & Producer")
    st.markdown("**Create original music from text descriptions using AI-powered generation**")
    
    # Initialize components
    try:
        music_gen = load_music_generator()
        audio_proc = load_audio_processor()
        styles = load_music_styles()
        exporter = load_export_manager()
    except Exception as e:
        st.error(f"❌ Failed to initialize: {e}")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Generation Settings")
        
        # Model selection
        available_models = music_gen.get_available_models()
        selected_model = st.selectbox("AI Model", available_models, index=0)
        
        # Music style selection
        available_styles = styles.get_all_styles()
        selected_style = st.selectbox("Music Style", available_styles, index=0)
        
        # Show style info
        style_info = styles.get_style_info(selected_style)
        if style_info:
            st.info(f"**{style_info['name']}**: {style_info['description']}")
        
        # Duration settings
        duration = st.slider("Duration (seconds)", 10, 120, 30, step=5)
        
        # Advanced settings
        st.subheader("⚙️ Advanced Settings")
        
        temperature = st.slider("Temperature (creativity)", 0.1, 2.0, 1.0, step=0.1,
                               help="Higher = more creative, Lower = more predictable")
        
        top_k = st.slider("Top-k sampling", 50, 500, 250, step=10,
                         help="Controls diversity of generation")
        
        # Audio effects
        st.subheader("🎚️ Audio Effects")
        add_fade = st.checkbox("Add Fade In/Out", value=True)
        volume_adjust = st.slider("Volume", 0.1, 2.0, 1.0, step=0.1)
        
        # Device info
        device = "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
        st.info(f"🖥️ Using: {device}")
        
        if device == "CPU":
            st.warning("⚠️ Using CPU - generation will be slower. Consider using GPU for faster results.")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎵 Compose", "🎧 Library", "🎼 Quick Prompts", "💡 Tips"])
    
    with tab1:
        st.header("✨ Compose Your Music")
        
        # Prompt input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            prompt = st.text_area(
                "Describe the music you want to create:",
                height=100,
                placeholder="A relaxing jazz piano piece with smooth saxophone and soft drums"
            )
        
        with col2:
            st.write("**Style Examples:**")
            mood_suggestions = styles.get_mood_suggestions()
            for mood, description in list(mood_suggestions.items())[:3]:
                if st.button(f"{mood}", key=f"mood_{mood}"):
                    st.session_state.prompt_suggestion = f"A {mood.lower()} piece, {description}"
        
        # Use session state for prompt suggestions
        if 'prompt_suggestion' in st.session_state:
            prompt = st.session_state.prompt_suggestion
            del st.session_state.prompt_suggestion
        
        if prompt:
            # Enhance prompt with style
            enhanced_prompt = styles.get_style_prompt(prompt, selected_style)
            
            with st.expander("🔧 Enhanced Prompt Preview"):
                st.write("**Original Prompt:**")
                st.code(prompt)
                st.write("**Enhanced Prompt:**")
                st.code(enhanced_prompt)
                
                use_enhancement = st.checkbox("Use enhanced prompt", value=True)
        
        # Generation buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            generate_music = st.button("🎶 Generate Music", type="primary")
        
        with col2:
            if st.button("🎲 Random Style"):
                import random
                random_style = random.choice(available_styles)
                st.session_state.random_style = random_style
        
        with col3:
            if st.button("⚡ Quick Generate"):
                st.session_state.quick_generate = True
        
        # Handle random style
        if 'random_style' in st.session_state:
            selected_style = st.session_state.random_style
            del st.session_state.random_style
            st.info(f"🎲 Random style selected: {selected_style}")
        
        # Generation logic
        if prompt and (generate_music or st.session_state.get('quick_generate', False)):
            if 'quick_generate' in st.session_state:
                del st.session_state.quick_generate
            
            # Prepare final prompt
            final_prompt = enhanced_prompt if 'use_enhancement' in locals() and use_enhancement else prompt
            
            # Show generation parameters
            with st.expander("📋 Generation Parameters"):
                st.json({
                    "prompt": final_prompt,
                    "style": selected_style,
                    "duration": duration,
                    "temperature": temperature,
                    "top_k": top_k,
                    "model": selected_model
                })
            
            # Generate music
            with st.spinner("🎼 AI is composing your music..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Loading AI model...")
                progress_bar.progress(0.2)
                
                status_text.text("Generating music...")
                start_time = time.time()
                
                audio_array, message = music_gen.generate_with_style(
                    final_prompt, 
                    selected_style, 
                    duration=duration,
                    temperature=temperature,
                    top_k=top_k
                )
                
                progress_bar.progress(0.8)
                elapsed = time.time() - start_time
                
                if audio_array is not None:
                    status_text.text("Processing audio...")
                    
                    # Apply audio effects
                    if add_fade:
                        audio_array = audio_proc.add_fade_effects(audio_array)
                    
                    if volume_adjust != 1.0:
                        audio_array = audio_proc.adjust_volume(audio_array, volume_adjust)
                    
                    progress_bar.progress(1.0)
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success(f"🎉 Music generated in {elapsed:.2f} seconds!")
                    
                    # Display audio player
                    audio_buffer = audio_proc.create_audio_buffer(audio_array)
                    st.audio(audio_buffer, format='audio/wav')
                    
                    # Audio information
                    audio_info = audio_proc.get_audio_info(audio_array)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Duration", f"{audio_info['duration']}s")
                    with col2:
                        st.metric("Sample Rate", f"{audio_info['sample_rate']} Hz")
                    with col3:
                        st.metric("Quality", f"{audio_info['max_amplitude']:.2f}")
                    
                    # Save music file
                    metadata = {
                        "style": selected_style,
                        "duration": duration,
                        "temperature": temperature,
                        "top_k": top_k,
                        "model": selected_model,
                        "generation_time": elapsed
                    }
                    
                    saved_path = exporter.save_music_file(audio_array, final_prompt, metadata)
                    
                    if saved_path:
                        st.success("💾 Music saved to library!")
                    
                    # Download options
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download WAV",
                            data=audio_buffer.getvalue(),
                            file_name=f"ai_music_{int(time.time())}.wav",
                            mime="audio/wav"
                        )
                    
                    with col2:
                        # Convert to MP3 for smaller download
                        try:
                            import tempfile
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                                audio_proc.save_audio(audio_array, tmp_wav.name)
                                
                                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
                                    if audio_proc.convert_to_mp3(tmp_wav.name, tmp_mp3.name):
                                        with open(tmp_mp3.name, 'rb') as f:
                                            mp3_data = f.read()
                                        
                                        st.download_button(
                                            label="📥 Download MP3",
                                            data=mp3_data,
                                            file_name=f"ai_music_{int(time.time())}.mp3",
                                            mime="audio/mp3"
                                        )
                        except Exception as e:
                            st.warning("MP3 conversion not available")
                
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ Failed to generate music: {message}")
    
    with tab2:
        st.header("🎧 Your Music Library")
        
        music_files = exporter.get_recent_music(20)
        
        if music_files:
            st.write(f"📂 Total tracks: {len(music_files)}")
            
            # Library controls
            col1, col2, col3 = st.columns(3)
            with col1:
                sort_by = st.selectbox("Sort by", ["Recent", "Style", "Duration"])
            with col2:
                filter_style = st.selectbox("Filter by style", ["All"] + available_styles)
            with col3:
                if st.button("🗑️ Clear Library"):
                    if st.checkbox("Confirm deletion"):
                        # Clear library logic here
                        st.warning("Library cleared!")
            
            # Filter music files
            filtered_files = music_files
            if filter_style != "All":
                filtered_files = [m for m in music_files if m.get('style') == filter_style]
            
            # Display music library
            for i, music in enumerate(filtered_files):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        try:
                            st.audio(music['filepath'])
                            
                            # Music details
                            st.write(f"**🎵 Prompt:** {music['prompt'][:100]}...")
                            
                            details_col1, details_col2, details_col3 = st.columns(3)
                            with details_col1:
                                st.write(f"**Style:** {music.get('style', 'N/A')}")
                            with details_col2:
                                st.write(f"**Duration:** {music.get('duration', 'N/A')}s")
                            with details_col3:
                                st.write(f"**Created:** {music['timestamp']}")
                        
                        except Exception as e:
                            st.error(f"Error loading track: {e}")
                    
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                            if exporter.delete_music_file(music['filepath']):
                                st.success("Track deleted!")
                                st.experimental_rerun()
                        
                        if st.button(f"📋 Details", key=f"details_{i}"):
                            st.session_state[f"show_details_{i}"] = True
                    
                    # Show detailed metadata if requested
                    if st.session_state.get(f"show_details_{i}", False):
                        with st.expander("📋 Full Details", expanded=True):
                            st.json(music)
                            if st.button("Close", key=f"close_{i}"):
                                st.session_state[f"show_details_{i}"] = False
                    
                    st.divider()
        
        else:
            st.info("🎵 No music tracks yet! Compose your first piece in the Compose tab.")
            
            # Quick start suggestions
            st.subheader("🚀 Quick Start")
            quick_prompts = [
                "A peaceful ambient soundscape",
                "Upbeat electronic dance music",
                "Classical piano melody"
            ]
            
            for prompt in quick_prompts:
                if st.button(f"Generate: {prompt}", key=f"quick_{prompt}"):
                    st.session_state.prompt_suggestion = prompt
                    st.switch_page("Compose")
    
    with tab3:
        st.header("🎼 Quick Prompt Generator")
        
        st.markdown("**Generate music prompts quickly by selecting options:**")
        
        # Quick prompt builder
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🎭 Mood")
            moods = list(styles.get_mood_suggestions().keys())
            selected_mood = st.selectbox("Choose mood", moods)
        
        with col2:
            st.subheader("🎸 Instruments")
            instruments = list(styles.get_instrument_suggestions().keys())
            selected_instrument = st.selectbox("Choose instrument", instruments)
        
        with col3:
            st.subheader("🎵 Genre")
            selected_genre = st.selectbox("Choose genre", available_styles)
        
        # Generate prompt
        if st.button("🎯 Generate Prompt"):
            mood_desc = styles.get_mood_suggestions()[selected_mood]
            instrument_desc = styles.get_instrument_suggestions()[selected_instrument]
            
            generated_prompt = f"A {selected_mood.lower()} {selected_genre} piece with {selected_instrument.lower()}, {mood_desc}, {instrument_desc}"
            
            st.success("Generated Prompt:")
            st.code(generated_prompt)
            
            if st.button("🎶 Use This Prompt"):
                st.session_state.prompt_suggestion = generated_prompt
                # Switch to compose tab
                st.info("Prompt saved! Go to the Compose tab to generate music.")
        
        # Prompt examples by category
        st.subheader("💡 Prompt Examples")
        
        prompt_categories = {
            "🎹 Classical": [
                "A romantic piano sonata in the style of Chopin",
                "Orchestral symphony with strings and brass",
                "Baroque harpsichord piece with intricate melodies"
            ],
            "🎸 Rock": [
                "Heavy metal guitar riffs with powerful drums",
                "Classic rock anthem with electric guitar solos",
                "Alternative rock with emotional vocals"
            ],
            "🎧 Electronic": [
                "Ambient techno with synthesized atmospheres",
                "High-energy EDM with bass drops",
                "Chillwave with retro synthesizers"
            ],
            "🎺 Jazz": [
                "Smooth jazz with saxophone and piano",
                "Bebop with fast-paced improvisation",
                "Jazz fusion with electric instruments"
            ]
        }
        
        for category, prompts in prompt_categories.items():
            with st.expander(category):
                for prompt in prompts:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"• {prompt}")
                    with col2:
                        if st.button("Use", key=f"use_{prompt[:20]}"):
                            st.session_state.prompt_suggestion = prompt
                            st.success("Prompt copied!")
    
    with tab4:
        st.header("💡 Tips for Better Music Generation")
        
        st.markdown("""
        ### 🎯 Writing Effective Music Prompts
        
        **Good prompts include:**
        - **Genre and style**: jazz, classical, electronic, rock, ambient
        - **Instruments**: piano, guitar, drums, synthesizer, violin
        - **Mood and tempo**: relaxing, energetic, slow, fast, melancholic
        - **Descriptors**: smooth, melodic, catchy, atmospheric, powerful
        
        **Example transformations:**
        - ❌ "Make music"
        - ✅ "A relaxing jazz piano piece with smooth saxophone and soft drums"
        
        ### 🎵 Understanding Generation Settings
        
        **Duration:**
        - 10-30 seconds: Quick samples and loops
        - 30-60 seconds: Short compositions
        - 60+ seconds: Full musical pieces
        
        **Temperature (Creativity):**
        - 0.1-0.5: Conservative, predictable
        - 0.5-1.0: Balanced creativity
        - 1.0-2.0: Highly creative, experimental
        
        **Top-k Sampling:**
        - 50-150: More focused, coherent
        - 150-300: Balanced diversity
        - 300-500: Maximum variety
        
        ### 🎼 Music Theory Tips
        
        **Rhythm and Tempo:**
        - "Slow ballad", "Medium swing", "Fast-paced"
        - "4/4 time", "Waltz rhythm", "Syncopated"
        
        **Harmony and Melody:**
        - "Major key", "Minor key", "Pentatonic scale"
        - "Ascending melody", "Repetitive motif"
        
        **Dynamics:**
        - "Soft and gentle", "Building intensity"
        - "Dramatic crescendo", "Quiet verses, loud chorus"
        
        ### 🚀 Pro Tips
        
        1. **Start simple** - Begin with basic prompts and add complexity
        2. **Experiment with combinations** - Mix different styles and moods
        3. **Use specific instruments** - More specific = better results
        4. **Describe the feeling** - Emotions guide the AI effectively
        5. **Reference musical eras** - "80s synth", "90s grunge", "Baroque"
        6. **Add context** - "Background music for...", "Theme for..."
        
        ### 🎨 Creative Techniques
        
        **Layering Concepts:**
        - "Acoustic guitar with electronic beats"
        - "Classical orchestra meets modern hip-hop"
        
        **Emotional Storytelling:**
        - "Music that tells the story of..."
        - "Soundtrack for a peaceful morning"
        
        **Cultural Fusion:**
        - "Japanese traditional meets electronic"
        - "Latin rhythms with jazz harmonies"
        
        ### ⚡ Performance Optimization
        
        **For Faster Generation:**
        - Use "small" model for quick tests
        - Generate shorter durations first
        - Lower temperature for faster processing
        
        **For Better Quality:**
        - Use "medium" or "large" models
        - Higher top-k values for more variety
        - Longer durations for complete compositions
        """)
        
        # Hardware recommendations
        st.subheader("🖥️ Hardware Recommendations")
        
        hardware_info = f"""
        **Current Setup:** {device}
        
        **Recommended for Music Generation:**
        - **GPU**: NVIDIA RTX 3060 or better (6GB+ VRAM)
        - **RAM**: 16GB+ for smooth operation
        - **Storage**: SSD for faster model loading
        
        **Generation Times:**
        - **CPU**: 2-5 minutes per 30-second track
        - **GPU (6GB)**: 30-60 seconds per 30-second track
        - **GPU (12GB+)**: 15-30 seconds per 30-second track
        """
        
        st.info(hardware_info)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    🎵 **Powered by MusicGen AI** | 🎼 **AudioCraft Framework** | 🚀 **Built with Streamlit**
    
    💡 **Tip**: Experiment with different styles and prompts to discover your unique AI music style!
    """)

if __name__ == "__main__":
    main()
