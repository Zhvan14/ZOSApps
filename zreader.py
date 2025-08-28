import os
import subprocess
from PIL import Image
from pyzbar.pyzbar import decode

# The full path to the image file containing the QR code.
image_path = input("QR Code Path: ")

def decode_qr_code_from_file(file_path):
    """
    Decodes a QR code from a specified image file.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        print("Please check the file path and try again.")
        return

    try:
        image = Image.open(file_path)
        decoded_objects = decode(image)

        if decoded_objects:
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                print("--- QR Code Found ---")
                print(f"Data: {data}")
                print(f"Type: {obj.type}")
                print("---")
        else:
            print("No QR code was found in the image. Make sure the image is clear and the QR code is not damaged.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Call the function with the path to your image
decode_qr_code_from_file(image_path)
input()
