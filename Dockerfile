# 使用支持CUDA的PaddlePaddle镜像作为基础镜像 docker pull paddlepaddle/paddle:3.2.0-gpu-cuda12.6-cudnn9.5
#FROM registry.baidubce.com/paddlepaddle/paddle:3.2.0-gpu-cuda12.6-cudnn9.5
FROM ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddle:3.2.0-gpu-cuda11.8-cudnn8.9

# 设置工作目录
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    # && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到工作目录
COPY . .

# 暴露端口
EXPOSE 8000

# 启动FastAPI应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

