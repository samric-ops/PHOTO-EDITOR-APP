import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import io
import time
import base64
from rembg import remove

# Page config
st.set_page_config(
    page_title="ID Photo Editor Pro",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .main-title h1 {
        font-size: 3rem;
        margin: 0;
        font-weight: bold;
    }
    .main-title p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Card styling */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Feature box */
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e0e0e0;
        transition: transform 0.3s;
    }
    .feature-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    /* Success message */
    .success-msg {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #f8f9fa;
    }
    
    /* Image containers */
    .image-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        background: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
if 'original_image' not in st.session_state:
    st.session_state.original_image = None

# Main title
st.markdown("""
<div class="main-title">
    <h1>📸 ID Photo Editor Pro</h1>
    <p>Create professional ID photos in seconds - Passport, 2x2, PDS, and more!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 📤 **Upload Photo**")
    
    uploaded_file = st.file_uploader(
        "Choose a photo (JPG, PNG, JPEG)",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a clear photo with good lighting"
    )
    
    if uploaded_file:
        st.success("✅ Photo uploaded successfully!")
        
        # Display file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.json(file_details)
        
        st.markdown("---")
        st.markdown("## 🎨 **Edit Options**")
        
        # 1. Background removal
        with st.expander("🎨 Background", expanded=True):
            remove_bg = st.checkbox("Remove Background", value=True)
            if remove_bg:
                bg_option = st.radio(
                    "Background Type",
                    ["Solid Color", "Transparent"],
                    horizontal=True
                )
                if bg_option == "Solid Color":
                    bg_color = st.color_picker("Choose Color", "#FFFFFF")
        
        # 2. Face enhancement
        with st.expander("👤 Face Enhancement", expanded=True):
            enhance_face = st.checkbox("Enhance Face Quality", value=True)
            if enhance_face:
                enhance_level = st.slider(
                    "Enhancement Level",
                    min_value=0,
                    max_value=100,
                    value=70,
                    help="Higher values = more enhancement"
                )
        
        # 3. Photo sizes
        with st.expander("📏 Photo Size", expanded=True):
            size_options = {
                "Passport (2x2 inch)": (600, 600),
                "1x1 inch": (300, 300),
                "2x2 inch": (600, 600),
                "Wallet (2.5x3.5 inch)": (750, 1050),
                "PDS (Personal Data Sheet)": (450, 450),
                "4x6 inch": (1200, 1800)
            }
            selected_size = st.selectbox(
                "Select Size",
                list(size_options.keys())
            )
            
            # Show dimensions
            st.caption(f"Dimensions: {size_options[selected_size][0]} x {size_options[selected_size][1]} pixels")
        
        # 4. Name and signature
        with st.expander("📝 Name & Signature", expanded=True):
            add_name = st.checkbox("Add Name")
            if add_name:
                name_text = st.text_input("Full Name", placeholder="Juan Dela Cruz")
                name_position = st.selectbox(
                    "Name Position",
                    ["Bottom Center", "Bottom Left", "Bottom Right"]
                )
                name_color = st.color_picker("Name Color", "#000000")
                name_size = st.slider("Name Size", 10, 50, 20)
            
            add_signature = st.checkbox("Add Signature")
            if add_signature:
                st.info("Upload signature with transparent background for best results")
                signature_file = st.file_uploader(
                    "Upload Signature",
                    type=['png'],
                    key="signature"
                )
        
        # Process button
        st.markdown("---")
        process_btn = st.button(
            "✨ PROCESS PHOTO",
            type="primary",
            use_container_width=True
        )
        
        if process_btn:
            st.session_state.processed_image = None

# Main content
if uploaded_file:
    # Load image
    image = Image.open(uploaded_file)
    
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Store original
    if st.session_state.original_image is None:
        st.session_state.original_image = image
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📷 **Original Photo**")
        st.image(image, use_column_width=True)
        st.caption(f"Size: {image.size[0]} x {image.size[1]} pixels")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ✨ **Processed Photo**")
        
        if process_btn:
            with st.spinner("🔄 Processing your photo... Please wait"):
                # Progress bar
                progress_bar = st.progress(0)
                
                # Convert to numpy array
                img_array = np.array(image)
                progress_bar.progress(10)
                
                # 1. Remove background
                if remove_bg:
                    try:
                        # Convert to PIL for rembg
                        img_pil = Image.fromarray(img_array)
                        img_no_bg = remove(img_pil)
                        
                        # Create background
                        if bg_option == "Solid Color":
                            # Convert hex to RGB
                            bg_rgb = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                            background = Image.new('RGB', img_pil.size, bg_rgb)
                            background.paste(img_no_bg, mask=img_no_bg.split()[3] if len(img_no_bg.split()) == 4 else None)
                            img_array = np.array(background)
                        else:
                            # Keep transparent
                            img_array = np.array(img_no_bg)
                        
                        progress_bar.progress(40)
                        st.success("✓ Background removed")
                    except Exception as e:
                        st.warning("Background removal skipped (using simple blend)")
                        # Fallback: simple color blend
                        if bg_option == "Solid Color":
                            bg_rgb = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                            overlay = np.full(img_array.shape, bg_rgb, dtype=np.uint8)
                            img_array = cv2.addWeighted(img_array, 0.8, overlay, 0.2, 0)
                
                # 2. Face enhancement
                if enhance_face:
                    # Simple enhancement using OpenCV
                    img_array = cv2.detailEnhance(img_array, sigma_s=10, sigma_r=0.15)
                    progress_bar.progress(60)
                    st.success("✓ Face enhanced")
                
                # 3. Resize
                target_size = size_options[selected_size]
                img_array = cv2.resize(img_array, target_size, interpolation=cv2.INTER_CUBIC)
                progress_bar.progress(80)
                
                # 4. Add name
                if add_name and name_text:
                    img_pil = Image.fromarray(img_array)
                    draw = ImageDraw.Draw(img_pil)
                    
                    # Try to load font
                    try:
                        font = ImageFont.truetype("arial.ttf", name_size)
                    except:
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", name_size)
                        except:
                            font = ImageFont.load_default()
                    
                    # Calculate text position
                    text_bbox = draw.textbbox((0, 0), name_text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    
                    if name_position == "Bottom Center":
                        x = (img_pil.width - text_width) // 2
                        y = img_pil.height - name_size - 20
                    elif name_position == "Bottom Left":
                        x = 20
                        y = img_pil.height - name_size - 20
                    else:  # Bottom Right
                        x = img_pil.width - text_width - 20
                        y = img_pil.height - name_size - 20
                    
                    # Add text shadow
                    draw.text((x+2, y+2), name_text, font=font, fill='gray')
                    # Add main text
                    draw.text((x, y), name_text, font=font, fill=name_color)
                    
                    img_array = np.array(img_pil)
                    progress_bar.progress(90)
                    st.success("✓ Name added")
                
                # 5. Add signature
                if add_signature and signature_file:
                    signature = Image.open(signature_file)
                    if signature.mode != 'RGBA':
                        signature = signature.convert('RGBA')
                    
                    # Resize signature
                    signature.thumbnail((100, 50))
                    
                    # Convert img_array to PIL
                    img_pil = Image.fromarray(img_array)
                    
                    # Paste signature
                    sig_x = img_pil.width - signature.width - 20
                    sig_y = img_pil.height - signature.height - 20
                    img_pil.paste(signature, (sig_x, sig_y), signature)
                    
                    img_array = np.array(img_pil)
                    st.success("✓ Signature added")
                
                progress_bar.progress(100)
                time.sleep(0.5)
                progress_bar.empty()
                
                # Store processed image
                st.session_state.processed_image = img_array
                st.success("✅ **Photo processed successfully!**")
        
        # Display processed image
        if st.session_state.processed_image is not None:
            st.image(st.session_state.processed_image, use_column_width=True)
            
            # Show dimensions
            height, width = st.session_state.processed_image.shape[:2]
            st.caption(f"Size: {width} x {height} pixels | 300 DPI")
            
            # Download buttons
            st.markdown("### 📥 **Download Options**")
            
            col_a, col_b, col_c = st.columns(3)
            
            # Convert to PIL for saving
            result_pil = Image.fromarray(st.session_state.processed_image.astype('uint8'))
            
            # JPEG Download
            buf_jpeg = io.BytesIO()
            result_pil.save(buf_jpeg, format='JPEG', quality=95, dpi=(300, 300))
            buf_jpeg.seek(0)
            
            with col_a:
                st.download_button(
                    label="📷 JPEG",
                    data=buf_jpeg,
                    file_name="id_photo.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
            
            # PNG Download
            buf_png = io.BytesIO()
            result_pil.save(buf_png, format='PNG', dpi=(300, 300))
            buf_png.seek(0)
            
            with col_b:
                st.download_button(
                    label="🖼️ PNG",
                    data=buf_png,
                    file_name="id_photo.png",
                    mime="image/png",
                    use_container_width=True
                )
            
            # Create photo sheet for passport
            with col_c:
                if "Passport" in selected_size or "PDS" in selected_size:
                    # Create 2x2 grid
                    sheet = Image.new('RGB', (result_pil.width * 2 + 60, result_pil.height * 2 + 60), 'white')
                    
                    # Paste 4 copies
                    for i in range(2):
                        for j in range(2):
                            x = 20 + j * (result_pil.width + 20)
                            y = 20 + i * (result_pil.height + 20)
                            sheet.paste(result_pil, (x, y))
                    
                    buf_sheet = io.BytesIO()
                    sheet.save(buf_sheet, format='JPEG', quality=95)
                    buf_sheet.seek(0)
                    
                    st.download_button(
                        label="📄 4x6 Sheet",
                        data=buf_sheet,
                        file_name="photo_sheet.jpg",
                        mime="image/jpeg",
                        use_container_width=True
                    )
            
            # Success message
            st.markdown("""
            <div class="success-msg">
                ✅ Your photo is ready! HD Quality (300 DPI) - Perfect for printing
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Welcome screen with features
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2>👋 Welcome to ID Photo Editor Pro!</h2>
        <p style="color: #666; font-size: 1.2rem;">
            Upload a photo from the sidebar to get started with professional ID photo editing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h1>🎨</h1>
            <h3>Background Editor</h3>
            <p>Remove background and choose any color</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h1>👤</h1>
            <h3>Face Enhancement</h3>
            <p>Enhance face quality naturally</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <h1>📏</h1>
            <h3>Standard Sizes</h3>
            <p>Passport, 2x2, 1x1, PDS, and more</p>
        </div>
        """, unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div class="feature-box">
            <h1>📝</h1>
            <h3>Name & Signature</h3>
            <p>Perfect for PDS and documents</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="feature-box">
            <h1>💾</h1>
            <h3>HD Output</h3>
            <p>300 DPI print-ready photos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="feature-box">
            <h1>📄</h1>
            <h3>Photo Sheets</h3>
            <p>Create 4x6 sheets with multiple copies</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How to use
    st.markdown("---")
    st.markdown("""
    <div class="card">
        <h3>📋 How to Use:</h3>
        <ol>
            <li><strong>Upload</strong> your photo using the sidebar</li>
            <li><strong>Choose</strong> your desired settings (background, size, name, etc.)</li>
            <li><strong>Click</strong> PROCESS PHOTO button</li>
            <li><strong>Download</strong> your HD photo in JPEG or PNG format</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p>Made with ❤️ using Streamlit | For best results, use well-lit photos with clear face</p>
    <p style="font-size: 0.8rem;">© 2024 ID Photo Editor Pro</p>
</div>
""", unsafe_allow_html=True)
