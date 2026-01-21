FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime 

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]



