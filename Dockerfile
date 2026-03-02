FROM python:3.10
USER root
WORKDIR /app
ADD ./requirements.txt /app
RUN pip install -r /app/requirements.txt
ADD . /app
EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]