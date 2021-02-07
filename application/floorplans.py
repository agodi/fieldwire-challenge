from application import app
from flask import jsonify, request, send_file
from .helper import load_project_floorplans, load_floorplan, create_floorplan, update_floorplan, drop_floorplan, fetch_image, filepath_for_image


@app.route('/projects/<string:project_id>/floorplans', methods=['GET'])
def get_all_floorplans(project_id):
    try:
        return jsonify(load_project_floorplans(project_id)), 200
    except ValueError as e:
        return jsonify({"status": "fail", "error": str(e)}), 400


@app.route('/projects/<string:project_id>/floorplans', methods=['POST'])
def add_floorplan(project_id):
    try:
        return jsonify(create_floorplan(project_id, request.form, request.files)), 200
    except ValueError as e:
        return jsonify({"status": "fail", "error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "fail", "error": str(e)}), 500


@app.route('/projects/<string:project_id>/floorplans/<string:floorplan_id>', methods=['GET'])
def get_floorplan(project_id, floorplan_id):
    try:
        return jsonify(load_floorplan(project_id, floorplan_id)), 200
    except ValueError as e:
        return jsonify({"status": "fail", "error": str(e)}), 400


@app.route('/projects/<string:project_id>/floorplans/<string:floorplan_id>', methods=['PATCH'])
def patch_floorplan(project_id, floorplan_id):
    try:
        update_floorplan(project_id, floorplan_id, request.form, request.files)
        return jsonify({"status": "success"}), 200
    except ValueError as e:
        return jsonify({"status": "fail", "error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "fail", "error": str(e)}), 500


@app.route('/projects/<string:project_id>/floorplans/<string:floorplan_id>', methods=['DELETE'])
def delete_floorplan(project_id, floorplan_id):
    try:
        drop_floorplan(project_id, floorplan_id)
        return jsonify({"status": "success"}), 200
    except ValueError as e:
        return jsonify({"status": "fail", "error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"status": "fail", "error": str(e)}), 500


@app.route('/projects/<string:project_id>/floorplans/<string:floorplan_id>/images/<string:name>', methods=['GET'])
def get_image(project_id, floorplan_id, name):
    try:
        filepath = filepath_for_image(project_id, floorplan_id, name)
        success = fetch_image(project_id, floorplan_id, name, filepath)
        if success:
            return send_file(filepath, mimetype='image/png')
        return jsonify({"status": "fail", "error": "Can't retrieve image"}), 500
    except RuntimeError as e:
        return jsonify({"status": "fail", "error": str(e)}), 500
