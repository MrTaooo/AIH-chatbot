# AIH-chatbot

1. Build the Docker image
`docker build -t ai-chatbot .`

2. Run the Docker container
`docker run -it --restart always --name AIH-chatbot --env-file .env ai-chatbot`