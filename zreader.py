import os
import subprocess
from PIL import Image
from pyzbar.pyzbar import decode

# The full path to the image file containing the QR code.
qrname = input("QR Name: ")
image_path = f"/storage/emulated/0/ZBucks/QR Codes/{qrname}"

# The path to your sound file
# Make sure you have a sound file in this location
# For example, you can place a file named 'beep.mp3' in your ZBucks folder
sound_path = f"/storage/emulated/0/ZBucks/Automated Programs/Extra/beep.mp3"

def play_sound():
    """
    Plays a sound file using the mpv command.
    """
    try:
        if os.path.exists(sound_path):
            # The command to play the sound file
            subprocess.run(["mpv", sound_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("Sound file not found.")
    except FileNotFoundError:
        print("Error: 'mpv' command not found. Is mpv installed?")
    except subprocess.CalledProcessError as e:
        print(f"Error playing sound: {e}")

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
            play_sound()  # Play sound if QR code is found
        else:
            print("No QR code was found in the image. Make sure the image is clear and the QR code is not damaged.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Call the function with the path to your image
decode_qr_code_from_file(image_path)