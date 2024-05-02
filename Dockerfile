FROM python:3.9
COPY . chatarena-werewolf
RUN pip install --upgrade pip
RUN pip install chatarena
RUN pip install git+https://github.com/chatarena/chatarena
RUN pip install chatarena[all_backends]
RUN pip install chatarena[all_envs]
RUN pip install chatarena[all]
RUN pip install --no-cache-dir gradio==4.28.3
RUN pip install chatarena[gradio]
EXPOSE 8080
ENV GRADIO_SERVER_NAME="0.0.0.0"
WORKDIR /chatarena-werewolf
CMD ["python3" , "app.py" ]