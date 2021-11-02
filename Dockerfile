FROM python:3.8.10

WORKDIR /app

RUN apt update -y && apt install libopenmpi-dev -y

# Those are commented because we want to test that everything works with minimal install
# COPY requirements.txt requirements.txt
# RUN pip3 install -r requirements.txt

COPY . .

# To be in a sandbox
CMD ["bash"]