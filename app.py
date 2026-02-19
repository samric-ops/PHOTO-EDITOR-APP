import streamlit as st
from PIL import Image
import numpy as np
import cv2
import io

st.set_page_config(page_title="ID Photo Editor", page_icon="📸", layout="wide")

# Title
st.markdown("""
<h1 style='text-align: center; color: #1E88E5;'>
    📸 ID Photo Editor Pro
</h1>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed' not in st.session_state:
    st.session_state.processed = None

# Sidebar
with st.sidebar:
    st.header("📤 Upload")
    uploaded_file = st.file_uploader("Choose photo", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        st.success("✅ Uploaded!")
        
        st.header("🎨 Settings")
        
        # Background
        bg_option = st.checkbox("Change Background", value=True)
        if bg_option:
            bg_color = st.color_picker("Pick color", "#FFFFFF")
        
        # Size
        size_option = st.selectbox(
            "Photo Size",
            ["Passport (2x2)", "1x1", "2x2", "Wallet"]
        )
        
        # Process button
        if st.button("✨ PROCESS", type="primary", use_container_width=True):
            st.session_state.processed = True

# Main content
if uploaded_file:
    # Load image
    image = Image.open(uploaded_file)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📷 Original")
        st.image(image, use_column_width=True)
        st.caption(f"Size: {image.size[0]} x {image.size[1]}")
    
    with col2:
        st.subheader("✨ Result")
        
        if st.session_state.processed:
            with st.spinner("Processing..."):
                # Convert to numpy
                img_array = np.array(image)
                h, w = img_array.shape[:2]
                
                # Change background
                if bg_option:
                    # Convert hex to RGB
                    bg = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    # Create solid background
                    background = np.full((h, w, 3), bg, dtype=np.uint8)
                    # Blend (simple version)
                    img_array = cv2.addWeighted(img_array, 0.9, background, 0.1, 0)
                
                # Resize based on selection
                if size_option == "Passport (2x2)":
                    new_size = (600, 600)
                elif size_option == "1x1":
                    new_size = (300, 300)
                elif size_option == "2x2":
                    new_size = (600, 600)
                else:  # Wallet
                    new_size = (750, 1050)
                
                img_array = cv2.resize(img_array, new_size, interpolation=cv2.INTER_CUBIC)
                
                # Convert back to PIL
                result = Image.fromarray(img_array)
                st.session_state.result_img = result
                
                st.success("✅ Done!")
        
        # Display result
        if 'result_img' in st.session_state:
            st.image(st.session_state.result_img, use_column_width=True)
            st.caption(f"Size: {st.session_state.result_img.size[0]} x {st.session_state.result_img.size[1]}")
            
            # Download
            buf = io.BytesIO()
            st.session_state.result_img.save(buf, format='PNG', dpi=(300, 300))
            buf.seek(0)
            
            st.download_button(
                "📥 Download HD Photo",
                data=buf,
                file_name="id_photo.png",
                mime="image/png",
                use_container_width=True
            )
else:
    # Welcome
    st.info("👆 Upload a photo to start editing")
    
    # Features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🎨 Background")
        st.write("Change background color")
    with col2:
        st.markdown("### 📏 Sizes")
        st.write("Passport, 1x1, 2x2, Wallet")
    with col3:
        st.markdown("### 💾 HD Output")
        st.write("300 DPI print ready")
