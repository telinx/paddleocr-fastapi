# paddleocr-fastapi

```
sudo docker build -t  paddleocr-fastapi:3.0.3 .

docker run --gpus all  -v /usr/lib/x86_64-linux-gnu/:/usr/lib/x86_64-linux-gnu/  -p 8100:8000 paddleocr-fastapi:3.0.3 

docker run --gpus all  -p 8100:8000 paddleocr-fastapi:3.0.3 

post http://xxx.xx.xx.xx:8000/ocr_img_url
{
    "image_url": ""
}

```