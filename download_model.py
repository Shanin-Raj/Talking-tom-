import urllib.request
import zipfile
import os
import sys

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
ZIP_PATH = "vosk-model.zip"
EXTRACT_PATH = "model"

def main():
    if os.path.exists(EXTRACT_PATH):
        print("Model already exists.")
        return

    print(f"Downloading model from {MODEL_URL} (this may take a minute) ...")
    
    # Progress hook
    def reporthook(blocknum, blocksize, totalsize):
        readso_far = blocknum * blocksize
        if totalsize > 0:
            percent = readso_far * 1e2 / totalsize
            sys.stdout.write(f"\rDownloading: {percent:.1f}%")
            sys.stdout.flush()

    urllib.request.urlretrieve(MODEL_URL, ZIP_PATH, reporthook)
    print("\nDownload complete! Extracting...")
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(".")
    
    # Rename extracted folder to 'model'
    extracted_folder = "vosk-model-small-en-us-0.15"
    if os.path.exists(extracted_folder):
        os.rename(extracted_folder, EXTRACT_PATH)
        
    print("Cleaning up zip file...")
    os.remove(ZIP_PATH)
    print("Done! Model is ready in the 'model' folder.")

if __name__ == "__main__":
    main()
