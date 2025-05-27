import os
import cv2
import numpy as np
from rembg import remove
from PIL import Image

# Define input and output folders
input_folder = "auto"
output_folder = "auto-results"
output_text_file = os.path.join(output_folder, "output_results.txt")

# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Try to open the output text file
try:
    with open(output_text_file, "w") as text_file:
        text_file.write("Image Processing Results:\n")
        text_file.write("="*50 + "\n")
    print(f" Successfully opened {output_text_file} for writing")
except Exception as e:
    print(f" Error opening text file: {e}")
    exit()

# Process all TIFF images
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".tiff"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename.replace(".tiff", ".png"))  # Convert output format to PNG
        
        print(f"📌 Processing Image: {filename}")
        
        # Load the image
        image = cv2.imread(input_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Binary threshold for contour detection
        _, threshold = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        black_contour = max(contours, key=cv2.contourArea)

        # Compute center of black region
        moments = cv2.moments(black_contour)
        if moments["m00"] != 0:
            black_center = (int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"]))
            cv2.circle(image, black_center, 5, (0, 0, 255), -1)  # **Red dot for black center**
        else:
            black_center = None

        # Remove background
        try:
            with open(input_path, "rb") as file:
                input_image = file.read()
            output_image = remove(input_image)
            with open(output_path, "wb") as file:
                file.write(output_image)
        except Exception as e:
            print(f" Error processing image {filename}: {e}")
            continue

        # Load the processed image
        image = cv2.imread(output_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Hough Circle Detection
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
            param1=50, param2=30, minRadius=10, maxRadius=0
        )

        if circles is None:
            print(f"⚠ No circles detected in {filename}")
            continue  # Skip this image if no circle is found
        else:
            print(f" Circle detected in {filename}")

        if black_center is not None:
            circles = np.uint16(np.around(circles))
            most_prominent_circle = circles[0][0]
            blue_center = (most_prominent_circle[0], most_prominent_circle[1])
            blue_radius = most_prominent_circle[2]

            # Draw detected blue circle
            cv2.circle(image, blue_center, blue_radius, (255, 0, 0), 2)  # **Blue circle**
            cv2.circle(image, blue_center, 5, (255, 255, 0), -1)  # **Cyan dot for center**

            # Extend the red line
            direction_vector = np.array(blue_center) - np.array(black_center)
            norm_direction = direction_vector / (np.linalg.norm(direction_vector) + 1e-6)

            line_start = (
                int(black_center[0] - norm_direction[0] * blue_radius * 2),
                int(black_center[1] - norm_direction[1] * blue_radius * 2)
            )

            line_end = (
                int(blue_center[0] + norm_direction[0] * blue_radius * 2),
                int(blue_center[1] + norm_direction[1] * blue_radius * 2)
            )

            cv2.line(image, line_start, line_end, (0, 0, 255), 2)  # **Red extended line**

            # Detect intersection points
            num_steps = 200
            purple_points = []
            for i in range(num_steps + 1):
                x = int(line_start[0] + (line_end[0] - line_start[0]) * i / num_steps)
                y = int(line_start[1] + (line_end[1] - line_start[1]) * i / num_steps)
                if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                    pixel = image[y, x]
                    if pixel[1] > 150 and pixel[2] > 150:
                        cv2.circle(image, (x, y), 5, (0, 165, 255), -1)  # **Orange intersections**
                    elif pixel[2] > 150 and cv2.pointPolygonTest(black_contour, (x, y), False) >= 0:
                        image[y, x] = (128, 0, 128)
                        purple_points.append((x, y))

            # Find farthest purple points
            left_side = [p for p in purple_points if p[0] < black_center[0]]
            right_side = [p for p in purple_points if p[0] > black_center[0]]

            farthest_left = max(left_side, key=lambda p: np.linalg.norm(np.array(p) - np.array(black_center)), default=None)
            farthest_right = max(right_side, key=lambda p: np.linalg.norm(np.array(p) - np.array(black_center)), default=None)

            blue_points = []
            if farthest_left:
                blue_points.append(farthest_left)
            if farthest_right:
                blue_points.append(farthest_right)

            # Find the closest blue point to the blue center
            if blue_points:
                closest_blue_to_blue = min(blue_points, key=lambda p: np.linalg.norm(np.array(p) - np.array(blue_center)))
                
                # Draw a purple line
                cv2.line(image, blue_center, closest_blue_to_blue, (128, 0, 128), 2)  # **Purple connection**
                
                # Draw orange point
                cv2.circle(image, closest_blue_to_blue, 10, (0, 165, 255), -1)  # **Orange dot**
                
                # Calculate the distance
                distance = np.linalg.norm(np.array(blue_center) - np.array(closest_blue_to_blue))

                # Save results to text file
                with open(output_text_file, "a") as text_file:  # Append mode
                    text_file.write(f"Image: {filename}\n")
                    text_file.write(f"  - Blue Circle Radius: {blue_radius:.2f} pixels\n")
                    text_file.write(f"  - Distance between Blue Center and Orange Point: {distance:.2f} pixels\n")
                    text_file.write("=" * 50 + "\n")

                print(f"📏 Distance: {distance:.2f} pixels")

        # Save the modified image
        cv2.imwrite(output_path, image)
        print(f" Processed and saved: {output_path}")

print(f" Batch processing completed! Results saved in {output_text_file}")
