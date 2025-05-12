FROM ollama/ollama

# Pull the llama3 model during build
RUN ollama serve & \
    sleep 5 && \
    ollama pull llama3 && \
    pkill ollama
