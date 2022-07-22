FROM serge3006/deepstream-python-bindings:0.0.1

# Add app and install runtime dependencies
COPY . /app
WORKDIR /app

RUN python3 -m pip install -r /app/requirements.txt

#CMD ["python3", "/app/main.py"]