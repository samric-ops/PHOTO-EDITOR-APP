import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io

st.set_page_config(page_title="ID Photo Editor", page_icon="📸")

st.title("📸 ID Photo Editor")
st.write("Simple ID Photo Editor for Streamlit")

# Sidebar
with st.sidebar:
    st.header("Upload Photo")
    uploaded_file = st.file_uploader("Choose a file", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        st.success("✅ Uploaded!")
        
        st.header("Settings")
        bg_color = st.color_picker("Background Color", "#FFFFFF")
        photo_size = st.selectbox("Size", ["Passport (2x2)", "1x1", "2x2"])
        
        process = st.button("Process Photo", type="primary")

# Main area
if uploaded_file and process:
    try:
        # Open image
        image = Image.open(uploaded_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy
        img_array = np.array(image)
        
        # Simple background change
        if bg_color != "#FFFFFF":
            h, w = img_array.shape[:2]
            # Convert hex to RGB
            bg = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            # Create new background
            new_bg = np.full((h, w, 3), bg, dtype=np.uint8)
            # Blend (80% original, 20% new bg)
            img_array = (img_array * 0.8 + new_bg * 0.2).astype(np.uint8)
        
        # Resize based on selection
        if photo_size == "Passport (2x2)":
            img_array = np.array(Image.fromarray(img_array).resize((600, 600)))
        elif photo_size == "1x1":
            img_array = np.array(Image.fromarray(img_array).resize((300, 300)))
        else:
            img_array = np.array(Image.fromarray(img_array).resize((600, 600)))
        
        # Display
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original")
            st.image(image)
        
        with col2:
            st.subheader("Processed")
            st.image(img_array)
            
            # Download
            result = Image.fromarray(img_array)
            buf = io.BytesIO()
            result.save(buf, format='PNG')
            buf.seek(0)
            
            st.download_button(
                "📥 Download",
                data=buf,
                file_name="edited_photo.png",
                mime="image/png"
            )
            
            st.success("✅ Done!")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

else:
    st.info("👈 Upload a photo to start editing")
    
    # Features
    st.markdown("---")
    st.markdown("### Features:")
    st.markdown("- Change background color")
    st.markdown("- Resize for ID photos")
    st.markdown("- Download HD photos")
