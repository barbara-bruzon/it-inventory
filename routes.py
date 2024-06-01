from flask import Blueprint, jsonify, request
import pymongo

routes = Blueprint('routes', __name__)

# Connection parameters
conn_uri = "mongodb://localhost:27017/"
db_name = "it"

ALLOWED_ASSETS = {'notebook', 'desktop', 'monitor1', 'monitor2', 'keyboard', 'mouse', 'nobreak', 'headset', 'cellphone', 'accessories'}

# Connect to MongoDB
try:
    conn_mongo = pymongo.MongoClient(conn_uri)
    collection_mongo = conn_mongo[db_name]["inventory"]
except Exception as error:
    print("An error has occurred while connecting to MongoDB: ", error)

# Default values for the assets
def get_default_values(asset_type):
    default_values = {}
    if asset_type == 'notebook':
        default_values = {'tag': 'Uninformed', 'model': 'Uninformed', 'serial_number': 'Uninformed',
                        'version': 'Uninformed', 'characteristics': 'Uninformed', 'observation': 'Uninformed'}
    elif asset_type == 'desktop':
        default_values = {'tag': 'Uninformed', 'model': 'Uninformed', 'serial_number': 'Uninformed',
                        'version': 'Uninformed', 'characteristics': 'Uninformed', 'observation': 'Uninformed'}
    elif asset_type.startswith('monitor'):
        default_values = {'model': 'Uninformed', 'serial_number': 'Uninformed', 'observation': 'Uninformed'}
    elif asset_type == 'keyboard':
        default_values = {'model': 'Uninformed', 'serial_number': 'Uninformed', 'observation': 'Uninformed'}
    elif asset_type == 'mouse':
        default_values = {'model': 'Uninformed', 'serial_number': 'Uninformed', 'observation': 'Uninformed'}
    elif asset_type == 'nobreak':
        default_values = {'model': 'Uninformed', 'serial_number': 'Uninformed', 'observation': 'Uninformed'}
    elif asset_type == 'headset':
        default_values = {'model': 'Uninformed', 'serial_number': 'Uninformed', 'observation': 'Uninformed'}
    elif asset_type == 'cellphone':
        default_values = {'model': 'Uninformed', 'imei1': 'Uninformed', 'number': 'Uninformed', 'observation': 'Uninformed'}
    elif asset_type == 'accessories':
        default_values = {'notebook_support': False, 'mousepad': False}

    return default_values

#### BEGIN - employee routes ####

# Insert an employee
@routes.route('/employee', methods=['POST'])
def insert_employee():
    try:
        data = request.json
        cpf = data.get('cpf', '')
        name = data.get('name', '')

        if len(cpf) != 11:
            return jsonify({'message': 'CPF must have 11 digits'}), 400

        if not name:
            return jsonify({'message': 'Name cannot be empty'}), 400

        # Checks if there is any unwanted attribute
        invalid_keys = set(data.keys()) - {'cpf', 'name'}
        if invalid_keys:
            return jsonify({'message': f'Invalid keys provided: {", ".join(invalid_keys)}'}), 400

        employee_data = {
            '_id': cpf,
            'name': name
        }

        collection_mongo.insert_one(employee_data)
        return jsonify({'message': f'Employee {name} inserted successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

# List all employees
@routes.route('/employee', methods=['GET'])
def list_employees():
    try:
        employees = list(collection_mongo.find({}, {'_id': 1, 'name': 1, 'assets': 1}))
        return jsonify(employees), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

# Retrieve employee's inventory
@routes.route('/employee/<cpf>', methods=['GET'])
def employee_inventory(cpf):
    try:
        if len(cpf) != 11:
            return jsonify({'message': 'CPF must have 11 digits'}), 400
        
        result = collection_mongo.find_one({'_id': cpf})
        if not result:
            return jsonify({'message': 'Employee not found'}), 404

        # Retorna apenas os assets do funcionário
        return jsonify({'assets': result.get('assets', [])}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

# Update employee's name
@routes.route('/employee/<cpf>', methods=['PUT'])
def update_employee(cpf):
    try:
        data = request.json
        name = data.get('name', '')

        if len(cpf) != 11:
            return jsonify({'message': 'CPF must have 11 digits'}), 400

        if not name:
            return jsonify({'message': 'Name cannot be empty'}), 400

        result = collection_mongo.update_one({'_id': cpf}, {'$set': {'name': name}})
        if result.matched_count == 0:
            return jsonify({'message': 'Employee not found'}), 404

        return jsonify({'message': 'Employee name updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

# Delete an employee
@routes.route('/employee/<cpf>', methods=['DELETE'])
def delete_employee(cpf):
    try:
        if len(cpf) != 11:
            return jsonify({'message': 'CPF must have 11 digits'}), 400

        result = collection_mongo.delete_one({'_id': cpf})
        if result.deleted_count == 0:
            return jsonify({'message': 'Employee not found'}), 404

        return jsonify({'message': f'Employee {cpf} deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

#### END - employee routes ####



#### BEGIN - assets routes ####

# Insert assets for an employee
@routes.route('/employee/<cpf>/asset', methods=['POST'])
def insert_employee_assets(cpf):
    try:
        data = request.json
        assets = data

        if not assets:
            return jsonify({'message': 'At least one asset must be provided'}), 400
        
        if len(cpf) != 11:
            return jsonify({'message': 'CPF must have 11 digits'}), 400

        # Check if the provided asset is allowed
        invalid_assets = [asset_type for asset_type in assets.keys() if asset_type not in ALLOWED_ASSETS]
        if invalid_assets:
            return jsonify({'message': f'Invalid asset types: {", ".join(invalid_assets)}'}), 400
        
        invalid_attributes = {}
        for asset_type, asset_info in assets.items():
            # Get the default values
            default_values = get_default_values(asset_type)

            # Checks if there is any unwanted attribute
            invalid_attrs = [attr for attr in asset_info.keys() if attr not in default_values.keys()]
            if invalid_attrs:
                invalid_attributes[asset_type] = invalid_attrs
            
            # Checks whether accessory attributes values ​​are boolean
            if asset_type == 'accessories':
                for attr, value in asset_info.items():
                    if attr in default_values.keys() and type(value) is not bool:
                        invalid_attributes.setdefault(asset_type, []).append(attr)

        if invalid_attributes:
            error_message = {
                'message': 'Invalid attributes for the following assets:',
                'invalid_attributes': invalid_attributes
            }
            return jsonify(error_message), 400

        # Check if the employee already has this asset
        existing_assets = collection_mongo.find_one({'_id': cpf})
        if existing_assets:
            existing_assets = existing_assets.get('assets', {})
            for asset_type in assets.keys():
                if asset_type in existing_assets:
                    return jsonify({'message': f'Asset {asset_type} already exists for this employee'}), 400

        for asset_type, asset_info in assets.items():
            default_values = get_default_values(asset_type)
            # Apply default values if necessary
            for key, value in default_values.items():
                if key not in asset_info:
                    asset_info[key] = value

            update_fields = {'$set': {f'assets.{asset_type}': asset_info}}
            collection_mongo.update_one({'_id': cpf}, update_fields, upsert=True)

        return jsonify({'message': 'Assets inserted successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

# Update asset for an employee
@routes.route('/employee/<cpf>/asset/<asset>', methods=['PUT'])
def update_employee_asset(cpf, asset):
    try:
        data = request.json
        if not data:
            return jsonify({'message': 'No data provided for update'}), 400
        
        if len(cpf) != 11:
            return jsonify({'message': 'CPF must have 11 digits'}), 400

        # Checks if the employee exists
        employee = collection_mongo.find_one({'_id': cpf})
        if not employee:
            return jsonify({'message': 'Employee not found'}), 404

        # Checks if the employee has this asset
        assets = employee.get('assets', {})
        if asset not in assets:
            return jsonify({'message': f'Asset {asset} not found for this employee'}), 404

        # Checks if there is any unwanted attribute
        default_values = get_default_values(asset)
        invalid_attributes = [attr for attr in data.keys() if attr not in default_values]
        if invalid_attributes:
            return jsonify({'message': f'Invalid attributes for asset {asset}: {", ".join(invalid_attributes)}'}), 400

        # Update given fields
        update_fields = {'$set': {f'assets.{asset}.{key}': value for key, value in data.items()}}
        collection_mongo.update_one({'_id': cpf}, update_fields)

        return jsonify({'message': f'Asset {asset} information updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

# Delete asset for an employee
@routes.route('/employee/<cpf>/asset/<asset>', methods=['DELETE'])
def delete_employee_asset(cpf, asset):
    try:
        if len(cpf) != 11:
            return jsonify({'message': 'CPF must have 11 digits'}), 400
        
        employee = collection_mongo.find_one({'_id': cpf})
        if not employee:
            return jsonify({'message': 'Employee not found'}), 404

        if asset not in employee.get('assets', {}):
            return jsonify({'message': 'Asset not found'}), 404

        # Exclui o asset apenas se ele existir
        result = collection_mongo.update_one({'_id': cpf}, {'$unset': {f'assets.{asset}': ""}})
        if result.modified_count == 0:
            return jsonify({'message': 'Failed to delete asset'}), 500

        return jsonify({'message': f'Asset {asset} deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

# Transfer asset from an employee to another
@routes.route('/employee/<source_cpf>/transfer/<target_cpf>/asset/<asset_type>', methods=['POST'])
def transfer_asset(source_cpf, target_cpf, asset_type):
    try:
        if len(source_cpf) != 11:
            return jsonify({'message': 'Source CPF must have 11 digits'}), 400
        
        if len(target_cpf) != 11:
            return jsonify({'message': 'Target CPF must have 11 digits'}), 400
        
        if asset_type not in ALLOWED_ASSETS:
            return jsonify({'message': 'Invalid asset type'}), 400

        # Checks if the employees exists
        source_employee = collection_mongo.find_one({'_id': source_cpf})
        target_employee = collection_mongo.find_one({'_id': target_cpf})

        if not source_employee:
            return jsonify({'message': 'Source employee not found'}), 404
        if not target_employee:
            return jsonify({'message': 'Target employee not found'}), 404

        # Checks if the source employee has this asset
        source_assets = source_employee.get('assets', {})
        if asset_type not in source_assets:
            return jsonify({'message': f'Source employee does not have asset {asset_type}'}), 400

        # Checks if the target employee has this asset
        target_assets = target_employee.get('assets', {})
        if asset_type in target_assets:
            return jsonify({'message': f'Target employee already has asset {asset_type}'}), 400

        # Transfer the asset
        asset_data = source_assets.pop(asset_type)
        collection_mongo.update_one({'_id': source_cpf}, {'$set': {'assets': source_assets}})
        collection_mongo.update_one({'_id': target_cpf}, {'$set': {f'assets.{asset_type}': asset_data}})

        return jsonify({'message': f'Asset {asset_type} transferred from {source_cpf} to {target_cpf} successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


#### END - assets routes ####