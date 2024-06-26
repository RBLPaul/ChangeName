from PIL import Image, PngImagePlugin
import tkinter as tk
from tkinter import filedialog
import argparse

import os
import io
import mimetypes
import shutil
import re


from dotenv import load_dotenv
# from extract_thinker.llm import LLM
# from extract_thinker import DocumentLoaderTesseract
# from extract_thinker.extractor import Extractor
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import fitz  # PyMuPDF library


load_dotenv()
cwd = os.getcwd()
from utils.llm import extract_with_gemini
   
def select_folder():
   root = tk.Tk()
   root.withdraw()
   folder = filedialog.askdirectory(master=root)
   root.destroy()
   return folder
import os


def get_files_with_type(directory):
  """
  Returns a dictionary containing file names and their MIME types.

  Args:
    directory: The path to the directory to search.

  Returns:
    A dictionary where keys are file names and values are MIME types.
  """
  files_with_types = {}
  for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if os.path.isfile(filepath):
      mime_type = mimetypes.guess_type(filepath)[0]
      files_with_types[filename] = mime_type
  return files_with_types


def copy_and_rename(source_file, destination_directory, new_filename):
    """
    Copies a file to a new directory, renaming it and replacing invalid characters.

    Args:
        source_file: The path to the original file.
        destination_directory: The path to the directory where you want to copy the file.
        new_filename: The new name you want to give the copied file.
    """
    try:
        # Handle escape sequences by replacing them with a single "!"
        # Exclude the escaped double quote (\\") from replacement
        new_filename = re.sub(r'\\(?!")', '!', new_filename)

        # Replace invalid characters (excluding parentheses) with "!"
        new_filename = re.sub(r'[^\w\s.\-()]', '!', new_filename)
        new_filename = new_filename.replace(" ", "")

        shutil.copy2(source_file, os.path.join(destination_directory, new_filename))
        print(f"File '{source_file}' copied to '{destination_directory}' as '{new_filename}' successfully.")
        return new_filename
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found.")
    except OSError as e:
        print(f"Error: Unable to copy file. {e}")
    return False


# Streamlit app
def main():
    print("ExtractThinker, Image to Text 👨‍💻 ")
    print('Made with ❤️ by Ruan')
    parser = argparse.ArgumentParser(description="Copy content from source to destination")
    parser.add_argument('-source', type=str, required=True, help='The source file path')
    parser.add_argument('-dest', type=str, required=True, help='The destination file path')

    args = parser.parse_args()

    source_folder = args.source
    dest_folder = args.dest


    file_types = get_files_with_type(source_folder)
    print(file_types)
    for filename, file_type in file_types.items():
            filename = os.path.join(source_folder, filename)
            # get image from different file formats
            if file_type == "application/pdf":
                doc = fitz.open(filename)
                for page in doc:  # iterate through the pages
                        pixmap = page.get_pixmap()  # render page to an image
                        pil_image =  Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                doc.close()
                # show the image
                # st.image(pil_image, caption=f'Uploaded {file_type}.', use_column_width=True)

                print(f"Extracting file {filename}")
                if isinstance(pil_image, PngImagePlugin.PngImageFile):
                    # Do something with the PNG image
                    print("This is a PNG image")
                else:
                    print("This is not a PNG image")

                result = extract_with_gemini(pil_image)
                print(result)
                newFileName = result['product_number'] + '(' + result['issue_date'] + ').pdf'
                result = copy_and_rename(filename, dest_folder, newFileName)
                if result:
                    print(f"Copy and Rename to {result} Sucessfully.")
                else:
                    print(f"Fail to copy and rename file {filename}.")





if __name__ == "__main__":
    main()