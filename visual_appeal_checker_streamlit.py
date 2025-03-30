# Updated Streamlit code with human-readable comments added to analysis


import streamlit as st
import os
import requests
import pandas as pd
import tempfile

# Title
st.title("🖼️ Visual Appeal Checker with Comments (Powered by Sightengine AI)")

# Sidebar for API Key Input
st.sidebar.header("🔐 API Credentials")
api_user = st.sidebar.text_input("Sightengine API User", type="default")
api_secret = st.sidebar.text_input("Sightengine API Secret", type="password")

# Upload images
uploaded_files = st.file_uploader("📁 Upload Image Files", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

# Process Button
if st.button("🔍 Analyze Images") and uploaded_files and api_user and api_secret:
    results = []

    with st.spinner("Analyzing images using Sightengine..."):
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name

            response = requests.post(
                url='https://api.sightengine.com/1.0/check.json',
                files={'media': open(tmp_file_path, 'rb')},
                data={
                    'models': 'image-properties',
                    'api_user': api_user,
                    'api_secret': api_secret
                }
            )

            output = response.json()
            media = output.get('media', {})

            sharpness = media.get('sharpness', 0)
            contrast = media.get('contrast', 0)
            brightness = media.get('brightness', 0)

            is_blurry = sharpness < 0.3
            low_contrast = contrast < 0.3

            # Generate human-readable comment
            if is_blurry and low_contrast:
                comment = "Image is blurry and has low contrast, not suitable for use."
            elif is_blurry:
                comment = "Image is blurry and needs better focus."
            elif low_contrast:
                comment = "Low contrast may affect readability."
            else:
                comment = "Image is clear and visually appealing."

            result = {
                'Image Name': uploaded_file.name,
                'Blurry': is_blurry,
                'Low Contrast': low_contrast,
                'Sharpness Score': round(sharpness, 2),
                'Contrast Score': round(contrast, 2),
                'Brightness': round(brightness, 2),
                'Suggested Action': 'Not Allowed' if is_blurry or low_contrast else 'Allowed',
                'Comment': comment
            }
            results.append(result)

        df = pd.DataFrame(results)
        st.success("✅ Analysis complete!")
        st.dataframe(df)

        # Provide CSV download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV Report", data=csv, file_name="visual_appeal_report.csv", mime="text/csv")

