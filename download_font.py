import os
import requests
import zipfile
import io

def download_oxanium_font():
    """Download Oxanium font from Google Fonts"""
    font_url = "https://fonts.google.com/download?family=Oxanium"
    font_folder = "d:\\Projects\\Bulk Postser Generator"
    
    print("Downloading Oxanium font...")
    
    try:
        # Download the font zip file
        response = requests.get(font_url)
        response.raise_for_status()
        
        # Extract the zip file
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(font_folder)
        
        # Check if the ExtraBold variant exists
        font_path = os.path.join(font_folder, "Oxanium-ExtraBold.ttf")
        if not os.path.exists(font_path):
            # Look for the font in the extracted folder
            for root, dirs, files in os.walk(font_folder):
                for file in files:
                    if file == "Oxanium-ExtraBold.ttf":
                        src_path = os.path.join(root, file)
                        # Copy to the main folder
                        with open(src_path, 'rb') as src, open(font_path, 'wb') as dst:
                            dst.write(src.read())
                        print(f"Found and copied font to {font_path}")
                        break
        
        if os.path.exists(font_path):
            print(f"Oxanium ExtraBold font downloaded successfully to {font_path}")
        else:
            print("Could not find Oxanium-ExtraBold.ttf in the downloaded package")
            print("Please download it manually from https://fonts.google.com/specimen/Oxanium")
    except Exception as e:
        print(f"Error downloading font: {e}")
        print("Please download Oxanium font manually from https://fonts.google.com/specimen/Oxanium")
        print("and place Oxanium-ExtraBold.ttf in your project folder")

if __name__ == "__main__":
    download_oxanium_font()