from application import app
from json import loads
from PIL import Image
import os

project_fields = ["name"]
floorplan_fields = ["name", "original"]
projects_storage = {}
floorplans_storage = {}
project_counter = 0
upload_folder = app.config["UPLOAD_FOLDER"]


def load_all_projects():
    projects = []

    for project in projects_storage.values():
        projects.append(project)

    return projects


def load_project(project_id):
    if project_id not in projects_storage:
        raise ValueError("No project associated to id: {}".format(project_id))
    return projects_storage[project_id]


def add_project(request_data):
    data = loads(request_data)
    if not all(field in data for field in project_fields):
        raise AttributeError("Missing project attributes in request")

    project = {}
    for field in project_fields:
        project[field] = data[field]

    project_id = str(new_project_id())
    project["id"] = project_id
    project["floorplans"] = []

    projects_storage[project_id] = project

    return str(project_id)


def update_project(project_id, request_data):
    data = loads(request_data)

    project = load_project(project_id)

    if not all(field in project_fields for field in data):
        raise AttributeError("Unknown project attributes in request")

    for field in data:
        project[field] = data[field]

    return True


def drop_project(project_id):
    if project_id not in projects_storage:
        raise ValueError("No project associated to id: {}".format(project_id))

    if project_id in floorplans_storage:
        for floorplan in floorplans_storage[project_id].values():
            delete_files(floorplan)
        del floorplans_storage[project_id]
    del projects_storage[project_id]

    return True


def load_project_floorplans(project_id):
    if project_id not in projects_storage:
        raise ValueError("No project associated to id: {}".format(project_id))

    floorplans = []
    if project_id in floorplans_storage:
        for floorplan in floorplans_storage[project_id].values():
            floorplans.append(floorplan)
    return floorplans


def load_floorplan(project_id, floorplan_id):
    if project_id not in projects_storage:
        raise ValueError("No project associated to id: {}".format(project_id))

    if project_id not in floorplans_storage or floorplan_id not in floorplans_storage[project_id]:
        raise ValueError("Project {} has no floorplan with id: {}".format(project_id, floorplan_id))

    return floorplans_storage[project_id][floorplan_id]


def create_floorplan(project_id, data, request_files):
    project = load_project(project_id)
    floorplan_id = str(len(project["floorplans"]) + 1)
    file = request_files["file"]
    filename = file.filename
    name = data["name"] if "name" in data else None

    filepath = os.path.join(upload_folder, "{}_{}_{}".format(project_id, floorplan_id, filename))
    floorplan = new_floorplan(project_id, floorplan_id, name, filename)
    project["floorplans"].append(new_floorplan_resource(project_id, floorplan_id))
    if project_id not in floorplans_storage:
        floorplans_storage[project_id] = {}
    floorplans_storage[project_id][floorplan_id] = floorplan

    store_files(floorplan, filepath, file)

    return floorplan


def store_files(floorplan, filepath, file):
    if os.path.exists(filepath):
        raise ValueError("A file with the given name already exists for the same project")
    file.save(filepath)
    thumbnail = Image.open(file).resize((100, 100))
    large = Image.open(file).resize((2000, 2000))

    thumb = filepath_from_resource_path(floorplan["project_id"], floorplan["id"], floorplan["thumb"])
    poster = filepath_from_resource_path(floorplan["project_id"], floorplan["id"], floorplan["large"])

    thumbnail.save(thumb)
    large.save(poster)


def update_floorplan(project_id, floorplan_id, data, request_files):
    floorplan = load_floorplan(project_id, floorplan_id)

    if not all(field in floorplan_fields for field in data):
        raise AttributeError("Unknown floorplan attributes in request")

    for field in data:
        floorplan[field] = data[field]

    if "file" in request_files:
        delete_files(floorplan)
        update_images(floorplan,  request_files)

    return True


def update_images(floorplan, request_files):
    project_id = floorplan["project_id"]
    floorplan_id = floorplan["id"]
    file = request_files["file"]
    filename = file.filename
    name = filename[:filename.rfind(".")]
    extension = filename[filename.rfind("."):]
    thumb_filename = "{}_thumb{}".format(name, extension)
    large_filename = "{}_large{}".format(name, extension)
    filepath = os.path.join(upload_folder, "{}_{}_{}".format(project_id, floorplan_id, filename))
    floorplan["original"] = image_resource_path(project_id, floorplan_id, filename)
    floorplan["thumb"] = image_resource_path(project_id, floorplan_id, thumb_filename)
    floorplan["large"] = image_resource_path(project_id, floorplan_id, large_filename)
    store_files(floorplan, filepath, file)


def drop_floorplan(project_id, floorplan_id):
    floorplan = load_floorplan(project_id, floorplan_id)

    delete_files(floorplan)
    del floorplans_storage[project_id][floorplan_id]

    return True


def new_project_id():
    global project_counter
    project_counter += 1
    return project_counter


def new_floorplan_resource(project_id, floorplan_id):
    return {"id": floorplan_id, "resource_path": "/projects/{}/floorplans/{}".format(project_id, floorplan_id)}


def new_floorplan(project_id, floorplan_id, name, filename):
    if not name:
        name = filename[:filename.rfind(".")]
    extension = filename[filename.rfind("."):]
    thumb_filename = "{}_thumb{}".format(name, extension)
    large_filename = "{}_large{}".format(name, extension)

    return {
        "id": floorplan_id,
        "name": name,
        "project_id": project_id,
        "original": image_resource_path(project_id, floorplan_id, filename),
        "thumb": image_resource_path(project_id, floorplan_id, thumb_filename),
        "large": image_resource_path(project_id, floorplan_id, large_filename),
    }


def image_resource_path(project_id, floorplan_id, filename):
    return "/images/{}/{}/{}".format(project_id, floorplan_id, filename)


def delete_files(floorplan):
    project_id = floorplan["project_id"]
    floorplan_id = floorplan["id"]

    files = [
        filepath_from_resource_path(project_id, floorplan_id, floorplan["original"]),
        filepath_from_resource_path(project_id, floorplan_id, floorplan["thumb"]),
        filepath_from_resource_path(project_id, floorplan_id, floorplan["large"])
    ]

    for file in files:
        if os.path.exists(file):
            os.remove(file)


def filepath_from_resource_path(project_id, floorplan_id, resource_path):
    return os.path.join(
        upload_folder,
        "{}_{}_{}".format(project_id, floorplan_id, resource_path[resource_path.rfind("/")+1:]))


def fetch_image(project_id, floorplan_id, name):
    filepath = os.path.join(upload_folder, "{}_{}_{}".format(project_id, floorplan_id, name))

    return filepath
