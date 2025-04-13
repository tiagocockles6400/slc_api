# Define a imagem base
FROM python:3.13

# Define o diret�rio de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de requisitos para o diret�rio de trabalho
COPY requirements.txt .

# Instala as depend�ncias do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o c�digo-fonte para o diret�rio de trabalho
COPY . .

# Define o comando de execu��o da API
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]