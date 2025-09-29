import asyncio
import base64
import gc
import os
import shutil
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from paddleocr import PaddleOCR

from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化PaddleOCR模型（仅初始化一次）
#ocr = PaddleOCR(use_doc_orientation_classify=False,use_doc_unwarping=False,use_textline_orientation=False)
ocr = PaddleOCR(paddlex_config="config.yaml")

@app.post("/ocr_img_url")
async def ocr_endpoint(request: dict):
    image_url = request.get("image_url")
    if not image_url:
        return {"error": "未提供图片URL"}

    try:
        # 使用PaddleOCR处理图片URL
        result = ocr.predict(input=image_url)
        # 提取识别结果中的文本内容
        #texts = [line[1][0] for line in result]
        # 可视化结果并保存 json 结果

        text_list = []
        for res in result:
            rec_texts = res.get('rec_texts', [])
            text_list.extend(rec_texts)
           
        #return JSONResponse({"result": text_list},status_code=200)
        
        #return res
        #return result
        return {"text": text_list}
    except Exception as e:
        return {"error": f"识别失败: {str(e)}"}


@app.post("/ocr", response_class=JSONResponse, summary="通过图片文件以及pdf文件进行文字提取")
async def extract_text(file: UploadFile = File(...)) -> JSONResponse:
    # 记录开始时间
    start_time = time.time()
    # 分配uuid标识用于debug
    file_uuid = str(uuid.uuid4())
    try:
        # 从上传的 file 对象中读取整个文件内容，结果是二进制数据。
        file_content = await file.read()

        # 创建一个系统临时目录（路径随机，保证唯一性），用于存放接收的文件。
        temp_directory = tempfile.mkdtemp()


        # 判断文件 MIME 类型
        if file.content_type.startswith("image/"):
            print(f"标识为{file_uuid}的文件类型为图片")
            ocr_file_path = os.path.join(temp_directory, "file.png")
        elif file.content_type == "application/pdf":
            print(f"标识为{file_uuid}的文件类型为pdf")
            ocr_file_path = os.path.join(temp_directory, "file.pdf")
        else:
            print(f"标识为{file_uuid}的文件类型不受支持")
            return JSONResponse(content={"error": "不受支持的文件类型"}, status_code=400)

        # 打开目标文件，把读取的内容写到临时目录中
        with open(ocr_file_path, "wb") as f:
            f.write(file_content)
            print(f"标识为{file_uuid}的文件已经暂存至{ocr_file_path}")

    except Exception as e:
        print(f"标识为{file_uuid}的文件处理失败: {e}")
        gc.collect()
        return JSONResponse(content={"error": f"文件处理失败: {e}"}, status_code=500)

    try:
        # 进行ocr识别
        result = ocr.predict(ocr_file_path)

        # 处理ocr结果并绘制图片
        text_list = []
        image_list = []
        num = 1
        for res in result:
            rec_texts = res.get('rec_texts', [])
            text_list.extend(rec_texts)
            res.save_to_img(os.path.join(temp_directory, f"{num}.png"))
            num = num + 1
        file_names = sorted(os.listdir(temp_directory))
        for file_name in file_names:
            if file_name.endswith(".png"):
                file_path = os.path.join(temp_directory, file_name)
                with open(file_path, "rb") as f:
                    img_bytes = f.read()
                    img_b64 = "data:image/png;base64," + base64.b64encode(img_bytes).decode("utf-8")
                    image_list.append(img_b64)

        # 计算总耗时
        detail_time = time.time() - start_time
        print(f"标识为{file_uuid}的文件处理共计耗时: {detail_time}s")
        return JSONResponse({"result": text_list, "detail_time": detail_time, "image_list": image_list},
                            status_code=200)
    except Exception as e:
        print(f"标识为{file_uuid}的文件ocr识别失败: {e}")
        return JSONResponse(content={"error": f"OCR识别失败: {e}"}, status_code=500)
    finally:
        shutil.rmtree(temp_directory, ignore_errors=True)
        gc.collect()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
