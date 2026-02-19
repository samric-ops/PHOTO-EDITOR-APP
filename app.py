import streamlit as st
from PIL import Image, ImageDraw
import io

# Must be the first Streamlit command
st.set_page_config(
    page_title="ID Photo Editor",
    page_icon="📸",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-box {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1 style="color: #667eea; margin:0;">📸 ID Photo Editor Pro</h1>
    <p style="color: #666;">Create professional ID photos in seconds</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed' not in st.session_state:
    st.session_state.processed = None

# Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Photo")
    
    uploaded_file = st.file_uploader(
        "Choose a photo (JPG, PNG)",
        type=['jpg', 'jpeg', 'png'],
        key='uploader'
    )
    
    if uploaded_file:
        # Load image
        image = Image.open(uploaded_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Display original
        st.markdown("#### Original")
        st.image(image, use_column_width=True)
        
        # Save to session
        st.session_state.original = image
        
        # Edit options
        st.markdown("---")
        st.markdown("### 🎨 Edit Options")
        
        bg_color = st.color_picker("Background Color", "#FFFFFF")
        
        size_map = {
            "Passport (2x2)": (600, 600),
            "1x1": (300, 300),
            "2x2": (600, 600),
            "PDS": (450, 450)
        }
        selected_size = st.selectbox("Photo Size", list(size_map.keys()))
        
        add_name = st.checkbox("Add Name")
        if add_name:
            name = st.text_input("Full Name")
        
        # Process button
        if st.button("✨ PROCESS PHOTO", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                # Create copy
                processed = image.copy()
                
                # Resize
                target_size = size_map[selected_size]
                processed = processed.resize(target_size, Image.Resampling.LANCZOS)
                
                # Add background color effect
                if bg_color != "#FFFFFF":
                    # Create colored overlay
                    overlay = Image.new('RGB', processed.size, bg_color)
                    # Blend
                    processed = Image.blend(overlay, processed, 0.9)
                
                # Add name
                if add_name and name:
                    draw = ImageDraw.Draw(processed)
                    # Simple text
                    w, h = processed.size
                    draw.text((w//2 - 50, h-40), name, fill='black')
                
                st.session_state.processed = processed
                st.success("✅ Done!")
        
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.processed:
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        st.markdown("### ✨ Processed Photo")
        st.image(st.session_state.processed, use_column_width=True)
        
        # Download
        buf = io.BytesIO()
        st.session_state.processed.save(buf, format='PNG', dpi=(300, 300))
        buf.seek(0)
        
        st.download_button(
            "📥 Download HD Photo",
            data=buf,
            file_name="id_photo.png",
            mime="image/png",
            use_container_width=True
        )
        
        st.info("✅ HD Quality - 300 DPI")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h3>✨ Your edited photo will appear here</h3>
            <p>Upload and process a photo to get started</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Features
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: space-around; background: white; padding: 2rem; border-radius: 10px; margin-top: 2rem;">
    <div style="text-align: center;">
        <h3>🎨</h3>
        <p>Background Color</p>
    </div>
    <div style="text-align: center;">
        <h3>📏</h3>
        <p>Standard Sizes</p>
    </div>
    <div style="text-align: center;">
        <h3>📝</h3>
        <p>Add Name</p>
    </div>
    <div style="text-align: center;">
        <h3>💾</h3>
        <p>HD Download</p>
    </div>
</div>
""", unsafe_allow_html=True)
