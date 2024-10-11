# Open the BMP file in binary mode
image_path = 'prj.bmp'

# Read the image data from the file
with open(image_path, 'rb') as f:
    # BMP files have a header that contains metadata
    header = f.read(54)  # BMP header is 54 bytes

    # The width and height are stored as 4-byte integers starting at byte 18 and 22 respectively
    largeur = int.from_bytes(header[18:22], byteorder='little')
    hauteur = int.from_bytes(header[22:26], byteorder='little')

    # Reading the pixel data
    pixel_data = f.read()

# BMP stores pixel data in BGR format (not RGB)
num_pixels = largeur * hauteur
print(f'Image size: {largeur} x {hauteur} pixels')
print(f'Number of pixels: {num_pixels}')

# Prepare empty lists to hold pixel data for red, green, and blue channels
image_rouge = bytearray()
image_vert = bytearray()
image_bleu = bytearray()

# YUV
image_y = bytearray()
image_u = bytearray()
image_v = bytearray()

# CMYK
image_c = bytearray()
image_m = bytearray()
image_y_cmyk = bytearray()  # Renaming to avoid confusion with Y from YUV
image_k = bytearray()

# XYZ
image_x = bytearray()
image_y_xyz = bytearray()  # Renaming to avoid confusion with Y from YUV
image_z = bytearray()

# Iterate over the pixel data
for i in range(num_pixels):
    b = pixel_data[i * 3]  # Blue channel
    g = pixel_data[i * 3 + 1]  # Green channel
    r = pixel_data[i * 3 + 2]  # Red channel

    # Red channel only image (R, 0, 0)
    image_rouge.extend([0, 0, r])
    # Green channel only image (0, G, 0)
    image_vert.extend([0, g, 0])
    # Blue channel only image (0, 0, B)
    image_bleu.extend([b, 0, 0])

    # Convert RGB to YUV
    Y = int(0.299 * r + 0.587 * g + 0.114 * b)
    U = int(-0.14713 * r - 0.28886 * g + 0.436 * b + 128)  # Adding 128 for U
    V = int(0.615 * r - 0.51499 * g - 0.10001 * b + 128)  # Adding 128 for V

    # Ensure values are in the 0-255 range
    Y = max(0, min(255, Y))
    U = max(0, min(255, U))
    V = max(0, min(255, V))

    image_y.extend([Y, Y, Y])  # Y value stored in all three channels for display
    image_u.extend([U, 0, 0])  # U value stored in R channel
    image_v.extend([0, 0, V])  # V value stored in B channel

    # Convert RGB to CMY
    C = 1 - (r / 255)
    M = 1 - (g / 255)
    Y_cmyk = 1 - (b / 255)

    # Calculate K (black)
    K = min(C, M, Y_cmyk)

    # Calculate final CMYK values
    if K == 1:
        C = 0
        M = 0
        Y_cmyk = 0
    else:
        C = (C - K) / (1 - K)
        M = (M - K) / (1 - K)
        Y_cmyk = (Y_cmyk - K) / (1 - K)

    # Scale CMYK values to the 0-255 range
    C = int(C * 255)
    M = int(M * 255)
    Y_cmyk = int(Y_cmyk * 255)
    K = int(K * 255)

    # Save CMYK values (for demonstration, we store them in RGB format)
    image_c.extend([C, 0, 0])  # C value in R channel
    image_m.extend([0, M, 0])  # M value in G channel
    image_y_cmyk.extend([0, 0, Y_cmyk])  # Y value in B channel
    image_k.extend([K, K, K])  # K value in grayscale

    # Convert RGB to XYZ
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    # Apply the transformation to XYZ (assuming sRGB color space)
    x = r_norm * 0.4124564 + g_norm * 0.3575761 + b_norm * 0.1804375
    y_xyz = r_norm * 0.2126729 + g_norm * 0.7151522 + b_norm * 0.0721750
    z = r_norm * 0.0193339 + g_norm * 0.1191920 + b_norm * 0.9503041

    # Scale XYZ values to the 0-255 range for display (optional)
    x_scaled = int(max(0, min(255, x * 255)))
    y_scaled = int(max(0, min(255, y_xyz * 255)))
    z_scaled = int(max(0, min(255, z * 255)))

    # Store XYZ values in respective bytearrays (for demonstration)
    image_x.extend([x_scaled, 0, 0])  # X value in R channel
    image_y_xyz.extend([0, y_scaled, 0])  # Y value in G channel
    image_z.extend([0, 0, z_scaled])  # Z value in B channel


# Write BMP headers and pixel data to new files for each channel
def save_bmp(filename, largeur, hauteur, pixel_data):
    with open(filename, 'wb') as f:
        # BMP header (54 bytes)
        header = bytearray(54)

        # Set the necessary values in the BMP header
        header[0:2] = b'BM'  # Signature
        header[2:6] = (54 + len(pixel_data)).to_bytes(4, byteorder='little')  # File size
        header[10:14] = (54).to_bytes(4, byteorder='little')  # Pixel data offset
        header[14:18] = (40).to_bytes(4, byteorder='little')  # Header size
        header[18:22] = largeur.to_bytes(4, byteorder='little')  # Image width
        header[22:26] = hauteur.to_bytes(4, byteorder='little')  # Image height
        header[26:28] = (1).to_bytes(2, byteorder='little')  # Planes
        header[28:30] = (24).to_bytes(2, byteorder='little')  # Bits per pixel
        header[34:38] = len(pixel_data).to_bytes(4, byteorder='little')  # Image size

        # Write header and pixel data
        f.write(header)
        f.write(pixel_data)


# Save the images
save_bmp('image_rouge.bmp', largeur, hauteur, image_rouge)
save_bmp('image_vert.bmp', largeur, hauteur, image_vert)
save_bmp('image_bleu.bmp', largeur, hauteur, image_bleu)

# Save the YUV images
save_bmp('image_y.bmp', largeur, hauteur, image_y)
save_bmp('image_u.bmp', largeur, hauteur, image_u)
save_bmp('image_v.bmp', largeur, hauteur, image_v)

# Save the CMYK images
save_bmp('image_c.bmp', largeur, hauteur, image_c)
save_bmp('image_m.bmp', largeur, hauteur, image_m)
save_bmp('image_y_cmyk.bmp', largeur, hauteur, image_y_cmyk)
save_bmp('image_k.bmp', largeur, hauteur, image_k)

# Save the XYZ images
save_bmp('image_x.bmp', largeur, hauteur, image_x)
save_bmp('image_y_xyz.bmp', largeur, hauteur, image_y_xyz)
save_bmp('image_z.bmp', largeur, hauteur, image_z)