import os
import csv
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import glob
import re

def generate_posters(csv_file, poster_template, photos_folder, output_folder, use_placeholder=True):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Create a placeholder image
    placeholder_width, placeholder_height = 230, 230
    placeholder_image = Image.new('RGB', (placeholder_width, placeholder_height), color=(100, 100, 100))
    draw = ImageDraw.Draw(placeholder_image)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    draw.text((placeholder_width//4, placeholder_height//2), "No Photo", fill="white", font=font)
    
    # Get all image files in the photos folder
    all_image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        all_image_files.extend(glob.glob(os.path.join(photos_folder, ext)))
    
    print(f"Found {len(all_image_files)} image files in photos folder")
    
    # Create a mapping of roll numbers to image files
    # This will help with manual mapping if needed
    roll_to_image = {}
    
    # Read the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        # Skip header row if it exists
        header = next(reader, None)
        
        # Track missing photos
        missing_photos = []
        processed_count = 0
        
        # Process each student
        for row in reader:
            roll_number, name, section = row
            
            # Load the poster template
            poster = Image.open(poster_template)
            
            # Rectangle area in the poster
            rectangle_x1, rectangle_y1 = 466.78, 751.43
            rectangle_width, rectangle_height = 266.44, 334.62
            
            # Try to find the photo using various methods
            photo_found = False
            student_photo = None
            
            # Method 1: Direct file path check with various extensions and patterns
            possible_filenames = [
                f"{roll_number}.jpg", 
                f"{roll_number}.jpeg", 
                f"{roll_number}.png",
                f"{roll_number.lower()}.jpg",
                f"{roll_number.upper()}.jpg",
                f"{roll_number}_*.jpg",  # Wildcard matching
                f"*{roll_number}*.jpg",  # Contains roll number
                f"{name.replace(' ', '_')}.jpg",  # Name-based
                f"{name.split()[0]}.jpg"  # First name only
            ]
            
            for pattern in possible_filenames:
                if '*' in pattern:
                    # Handle wildcard patterns
                    matching_files = glob.glob(os.path.join(photos_folder, pattern))
                    if matching_files:
                        try:
                            student_photo = Image.open(matching_files[0])
                            photo_found = True
                            print(f"Found photo for {name} using pattern {pattern}: {matching_files[0]}")
                            break
                        except Exception as e:
                            print(f"Error opening {matching_files[0]}: {e}")
                else:
                    # Direct file check
                    photo_path = os.path.join(photos_folder, pattern)
                    if os.path.exists(photo_path):
                        try:
                            student_photo = Image.open(photo_path)
                            photo_found = True
                            print(f"Found photo for {name} at {photo_path}")
                            break
                        except Exception as e:
                            print(f"Error opening {photo_path}: {e}")
            
            # Method 2: Try to find by partial roll number match
            if not photo_found:
                for img_path in all_image_files:
                    base_name = os.path.basename(img_path)
                    if roll_number in base_name:
                        try:
                            student_photo = Image.open(img_path)
                            photo_found = True
                            print(f"Found photo for {name} via partial match: {img_path}")
                            break
                        except Exception as e:
                            print(f"Error opening {img_path}: {e}")
            
            # After finding the photo and before pasting it onto the poster
            if not photo_found:
                print(f"No photo found for {name} (Roll No: {roll_number})")
                missing_photos.append((roll_number, name))
                
                if use_placeholder:
                    # Use placeholder image
                    student_photo = placeholder_image.resize((int(rectangle_width), int(rectangle_height)))
                else:
                    continue
            else:
                # Resize the photo to fit the rectangle
                student_photo = student_photo.resize((int(rectangle_width), int(rectangle_height)))
            
            # Create a mask with rounded corners
            mask = Image.new('L', (int(rectangle_width), int(rectangle_height)), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.rounded_rectangle([(0, 0), (int(rectangle_width), int(rectangle_height))], radius=50, fill=255)
            
            # Apply the mask to create rounded corners
            student_photo_rgba = student_photo.convert("RGBA")
            masked_photo = Image.new("RGBA", student_photo.size, (0, 0, 0, 0))
            masked_photo.paste(student_photo_rgba, (0, 0), mask)
            
            # Paste the masked photo onto the poster
            poster.paste(masked_photo, (int(rectangle_x1), int(rectangle_y1)), masked_photo)
            
            # Add name and section text
            draw = ImageDraw.Draw(poster)
            
            # Download and use Oxanium font
            font_path = "d:\\Projects\\Bulk Postser Generator\\Oxanium-ExtraBold.ttf"
            if not os.path.exists(font_path):
                # If font doesn't exist, try to download it
                try:
                    import requests
                    import zipfile
                    import io
                    
                    print("Downloading Oxanium font...")
                    font_url = "https://fonts.googleapis.com/css2?family=Oxanium:wght@800&display=swap"
                    response = requests.get(font_url)
                    
                    # Extract font URL from CSS
                    font_file_url = None
                    for line in response.text.split('\n'):
                        if "url(" in line and ".ttf" in line:
                            font_file_url = line.split("url(")[1].split(")")[0]
                            break
                    
                    if font_file_url:
                        # Download the actual font file
                        font_response = requests.get(font_file_url)
                        with open(font_path, 'wb') as f:
                            f.write(font_response.content)
                        print(f"Downloaded Oxanium font to {font_path}")
                    else:
                        print("Could not extract font URL from Google Fonts")
                except Exception as e:
                    print(f"Error downloading font: {e}")
            
            # Try to use Oxanium font, fall back to Arial if not available
            try:
                if os.path.exists(font_path):
                    name_font = ImageFont.truetype(font_path, 46)
                    section_font = ImageFont.truetype(font_path, 40)
                else:
                    name_font = ImageFont.truetype("arial.ttf", 46)
                    section_font = ImageFont.truetype("arial.ttf", 40)
            except Exception as e:
                print(f"Error loading font: {e}")
                name_font = ImageFont.load_default()
                section_font = ImageFont.load_default()
            
            # Center align the name text
            name_text = f"{name}"
            name_width = draw.textlength(name_text, font=name_font)
            # Center horizontally relative to the photo position
            name_x = rectangle_x1 + (rectangle_width - name_width) / 2
            name_y = 634.61
            draw.text((int(name_x), int(name_y)), name_text, fill="#ffffff", font=name_font)
            
            # Center align the section text - removed "Section:" prefix
            section_text = f"{section}"  # Only display the section content
            section_width = draw.textlength(section_text, font=section_font)
            # Center horizontally relative to the photo position
            section_x = rectangle_x1 + (rectangle_width - section_width) / 2
            section_y = 684.6
            draw.text((int(section_x), int(section_y)), section_text, fill="#e4d494", font=section_font)
            
            # Save the generated poster
            safe_name = name.replace('/', '_').replace('\\', '_').replace(':', '_')
            output_path = os.path.join(output_folder, f"{roll_number}_{safe_name}_poster.jpg")
            poster.save(output_path)
            processed_count += 1
            print(f"Generated poster for {name} (Roll No: {roll_number})")
        
        # Print summary
        print("\n" + "="*50)
        print(f"SUMMARY: Generated {processed_count} posters")
        
        if missing_photos:
            print(f"\nWARNING: {len(missing_photos)} students have missing photos:")
            # Only print roll numbers of students with missing photos
            for roll, _ in missing_photos:
                print(f"  - {roll}")
            
            if use_placeholder:
                print("\nPlaceholder images were used for missing photos.")
            
            # Create a helper script to manually map photos
            create_manual_mapping_script(missing_photos, all_image_files, photos_folder)
        else:
            print("\nAll posters generated successfully with no missing photos!")

def create_manual_mapping_script(missing_photos, all_image_files, photos_folder):
    """Create a helper script to manually map photos to students"""
    script_path = "d:\\Projects\\Bulk Postser Generator\\manual_photo_mapping.py"
    
    with open(script_path, 'w') as f:
        f.write("""import os
import shutil
import glob

# This script helps you manually map photos to students
# For each missing photo, you can specify the path to the correct photo

photos_folder = "{}"

# List of students with missing photos
missing_photos = {}

# List of available image files
available_images = {}

# For each missing photo, copy the correct image and rename it
for roll, name in missing_photos:
    print(f"\\nStudent: {{name}} (Roll No: {{roll}})")
    print("Available images:")
    for i, img_path in enumerate(available_images):
        print(f"  {{i}}: {{os.path.basename(img_path)}}")
    
    choice = input("Enter the number of the correct image (or 's' to skip): ")
    if choice.lower() == 's':
        continue
    
    try:
        choice = int(choice)
        if 0 <= choice < len(available_images):
            src_path = available_images[choice]
            dest_path = os.path.join(photos_folder, f"{{roll}}.jpg")
            shutil.copy2(src_path, dest_path)
            print(f"Copied {{src_path}} to {{dest_path}}")
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid input")

print("\\nMapping complete. Run the poster generation script again.")
""".format(
            photos_folder.replace('\\', '\\\\'),
            repr(missing_photos),
            repr(all_image_files)
        ))
    
    print(f"\nCreated a helper script for manual photo mapping: {script_path}")
    print("Run this script to manually map photos to students with missing photos.")

if __name__ == "__main__":
    # Define paths
    csv_file = "d:\\Projects\\Bulk Postser Generator\\students.csv"
    poster_template = "d:\\Projects\\Bulk Postser Generator\\poster_template.jpg"
    photos_folder = "d:\\Projects\\Bulk Postser Generator\\photos"
    output_folder = "d:\\Projects\\Bulk Postser Generator\\generated_posters"
    
    # List all files in the photos folder to help with debugging
    if os.path.exists(photos_folder):
        print(f"\nFiles in photos folder ({photos_folder}):")
        files = os.listdir(photos_folder)
        if files:
            for file in files:
                print(f"  - {file}")
                # Print file details
                file_path = os.path.join(photos_folder, file)
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"    Size: {file_size:.2f} KB")
        else:
            print("  No files found in photos folder!")
            print("\nPlease add student photos to this folder before running the script.")
            print("Photos should be named according to roll numbers (e.g., 22BCAA65.jpg)")
            exit(1)
    else:
        print(f"\nPhotos folder not found: {photos_folder}")
        os.makedirs(photos_folder)
        print(f"Created photos folder: {photos_folder}")
        print("\nPlease add student photos to this folder before running the script.")
        print("Photos should be named according to roll numbers (e.g., 22BCAA65.jpg)")
        exit(1)
    
    # Generate posters with placeholder images for missing photos
    generate_posters(csv_file, poster_template, photos_folder, output_folder, use_placeholder=True)
    