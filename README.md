<h1 align="center">IT Inventory API</h1>
<p align="center">API for managing IT asset inventory per employee</p>

> **Note:** For this project, a database is necessary. Be sure to have MongoDB up and running on your machine before proceeding.

## Project tree
```shell
.
├── static
    └── swagger.json
├── app.py
├── requirements.txt
└── routes.py
```

## Requirements
- Python
- MongoDB
- Flask
- Flask-Swagger-UI
- pymongo

## Getting started
### Clone the repository:
```shell
git clone https://github.com/barbara-bruzon/it-inventory
```
### Set up the MongoDB database
Create a MongoDB database and a collection to save the data. I chose to call them `it` and `inventory`, respectively.

### Creating a virtual environment (optional)
For Windows - run it in CMD:
```shell
# Create
python -m venv <env_name>

# Activate
<env_name>\Scripts\activate

# Deactivate
deactivate
```

For Linux and MacOS:
```shell
# Create
python3 -m venv <env_name>

# Activate
source <env_name>/bin/activate

# Deactivate
deactivate
```

### Install project dependencies
Run the following to install everything necessary:
```shell
pip install -r requirements.txt
```

## Executing the Python API
To execute it, just type the following command in the terminal:
```shell
pyhon app.py
```

Open ypur browser and go to [http://localhost:5000/api](http://localhost:5000/api) to access the Swagger UI and explore the API. You can also send HTTP requests via tools like cURL, Postman and Thunder Client.

## Troubleshooting
If you have any issues during setup or execution, make sure to check the following:
- Ensure MongoDB is up and running on your machine.
- The database and collection names in the script match the ones created - they should be (`it`) and (`inventory`) respectively.
- Ensure all required dependencies are installed (`pymongo`, `Flask` and `Flask-Swagger-UI`).
- Make sure you are running the commands inside the correct directories
