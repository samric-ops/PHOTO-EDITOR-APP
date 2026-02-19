import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import cv2

st.set_page_config(page_title="ID Photo Editor", page_icon="📸", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .title {
        text-align: center;
        color: #1E88E5;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>📸 ID Photo Editor</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📤 Upload Photo")
    uploaded_file = st.file_uploader("Choose a photo", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        st.success("✅ Photo uploaded!")
        
        st.markdown("---")
        st.header("🎨 Edit Options")
        
        # Background color
        bg_color = st.color_picker("Background Color", "#FFFFFF")
        
        # Size selection
        size_options = {
            "Passport (2x2 inch)": (600, 600),
            "1x1 inch": (300, 300),
            "2x2 inch": (600, 600),
            "4x6 inch": (1200, 1800)
        }
        selected_size = st.selectbox("Select Size", list(size_options.keys()))
        
        # Add name
        add_name = st.checkbox("Add Name")
        if add_name:
            name_text = st.text_input("Full Name")
        
        # Process button
        process_btn = st.button("✨ Process Photo", type="primary", use_container_width=True)

# Main content
if uploaded_file:
    # Open image
    image = Image.open(uploaded_file)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original")
        st.image(image, use_column_width=True)
    
    with col2:
        st.subheader("Processed")
        
        if process_btn:
            with st.spinner("Processing..."):
                # Convert to numpy array
                img_array = np.array(image)
                
                # Change background color (simple version)
                if bg_color != "#FFFFFF":
                    # Convert hex to RGB
                    bg = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    # Create colored overlay
                    h, w = img_array.shape[:2]
                    overlay = np.full((h, w, 3), bg, dtype=np.uint8)
                    # Blend
                    img_array = cv2.addWeighted(img_array, 0.8, overlay, 0.2, 0)
                
                # Resize
                target_size = size_options[selected_size]
                img_array = cv2.resize(img_array, target_size, interpolation=cv2.INTER_CUBIC)
                
                # Add name if provided
                if add_name and name_text:
                    img_pil = Image.fromarray(img_array)
                    draw = ImageDraw.Draw(img_pil)
                    try:
                        font = ImageFont.truetype("arial.ttf", 20)
                    except:
                        font = ImageFont.load_default()
                    
                    # Get text size
                    text_bbox = draw.textbbox((0, 0), name_text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    
                    # Position at bottom center
                    x = (img_pil.width - text_width) // 2
                    y = img_pil.height - 40
                    
                    # Draw text with shadow
                    draw.text((x+1, y+1), name_text, font=font, fill='gray')
                    draw.text((x, y), name_text, font=font, fill='black')
                    
                    img_array = np.array(img_pil)
                
                st.session_state['processed'] = img_array
                st.success("✅ Done!")
        
        # Display processed image
        if 'processed' in st.session_state:
            st.image(st.session_state['processed'], use_column_width=True)
            
            # Download button
            result_pil = Image.fromarray(st.session_state['processed'].astype('uint8'))
            buf = io.BytesIO()
            result_pil.save(buf, format='PNG', dpi=(300, 300))
            buf.seek(0)
            
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
    # Welcome message
    st.info("👈 Upload a photo from the sidebar to get started!")
    
    # Features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🎨 Background")
        st.markdown("Change background color")
    with col2:
        st.markdown("### 📏 Sizes")
        st.markdown("Passport, 1x1, 2x2, 4x6")
    with col3:
        st.markdown("### 📝 Text")
        st.markdown("Add name to photo")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Streamlit ID Photo Editor</p>", unsafe_allow_html=True)
