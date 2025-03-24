FROM python:3.10

RUN pip install --upgrade pip
RUN pip install python-lsp-server

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src

# CMD ["fastapi", "run", "--proxy-headers","--port", "80", "app/main.py"]
ENTRYPOINT ["uvicorn"]
CMD ["src.main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]
