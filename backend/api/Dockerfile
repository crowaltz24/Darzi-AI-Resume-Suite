FROM python:3.12.6

WORKDIR /code

RUN pip install --no-cache-dir uv
ENV VIRTUAL_ENV=/code/.venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . .
RUN uv pip install -e .

RUN uv pip install pip && python -m spacy download en_core_web_sm

ENV PORT=7860
EXPOSE $PORT

CMD ["python", "main.py"]
