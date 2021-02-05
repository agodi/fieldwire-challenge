from application import app
from flask import jsonify, request
from .helper import load_all_projects, load_project, add_project, update_project, drop_project


@app.route('/projects', methods=['GET'])
def read_all_projects():
    try:
        projects = load_all_projects()
        return jsonify(projects), 200
    except RuntimeError as e:
        return jsonify({"status": "fail", "error": str(e)}), 500


@app.route('/projects', methods=['POST'])
def create_project():
    try:
        project_id = add_project(request.data)
        return jsonify({"status": "success", "project_id": project_id}), 200
    except (ValueError, AttributeError) as e:
        return jsonify({"status": "fail", "error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "fail", "error": str(e)}), 500


@app.route('/projects/<string:project_id>', methods=['GET'])
def read_project(project_id):
    try:
        project = load_project(project_id)
        return jsonify(project), 200
    except ValueError as e:
        return jsonify({"status": "fail", "error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "fail", "error": str(e)}), 500


@app.route('/projects/<string:project_id>', methods=['PATCH'])
def patch_project(project_id):
    try:
        update_project(project_id, request.data)
        return jsonify({"status": "success"}), 200
    except AttributeError as e:
        return jsonify({"status": "fail", "error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "fail", "error": str(e)}), 500


@app.route('/projects/<string:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        drop_project(project_id)
        return jsonify({"status": "success"}), 200
    except ValueError as e:
        return jsonify({"status": "fail", "error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "fail", "error": str(e)}), 500
