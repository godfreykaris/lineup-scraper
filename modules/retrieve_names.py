import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import pillow_avif
import re
import pandas as pd
import modules.shared as shared

class ImageProcessor:
    def __init__(self, tesseract_location):
        pytesseract.pytesseract.tesseract_cmd = tesseract_location

    def preprocess_image(self, image_path):
        avif_image = Image.open(image_path)
        enhancer = ImageEnhance.Contrast(avif_image)
        contrast_image = enhancer.enhance(2.2)
        grayscale_image = contrast_image.convert('L')
        threshold_global = 235
        binarized_image_global = grayscale_image.point(lambda p: p > threshold_global and 255)
        bottom_center_height = 50
        bottom_center_region = (
            0, avif_image.height - bottom_center_height, avif_image.width, avif_image.height
        )
        bottom_center_image = avif_image.crop(bottom_center_region)
        enhancer_bottom = ImageEnhance.Contrast(bottom_center_image)
        contrast_bottom = enhancer_bottom.enhance(2.5)
        grayscale_bottom = contrast_bottom.convert('L')
        threshold_bottom = 210
        binarized_bottom = grayscale_bottom.point(lambda p: p > threshold_bottom and 255)
        binarized_image = ImageOps.invert(binarized_image_global)
        binarized_image.paste(binarized_bottom, (0, avif_image.height - bottom_center_height))
        return binarized_image

    def extract_text(self, image):
        extracted_text = pytesseract.image_to_string(image, config='--psm 6 -l eng --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
        return extracted_text

    def extract_names(self, text):
        names = re.findall(r'\b[A-Za-z]+\b', text)
        return names

    def filter_names(self, names):
        filtered_names = []
        prev_name = None

        for i, name in enumerate(names):
            if i == len(names) - 1:
                continue
            name = re.sub(r'[^A-Za-z]', '', name)
            if len(name) < 3:
                continue
            modified_name = []
            prev_char = ''
            consecutive_count = 0
            for char in name:
                if char == prev_char:
                    consecutive_count += 1
                    if consecutive_count <= 2:
                        modified_name.append(char)
                else:
                    consecutive_count = 1
                    modified_name.append(char)
                prev_char = char
            filtered_name = ''.join(modified_name).strip()
            if re.match(r'^(\w)\1*$', name, re.IGNORECASE):
                continue
            if filtered_name == prev_name:
                continue
            filtered_names.append(filtered_name)
            prev_name = filtered_name
        return filtered_names

    def process_image_and_extract_names(self, image_path, team_name):
        processed_image = self.preprocess_image(image_path)
        extracted_text = self.extract_text(processed_image)
        names = self.extract_names(extracted_text)
        filtered_names = self.filter_names(names)
        df = pd.DataFrame(filtered_names, columns=[team_name])
        
        return df

if __name__ == "__main__":
    tesseract_location = shared.tesseract_location
    image_processor = ImageProcessor(tesseract_location)
    image_path = '../lineup.avif'
    image_processor.process_image_and_extract_names(image_path,"arsenal")
