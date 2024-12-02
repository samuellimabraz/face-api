# Use uma imagem base oficial do Python
FROM borda/docker_python-opencv-ffmpeg:cpu-py3.10-cv4.8.1


# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copie os arquivos necessários
COPY requirements.txt requirements.txt

# Instale as dependências
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir --ignore-installed -r requirements.txt

# Copie o restante do código para o container
COPY . .

# Exponha a porta que sua API usa
EXPOSE 8000

# Comando para iniciar a API
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
