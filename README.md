# flask_task
Task REST API in Flask, deployable on Azure

A basic REST API endpoint with authentication and authorization

Hosted on [Azure](https://flask-tasks-twvmz7gf2c5ce-app-service.azurewebsites.net/apidocs/)
# Dev environment
## Prerequisit
In order to use the provided dev containter, ensure that you have installed the official "dev containers" extention for VSCode. You can find it by searching for "dev containers" in the extension marketplace in VSCode. It's the one by Microsoft. 

Next, make sure that you have installed docker and have it running on your machine. You can find instructions for your operating system [on the official site](https://docs.docker.com/engine/install/).

## Setting up the .devcontainer
Now that you have Docker running and the devcontainers plugin installted, create an `.env` file in the `.devcontainer` folder. Use the `.env_example` as an example for what the file should contain. 

After this, restart VSCode. You should get a pop-up asking you if you would like to start the dev container. Click yes and wait for the environment to load. All dependencies should be automatically installed and VSCode should have selected the correct interperter.

## Local venv and requirements
Alternatively you could use a local virtual environment and `pip install -r requirements.txt` to have the Flask API working on a localhost. Set the configuration to testing to use a SQLite database.

# Azure
This project can be deployed to azure using `azd`
In the root run `azd up` to set up the resource group in your subscription
Afterwards you can use `azd deploy` to update the code running on App Service

# unittests
To run the unittests, have a virtualenvironment or devcontainer set up and run `python -m unittest tests.test_task` in the root to run the test.
These will use the testing configuration and the SQLite database
