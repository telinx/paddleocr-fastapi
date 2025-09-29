from paddleocr import PaddleOCR

class PaddleOCRService:
    def __init__(self):
        # 初始化PaddleOCR模型，使用GPU
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=True)

    def predict(self, image_bytes):
        # 进行OCR预测
        result = self.ocr.ocr(image_bytes, cls=True)
        return result

