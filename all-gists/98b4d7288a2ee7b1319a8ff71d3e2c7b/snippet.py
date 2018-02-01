import io
import math
from difflib import SequenceMatcher

from google.oauth2 import service_account
from google.cloud import vision as GoogleVision
from google.cloud.vision import types as GoogleTypes

from PIL import Image, ImageSequence


class GifCaptionExtractor(object):

    def __init__(self):
        self.client = self.get_api_client()

    def get_api_client(self):
        """Creates a scoped session for Google Cloud Vision"""
        creds_json_path = '/path/to/google/account/creds.json'
        creds = service_account.Credentials.from_service_account_file(creds_json_path)
        scoped_credentials = creds.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
        client = GoogleVision.ImageAnnotatorClient(credentials=scoped_credentials)
        return client

    def get_gif_frames(self, path):
        """Returns percentage of a GIF's frames as local file paths"""
        frame_percentage = .25
        frame_paths = []
        im = Image.open(path)
        frame_count = 0
        image_name = path.split('.')[0]
        for frame in ImageSequence.Iterator(im):
            frame_path = image_name + "-%s.gif" % frame_count
            frame.save(frame_path)
            frame_paths.append(frame_path)
            frame_count += 1
        denominator = math.floor(frame_count * frame_percentage)
        frames_to_check = [path for idx, path in enumerate(frame_paths) if idx % denominator == 0]
        frames_to_check.append(frame_paths[-1])
        return frames_to_check

    def get_ocr_data(self, path):
        """Queries Google Cloud Vision OCR endpoint and returns normalized text string"""
        with io.open(path, 'rb') as image_file:
            content = image_file.read()
            img_obj = GoogleTypes.Image(content=content)
            img_results = self.client.text_detection(image=img_obj)
            # google text annotations returns lots of things, but we only want description
            # https://cloud.google.com/vision/docs/detecting-text#vision-text-detection-python
            return img_results.text_annotations[0].description.lower().strip().replace('\n', ' ')

    def get_caption_data(self, gif_path):
        """Returns caption data from a GIF"""
        frame_paths = self.get_gif_frames(gif_path)
        caption_data = []
        gif_caption = self.get_ocr_data(frame_paths[0])
        frame_paths.pop(0)
        if not gif_caption:
            return ''
        caption_data.append(gif_caption)
        for idx, path in enumerate(frame_paths):
            frame_text_results = self.get_ocr_data(path)
            if frame_text_results:
                frame_caption_text = frame_text_results
                prev_caption_text = caption_data[-1]
                text_similarity = SequenceMatcher(None, prev_caption_text, frame_caption_text).ratio()
                if text_similarity < .60:
                    caption_data.append(frame_caption_text)
        return caption_data


if __name__ == "__main__":
    gif_path = "/path/to/example.gif"
    caption_extractor = GifCaptionExtractor()
    caption = caption_extractor.get_caption_data(gif_path)
    print(" ".join([words for words in caption]))