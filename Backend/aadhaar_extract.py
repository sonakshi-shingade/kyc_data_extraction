import pytesseract
import re
import logging 
from typing import Optional, Dict
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AadhaarCardDetails:
    """
    A class to extract Aadhaar card details like Name, DOB, Gender, Aadhaar Number, and Father's Name using OCR from an image.
    """

    def __init__(self) -> None:
        try:
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            logging.info("Tesseract OCR path configured successfully.")
        except Exception as e:
            logging.error(f"Failed to configure Tesseract OCR path: {e}")

    def extract_text(self, file: Image) -> None:
        try:
            self.text = pytesseract.image_to_string(file)
            # print(self.text)  # Optional: For debugging
            logging.info("Text extracted successfully from image.")

        except Exception as e:
            logging.error(f"Error extracting text from image: {e}")
            self.text = ""

    def get_name(self) -> Optional[str]:
        try:
            # Aadhaar cards usually start with the name near the top
            lines = self.text.splitlines()
            lines = [line.strip() for line in lines if line.strip()]
            for line in lines:
                if re.search(r'^[A-Z][a-zA-Z\s]+$', line) and 'Government' not in line:
                    return line
            return None
        except Exception as e:
            logging.error(f"Error extracting Name: {e}")
            return None

    def get_dob(self) -> Optional[str]:
        try:
            dob_match = re.search(r'\d{2}/\d{2}/\d{4}', self.text)
            if dob_match:
                return dob_match.group()
            # Some Aadhaar cards use "Year of Birth: YYYY"
            yob_match = re.search(r'Year of Birth[:\s]+(\d{4})', self.text)
            if yob_match:
                return yob_match.group(1)   
            return None
        except Exception as e:
            logging.error(f"Error extracting DOB: {e}")
            return None

    def get_gender(self) -> Optional[str]:
        try:
            if re.search(r'\bMale\b', self.text, re.IGNORECASE):
                return "Male"
            elif re.search(r'\bFemale\b', self.text, re.IGNORECASE):
                return "Female"
            elif re.search(r'\bTransgender\b', self.text, re.IGNORECASE):
                return "Transgender"
            return ""
        except Exception as e:
            logging.error(f"Error extracting Gender: {e}")
            return ""

    def get_aadhaar_number(self) -> Optional[str]:
        try:
            # Aadhaar is a 12-digit number, sometimes written with spaces
            aadhaar_match = re.search(r'(\d{4}\s\d{4}\s\d{4})', self.text)
            if aadhaar_match:
                return aadhaar_match.group().replace(" ", "")
            return None
        except Exception as e:
            logging.error(f"Error extracting Aadhaar Number: {e}")
            return None

    def get_father_name(self) -> Optional[str]:
        try:
            # Look for guardian/father phrases in English
            match = re.search(r'(S/O|D/O|C/O)\s*[:\-]?\s*([A-Za-z\s]+)', self.text, re.IGNORECASE)
            if match:
                return match.group(2).strip()
            return ""
        except Exception as e:
            logging.error(f"Error extracting Father’s Name: {e}")
            return ""

    def get_aadhaar_details(self, file: Image) -> Dict[str, Optional[str]]:
        try:
            self.extract_text(file)
            return {
                "Name": self.get_name(),
                "DOB": self.get_dob(),
                "Gender": self.get_gender(),
                "Aadhaar_Number": self.get_aadhaar_number()
            }
        except Exception as e:
            logging.error(f"Failed to get Aadhaar details: {e}")
            return {
                "Name": "",
                "DOB": "",
                "Gender": "",
                "Aadhaar_Number": "",
                "Father's Name": ""
            }
