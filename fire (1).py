import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
# Global variable to store the image path
image_path = None

# Global variable to store image dimensions and pixel data
largeur = hauteur = None
pixel_data = None

def upload_image():
    global image_path, largeur, hauteur, pixel_data  # Declare global variables

    # Open a file dialog and restrict it to .bmp files
    image_path = filedialog.askopenfilename(
        title="Select a BMP file",
        filetypes=[("BMP Files", "*.bmp")]
    )
    
    if image_path:
        try:
            # Open the BMP file and display a confirmation
            img = Image.open(image_path)
            img.thumbnail((200, 200))  # Resize for display purposes
            img_tk = ImageTk.PhotoImage(img)
            
            label_image.config(image=img_tk)
            label_image.image = img_tk  # Keep a reference to avoid garbage collection
            messagebox.showinfo("Success", f"Image uploaded: {image_path}")
            
            # Read the image data from the file
            with open(image_path, 'rb') as f:
                header = f.read(54)  # BMP header is 54 bytes

                # The width and height are stored as 4-byte integers
                largeur = int.from_bytes(header[18:22], byteorder='little')
                hauteur = int.from_bytes(header[22:26], byteorder='little')

                # Reading the pixel data
                pixel_data = f.read()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open the image. {str(e)}")
    else:
        messagebox.showwarning("No file selected", "Please select a BMP file.")

def save_bmp(filename, largeur, hauteur, pixel_data):
    if image_path and largeur and hauteur and pixel_data:
        with open(filename, 'wb') as f:
            # BMP header (54 bytes)
            header = bytearray(54)
            header[0:2] = b'BM'
            header[2:6] = (54 + len(pixel_data)).to_bytes(4, byteorder='little')
            header[10:14] = (54).to_bytes(4, byteorder='little')  # Pixel data offset
            header[14:18] = (40).to_bytes(4, byteorder='little')  # Header size
            header[18:22] = largeur.to_bytes(4, byteorder='little')
            header[22:26] = hauteur.to_bytes(4, byteorder='little')
            header[26:28] = (1).to_bytes(2, byteorder='little')  # Planes
            header[28:30] = (24).to_bytes(2, byteorder='little')  # Bits per pixel
            header[34:38] = len(pixel_data).to_bytes(4, byteorder='little')  # Image size

            # Write header and pixel data
            f.write(header)
            f.write(pixel_data)
    else:
        messagebox.showerror("Error", "Please upload a BMP image first.")

def save_rgb():
    # Prepare RGB data and save
    if pixel_data:
        image_rouge = bytearray()
        image_vert = bytearray()
        image_bleu = bytearray()
        for i in range(largeur * hauteur):
            b = pixel_data[i * 3]
            g = pixel_data[i * 3 + 1]
            r = pixel_data[i * 3 + 2]
           # Red channel only image (R, 0, 0)
            image_rouge.extend([0, 0, r])
            # Green channel only image (0, G, 0)
            image_vert.extend([0, g, 0])
            # Blue channel only image (0, 0, B)
            image_bleu.extend([b, 0, 0])
        save_bmp('image_r.bmp', largeur, hauteur, image_rouge)
        save_bmp('image_v.bmp', largeur, hauteur, image_vert)
        save_bmp('image_b.bmp', largeur, hauteur, image_bleu)
# Check if images exist after saving
        if all(os.path.exists(path) for path in ['image_r.bmp', 'image_v.bmp', 'image_b.bmp']):
            display_images(title="RGB images", image_paths=['image_r.bmp', 'image_v.bmp', 'image_b.bmp'],labels=['Red image', 'Green image', 'Blue image'])
        else:
            messagebox.showerror("Error", "Images were not saved successfully.")
    else:
        messagebox.showwarning("Warning", "Upload a BMP file before saving.")

def save_xyz():
    # Prepare XYZ data and save
    if pixel_data:
        image_x, image_y, image_z = bytearray(), bytearray(), bytearray()
        for i in range(largeur * hauteur):
            b = pixel_data[i * 3]
            g = pixel_data[i * 3 + 1]
            r = pixel_data[i * 3 + 2]
            
            r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
            x = r_norm * 0.4124564 + g_norm * 0.3575761 + b_norm * 0.1804375
            y_xyz = r_norm * 0.2126729 + g_norm * 0.7151522 + b_norm * 0.0721750
            z = r_norm * 0.0193339 + g_norm * 0.1191920 + b_norm * 0.9503041

            x_scaled = int(max(0, min(255, x * 255)))
            y_scaled = int(max(0, min(255, y_xyz * 255)))
            z_scaled = int(max(0, min(255, z * 255)))

            image_x.extend([x_scaled, 0, 0])  # X in R
            image_y.extend([0, y_scaled, 0])  # Y in G
            image_z.extend([0, 0, z_scaled])  # Z in B

        save_bmp('image_x.bmp', largeur, hauteur, image_x )
        save_bmp('image_y.bmp', largeur, hauteur, image_y )
        save_bmp('image_z.bmp', largeur, hauteur, image_z )
        if all(os.path.exists(path) for path in ['image_x.bmp', 'image_y.bmp', 'image_z.bmp']):
            display_images(title="XYZ images", image_paths=['image_x.bmp', 'image_y.bmp', 'image_z.bmp'],labels=['X image', 'Y image', 'Z image'])
        else:
            messagebox.showerror("Error", "Images were not saved successfully.")
    else:
        messagebox.showwarning("Warning", "Upload a BMP file before saving.")


def save_yuv():
    # Prepare YUV data and save
    if pixel_data:
        image_y, image_u, image_v = bytearray(), bytearray(), bytearray()
        for i in range(largeur * hauteur):
            b = pixel_data[i * 3]
            g = pixel_data[i * 3 + 1]
            r = pixel_data[i * 3 + 2]
            
            y = 0.299 * r + 0.587 * g + 0.114 * b
            u = -0.147 * r - 0.289 * g + 0.436 * b
            v = 0.615 * r - 0.515 * g - 0.100 * b

            y_scaled = int(max(0, min(255, y)))
            u_scaled = int(max(0, min(255, u + 128)))
            v_scaled = int(max(0, min(255, v + 128)))

            image_y.extend([y_scaled, 0, 0])  # Y in R
            image_u.extend([0, u_scaled, 0])  # U in G
            image_v.extend([0, 0, v_scaled])  # V in B

        save_bmp('image_y.bmp', largeur, hauteur, image_y )
        save_bmp('image_u.bmp', largeur, hauteur, image_u )
        save_bmp('image_v.bmp', largeur, hauteur, image_v )
        
        if all(os.path.exists(path) for path in ['image_y.bmp', 'image_u.bmp', 'image_v.bmp']):
            display_images(title="YUV images", image_paths=['image_y.bmp', 'image_u.bmp', 'image_v.bmp'],labels=['Y image', 'U image', 'V image'])
        else:
            messagebox.showerror("Error", "Images were not saved successfully.")
    else:
        messagebox.showwarning("Warning", "Upload a BMP file before saving.")
        
def save_cmyk():
    # Prepare CMYK data and save
    if pixel_data:
        image_c, image_m, image_y, image_k = bytearray(), bytearray(), bytearray(), bytearray()
        for i in range(largeur * hauteur):
            b = pixel_data[i * 3]
            g = pixel_data[i * 3 + 1]
            r = pixel_data[i * 3 + 2]
            
            c = 1 - r / 255.0
            m = 1 - g / 255.0
            y = 1 - b / 255.0
            k = min(c, m, y)

            c_scaled = int(max(0, min(255, c * 255)))
            m_scaled = int(max(0, min(255, m * 255)))
            y_scaled = int(max(0, min(255, y * 255)))
            k_scaled = int(max(0, min(255, k * 255)))

            image_c.extend([c_scaled, 0, 0])  # C in R
            image_m.extend([0, m_scaled, 0])  # M in G
            image_y.extend([0, 0, y_scaled])  # Y in B
            image_k.extend([0, 0, k_scaled])  # K in B

        save_bmp('image_c.bmp', largeur, hauteur, image_c )
        save_bmp('image_m.bmp', largeur, hauteur, image_m )
        save_bmp('image_y.bmp', largeur, hauteur, image_y )
        save_bmp('image_k.bmp', largeur, hauteur, image_k )
        
        if all(os.path.exists(path) for path in ['image_c.bmp', 'image_m.bmp', 'image_y.bmp', 'image_k.bmp']):
            display_images(title="CMYK images", image_paths=['image_c.bmp', 'image_m.bmp', 'image_y.bmp', 'image_k.bmp'],labels=['C image', 'M image', 'Y image', 'K image'])
        else:
            messagebox.showerror("Error", "Images were not saved successfully.")
    else:
        messagebox.showwarning("Warning", "Upload a BMP file before saving.")
        
def display_images(title , image_paths,labels):
    # Create a new window to display images
    display_window = tk.Toplevel(root)
    display_window.title(title)

    # Load and display images
    images = []
    for img_path in image_paths:
        try:
            img = Image.open(img_path)
            img = img.resize((200, 200), Image.LANCZOS)  # Resize using LANCZOS filter
            images.append(ImageTk.PhotoImage(img))
        except Exception as e:
            print(f"Failed to load image {img_path}: {e}")

    # Create a Frame to hold the images
    frame = tk.Frame(display_window)
    frame.pack(pady=40)

    # Display each image and its label
    for i, img in enumerate(images):
        # Create a label for the image
        img_label = tk.Label(frame, image=img)
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.grid(row=0, column=i, padx=10)  # Place each image in a separate column

        # Create a label for the text under the image
        text_label = tk.Label(frame, text=labels[i])
        text_label.grid(row=1, column=i, padx=10)  # Place text label below the image

# Create the main window
root = tk.Tk()
root.title("BMP Image Uploader")
root.geometry("400x600")
root.eval('tk::PlaceWindow . center')

# Add a button to trigger the file upload dialog
btn_upload = tk.Button(root, text="Upload BMP Image", command=upload_image)
btn_upload.pack(pady=20)

# Label to display the selected image
label_image = tk.Label(root)
label_image.pack(pady=20)

# Add buttons to save images in different formats
btn_save_rgb = tk.Button(root, text="Save as RGB", command=save_rgb)
btn_save_rgb.pack(pady=10)

btn_save_xyz = tk.Button(root, text="Save as XYZ", command=save_xyz)
btn_save_xyz.pack(pady=10)

btn_save_yuv = tk.Button(root, text="Save as YUV", command=save_yuv)
btn_save_yuv.pack(pady=10)

btn_save_cmyk = tk.Button(root, text="Save as CMYK", command=save_cmyk)
btn_save_cmyk.pack(pady=10)

# Run the tkinter event loop
root.mainloop()
