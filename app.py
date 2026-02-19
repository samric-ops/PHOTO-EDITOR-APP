import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(
    page_title="ID Photo Editor",
    page_icon="📸",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1E88E5;
        font-size: 3rem;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📸 ID Photo Editor</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1E88E5/ffffff?text=ID+Photo+Editor", use_column_width=True)
    st.markdown("---")
    
    st.markdown("### 📤 Upload Photo")
    uploaded_file = st.file_uploader(
        "Choose a photo (JPG/PNG)",
        type=['jpg', 'jpeg', 'png']
    )
    
    if uploaded_file:
        st.success("✅ Photo uploaded!")
        st.markdown("---")
        
        st.markdown("### 🎨 Edit Options")
        
        # Background color
        bg_color = st.color_picker("Background Color", "#FFFFFF")
        
        # Size selection
        size_options = {
            "Passport (2x2 inch)": (600, 600),
            "1x1 inch": (300, 300),
            "2x2 inch": (600, 600),
            "PDS (Personal Data Sheet)": (450, 450)
        }
        selected_size = st.selectbox("Photo Size", list(size_options.keys()))
        
        # Add name
        add_name = st.checkbox("Add Name")
        if add_name:
            name_text = st.text_input("Full Name")
            name_color = st.color_picker("Name Color", "#000000")
        
        # Process button
        process_btn = st.button(
            "✨ PROCESS PHOTO",
            type="primary",
            use_container_width=True
        )

# Main content
if uploaded_file:
    # Open image
    original_image = Image.open(uploaded_file)
    
    # Convert to RGB if necessary
    if original_image.mode != 'RGB':
        original_image = original_image.convert('RGB')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📷 Original")
        st.image(original_image, use_column_width=True)
        st.caption(f"Size: {original_image.size[0]} x {original_image.size[1]}")
    
    with col2:
        st.markdown("### ✨ Processed")
        
        if process_btn:
            with st.spinner("🔄 Processing..."):
                # Create a copy
                processed = original_image.copy()
                
                # Resize first
                target_size = size_options[selected_size]
                processed = processed.resize(target_size, Image.Resampling.LANCZOS)
                
                # Create a new image with background color
                if bg_color != "#FFFFFF":
                    # Create colored background
                    colored_bg = Image.new('RGB', processed.size, bg_color)
                    
                    # Paste processed image on colored background
                    # For now, just blend by creating a new image
                    # This is a simple effect without actual background removal
                    processed = Image.blend(colored_bg, processed, 0.9)
                
                # Add name if provided
                if add_name and name_text:
                    draw = ImageDraw.Draw(processed)
                    
                    # Try to use a font
                    try:
                        font = ImageFont.truetype("arial.ttf", 20)
                    except:
                        font = ImageFont.load_default()
                    
                    # Get text size
                    text_bbox = draw.textbbox((0, 0), name_text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    
                    # Position at bottom
                    x = (processed.width - text_width) // 2
                    y = processed.height - 40
                    
                    # Draw text
                    draw.text((x, y), name_text, font=font, fill=name_color)
                
                # Save to session state
                st.session_state['processed'] = processed
                st.success("✅ Done!")
        
        # Display processed image
        if 'processed' in st.session_state:
            st.image(st.session_state['processed'], use_column_width=True)
            st.caption(f"Size: {st.session_state['processed'].size[0]} x {st.session_state['processed'].size[1]}")
            
            # Download button
            buf = io.BytesIO()
            st.session_state['processed'].save(buf, format='PNG', dpi=(300, 300))
            buf.seek(0)
            
            st.markdown("---")
            st.download_button(
                "📥 Download HD Photo",
                data=buf,
                file_name="id_photo.png",
                mime="image/png",
                use_container_width=True
            )
            
            st.markdown("""
            <div class='success-box'>
                ✅ HD Quality (300 DPI) - Ready for printing
            </div>
            """, unsafe_allow_html=True)

else:
    # Welcome screen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-box'>
            <h3>🎨 Background</h3>
            <p>Change background color easily</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-box'>
            <h3>📏 Standard Sizes</h3>
            <p>Passport, 1x1, 2x2, PDS</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-box'>
            <h3>📝 Add Name</h3>
            <p>Perfect for official documents</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("👆 Upload a photo from the sidebar to get started!")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Made with ❤️ using Streamlit</p>",
    unsafe_allow_html=True
)
