from PIL import Image
import os
import math

# Define paths
IMAGE_FOLDER = "../data/photos/"
OUTPUT_FILE = "../data/photos/collage.png"

# Ensure the output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Get all .jpg and .png files
image_files = [os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".jpg", ".png"))]

# Set target collage size (small webpage resolution)
collage_width = 800  # Width in pixels
collage_height = 600  # Height in pixels

# Determine grid layout
num_images = len(image_files)
if num_images == 0:
    print("❌ No images found in the folder.")
    exit()

grid_cols = math.ceil(math.sqrt(num_images))  # Approximate square layout
grid_rows = math.ceil(num_images / grid_cols)

# Resize images to fit within the collage dimensions
thumb_width = collage_width // grid_cols
thumb_height = collage_height // grid_rows

# Create a blank canvas
collage = Image.new("RGB", (collage_width, collage_height), (255, 255, 255))

print(f"📂 Found {num_images} images. Creating a {grid_cols}x{grid_rows} grid.")
print(f"📏 Thumbnail size: {thumb_width}x{thumb_height}px")
print(f"🎨 Collage canvas size: {collage_width}x{collage_height}px")

# Load and paste images
processed_count = 0
skipped_count = 0

for index, img_path in enumerate(image_files):
    try:
        print(f"📷 Processing image {index+1}/{num_images}: {os.path.basename(img_path)}")

        img = Image.open(img_path)

        # Handle transparent images
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
            background = Image.new("RGBA", img.size, (255, 255, 255, 255))  # White background
            img = Image.alpha_composite(background, img).convert("RGB")
            print(f"🛠️ Converted {os.path.basename(img_path)} from RGBA to RGB.")

        else:
            img = img.convert("RGB")

        img = img.resize((thumb_width, thumb_height))  # Resize image to fit grid
        print(f"📏 Resized {os.path.basename(img_path)} to {thumb_width}x{thumb_height}px.")

        # Calculate placement
        x = (index % grid_cols) * thumb_width
        y = (index // grid_cols) * thumb_height
        print(f"📍 Placing {os.path.basename(img_path)} at ({x}, {y}).")

        collage.paste(img, (x, y))
        processed_count += 1

    except Exception as e:
        print(f"⚠️ Skipping {os.path.basename(img_path)} due to error: {e}")
        skipped_count += 1

# Save the final collage
collage.save(OUTPUT_FILE)
collage.show()

# Final summary
print(f"\n✅ Collage created successfully!")
print(f"🖼️ Saved as: {OUTPUT_FILE}")
print(f"📊 Processed images: {processed_count}/{num_images}")
print(f"⚠️ Skipped images: {skipped_count}/{num_images}")