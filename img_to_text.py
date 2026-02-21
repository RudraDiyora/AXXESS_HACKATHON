import pytesseract
import os 
import enum
import sys
class OS(enum.Enum):
    Mac = 0 
    Windows = 1
class ImageReader: 
    def __init__(self, os: OS):
        if os == OS.Mac:
            print("running on Mac\n")    #this is since tesseract works differently on mac and windows

        if os == OS.Windows:
            windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe" 
            pytesseract.pytesseract.tesseract_cmd = windows_path
            print("running on Windows\n")

    def extract_resume_data(self, pdf_path):
        from PIL import Image, ImageEnhance
        img = Image.open(pdf_path)
        img = img.convert('L')
        
        enhancer = ImageEnhance.Contrast(img)          # Enhance Contrast to Make the blacks blacker and whites whiter
        img = enhancer.enhance(1.5) # Increase contrast by 1.5x
        sharpness_enhancer = ImageEnhance.Sharpness(img)   #increases the sharpness
        img = sharpness_enhancer.enhance(1.2)
        img = img.point(lambda x: 0 if x < 100 else 255, '1')          # Any pixel darker than 100 becomes 0 (black), others become 255 (white) to make the library more accurate

        text = pytesseract.image_to_string(img)
        print(text)
        return text
    
if __name__ == "__main__":
    resume_path = input("enter the path to the image file : ")  #getting input from user
    if not os.path.exists(resume_path):  #checking if the file path is valid
        print("File not found.")
        sys.exit(1)

    reader = ImageReader(OS.Windows)
    text = reader.extract_resume_data(resume_path)  #extracting text from pdf
    