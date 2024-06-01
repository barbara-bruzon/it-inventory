from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from routes import routes

app = Flask(__name__)

# Import routes
app.register_blueprint(routes)

# Swagger configuration
SWAGGER_URL = '/api'
API_URL = '/static/swagger.json' 

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "IT Inventory" 
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)
