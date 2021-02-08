from application import app
from flask import jsonify, request
from .helper import load_all_projects, load_project, add_project, update_project, drop_project, api_response


@app.route('/projects', methods=['GET'])
def read_all_projects():
    try:
        projects = load_all_projects()
        return jsonify(api_response(status="success", data=projects)), 200
    except (ValueError, AttributeError, RuntimeError) as e:
        return jsonify(api_response(status="fail", error=str(e))), 500


@app.route('/projects', methods=['POST'])
def create_project():
    try:
        project_resource = add_project(request.data)
        return jsonify(api_response(status="success", data=project_resource)), 200
    except (ValueError, AttributeError, RuntimeError) as e:
        return jsonify(api_response(status="fail", error=str(e))), 500


@app.route('/projects/<string:project_id>', methods=['GET'])
def read_project(project_id):
    try:
        project = load_project(project_id)
        return jsonify(api_response(status="success", data=project)), 200
    except (ValueError, AttributeError, RuntimeError) as e:
        return jsonify(api_response(status="fail", error=str(e))), 500


@app.route('/projects/<string:project_id>', methods=['PATCH'])
def patch_project(project_id):
    try:
        update_project(project_id, request.data)
        return jsonify(api_response(status="success")), 200
    except (ValueError, AttributeError, RuntimeError) as e:
        return jsonify(api_response(status="fail", error=str(e))), 500


@app.route('/projects/<string:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        drop_project(project_id)
        return jsonify(api_response(status="success")), 200
    except (ValueError, AttributeError, RuntimeError) as e:
        return jsonify(api_response(status="fail", error=str(e))), 500

