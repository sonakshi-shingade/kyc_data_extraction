import pytesseract
import re
import logging
from typing import Optional, Dict
from PIL import Image 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PanCardDetails:
    """
    A class to extract PAN card details like Date of Birth (DOB) and PAN number using OCR from an image.
    """

    def __init__(self) -> None:
        """
        Initialize the Tesseract OCR executable path.
        """
        try:
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            logging.info("Tesseract OCR path configured successfully.")
        except Exception as e:
            logging.error(f"Failed to configure Tesseract OCR path: {e}")

    def extract_text(self, file: Image) -> None:
        """
        Extract text from an image using pytesseract OCR.

        Args:
            file (Image): The file path to the PAN card image.
        """
        try:
            self.text = pytesseract.image_to_string(file)
            print(self.text)
            logging.info("Text extracted successfully from image.")
        except Exception as e:
            logging.error(f"Error extracting text from image: {e}")
            self.text = ""

    def get_dob(self) -> Optional[str]:
        """
        Extract the date of birth (DOB) from the text using regular expressions.

        Returns:
            Optional[str]: The DOB if found, else None.
        """
        try:
            dob_match = re.search(r'\d{2}/\d{2}/\d{4}', self.text)
            if dob_match:
                logging.info("DOB found.")
                return dob_match.group()
            else:
                logging.warning("DOB not found in the text.")
                return None
        except Exception as e:
            logging.error(f"Error extracting DOB: {e}")
            return None

    def get_pan(self) -> Optional[str]:
        """
        Extract the PAN number from the text using regular expressions.

        Returns:
            Optional[str]: The PAN number if found, else None.
        """
        try:
            pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', self.text)
            if pan_match:
                logging.info("PAN number found.")
                return pan_match.group()
            else:
                logging.warning("PAN number not found in the text.")
                return None
        except Exception as e:
            logging.error(f"Error extracting PAN number: {e}")
            return None

    def get_pan_details(self, file: Image) -> Dict[str, Optional[str]]:
        """
        Extract both DOB and PAN number from the given PAN card image.

        Args:
            file (Image): The file path to the PAN card image.

        Returns:
            Dict[str, Optional[str]]: A dictionary containing the extracted DOB and PAN number.
        """
        try:
            self.extract_text(file)
            dob = self.get_dob()
            pan = self.get_pan()
            return {"DOB": dob, "PAN": pan}
        except Exception as e:
            logging.error(f"Failed to get PAN details: {e}")
            return {"DOB": None, "PAN": None}
