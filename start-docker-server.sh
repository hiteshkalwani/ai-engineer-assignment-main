# we will use this file to start the docker server
# and test your application.
# please do not modify this file or any relevant files
# unless you know what you are doing.
if [ ! -f .env ]; then
    echo "Please create a .env file, see .env.example for reference"
    exit 1
fi
export IMAGE_NAME=code-snipper
docker build -t $IMAGE_NAME .

# Run the Docker container with the Docker socket mounted
docker run --rm -p 8000:8000 --env-file .env -v /var/run/docker.sock:/var/run/docker.sock $IMAGE_NAME
