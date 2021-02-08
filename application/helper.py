from application import app, sql_conn
from json import loads
from .models import Project, Floorplan
from PIL import Image
import os


project_fields = ["name"]
floorplan_fields = ["name", "original"]
upload_folder = app.config["UPLOAD_FOLDER"]

select_all_projects = """SELECT id, name, floorplan_count, created_at, last_modified_at FROM project"""
select_project = """SELECT id, name, floorplan_count, created_at, last_modified_at FROM project WHERE id = %s"""
select_project_floorplan_counter = """SELECT floorplan_count FROM project WHERE id = %s"""
insert_project = """INSERT INTO project (name) values (%s)"""
update_project_name = """UPDATE project SET name = %s WHERE  id = %s"""
update_project_floorplan_counter = """UPDATE project SET floorplan_count = %s WHERE id = %s"""
delete_project = """DELETE FROM project WHERE id = %s"""

select_floorplan = """SELECT id, project_id, name, original_resource_url, thumb_resource_url,
                    large_resource_url, created_at, last_modified_at FROM floorplan WHERE id = %s AND project_id = %s"""
select_project_floorplans_ids = """SELECT id FROM floorplan WHERE project_id = %s"""
insert_floorplan = """INSERT INTO floorplan (id, project_id, name, original_resource_url, thumb_resource_url, 
                    large_resource_url) VALUES (%s, %s, %s, %s, %s, %s)"""
update_floorplan_name = """UPDATE floorplan SET name = %s WHERE id = %s AND project_id = %s"""
update_floorplan_resources = """UPDATE floorplan SET original_resource_url = %s, thumb_resource_url = %s, large_resource_url = %s 
                                WHERE id = %s AND project_id = %s"""
delete_floorplan = """DELETE FROM floorplan WHERE id = %s AND project_id = %s"""

select_original_image = """SELECT original_image FROM floorplan_image WHERE id = %s AND project_id = %s"""
select_thumb_image = """SELECT thumb_image FROM floorplan_image WHERE id = %s AND project_id = %s"""
select_large_image = """SELECT large_image FROM floorplan_image WHERE id = %s AND project_id = %s"""
insert_image = """INSERT INTO floorplan_image (id, project_id, original_image, thumb_image, large_image) 
                    VALUES (%s, %s, %s, %s, %s)"""
update_image = """UPDATE floorplan_image SET original_image = %s, thumb_image = %s, large_image = %s 
                    WHERE id = %s AND project_id = %s"""


def load_all_projects():
    projects = []
    cursor = sql_conn.cursor()
    cursor.execute(select_all_projects)
    resultset = cursor.fetchall()
    cursor.close()

    for result in resultset:
        floorplans_ids = load_floorplans_ids(result[0])
        projects.append(Project(result[0], result[1], result[3], result[4], floorplans_ids))

    return projects


def load_floorplans_ids(project_id):
    floorplans = []
    cursor = sql_conn.cursor()

    cursor.execute(select_project_floorplans_ids, (project_id,))
    for floorplan_id in cursor:
        floorplans.append(floorplan_id)
    cursor.close()

    return floorplans


def load_project(project_id):
    cursor = sql_conn.cursor()
    cursor.execute(select_project, (project_id,))

    resultset = cursor.fetchone()
    cursor.close()

    if not resultset:
        raise ValueError("No project associated to id: {}".format(project_id))

    floorplans_ids = load_floorplans_ids(resultset[0])

    return Project(resultset[0], resultset[1], resultset[3], resultset[4], floorplans_ids)


def add_project(request_data):
    data = loads(request_data)
    if not all(field in data for field in project_fields):
        raise AttributeError("Missing project attributes in request")

    cursor = sql_conn.cursor()
    cursor.execute(insert_project, (data["name"],))
    sql_conn.commit()
    cursor.close()

    return new_project_resource(cursor.lastrowid)


def update_project(project_id, request_data):
    data = loads(request_data)

    project = load_project(project_id)

    if not all(field in project_fields for field in data):
        raise AttributeError("Unknown project attributes in request")

    cursor = sql_conn.cursor()
    cursor.execute(update_project_name, (data["name"], project.id))
    sql_conn.commit()
    cursor.close()

    return True


def drop_project(project_id):
    project = load_project(project_id)

    cursor = sql_conn.cursor()
    cursor.execute(delete_project, (project.id, ))
    sql_conn.commit()
    cursor.close()

    return True


def load_project_floorplans(project_id):
    project = load_project(project_id)

    floorplans_ids = load_floorplans_ids(project.id)
    floorplans = []

    for floorplan_id in floorplans_ids:
        floorplans.append(load_floorplan(project.id, floorplan_id[0]))

    return floorplans


def load_floorplan(project_id, floorplan_id):
    project = load_project(project_id)

    return load_floorplan_details(project.id, floorplan_id)


def load_floorplan_details(project_id, floorplan_id):
    cursor = sql_conn.cursor()
    cursor.execute(select_floorplan, (floorplan_id, project_id))

    resultset = cursor.fetchone()
    cursor.close()

    if not resultset:
        raise ValueError("Project {} has no floorplan with id: {}".format(project_id, floorplan_id))

    return Floorplan(
        resultset[0],
        resultset[1],
        resultset[2],
        resultset[3],
        resultset[4],
        resultset[5],
        resultset[6],
        resultset[7])


def create_floorplan(project_id, data, request_files):
    project = load_project(project_id)
    floorplan_id = get_last_floorplan_id(project.id) + 1
    file = request_files["file"]
    filename = file.filename
    name = data["name"] if "name" in data else None

    floorplan = new_floorplan(project_id, floorplan_id, name, filename, None, None)
    insert_new_floorplan(floorplan)
    add_floorplan_to_project(floorplan_id, project.id)
    insert_floorplan_images(file, filename, floorplan.id, project.id)
    sql_conn.commit()

    return new_floorplan_resource(project_id, floorplan_id)


def insert_new_floorplan(floorplan):
    floorplan_cursor = sql_conn.cursor()
    floorplan_cursor.execute(insert_floorplan,
                             (floorplan.id,
                              floorplan.project_id,
                              floorplan.name,
                              floorplan.original_resource_url,
                              floorplan.thumb_resource_url,
                              floorplan.large_resource_url))
    floorplan_cursor.close()


def add_floorplan_to_project(floorplan_id, project_id):
    project_cursor = sql_conn.cursor()
    project_cursor.execute(update_project_floorplan_counter, (floorplan_id, project_id))
    project_cursor.close()


def insert_floorplan_images(file, filename, floorplan_id, project_id):
    store_temporary_images(file, filename)

    image_cursor = sql_conn.cursor()

    original = open(filename, "rb")
    thumb = open("{}_{}".format("thumb", filename), "rb")
    large = open("{}_{}".format("large", filename), "rb")

    image_cursor.execute(insert_image, (floorplan_id, project_id, original.read(), thumb.read(), large.read()))

    original.close()
    thumb.close()
    large.close()
    image_cursor.close()
    delete_temporary_images(filename)


def get_last_floorplan_id(project_id):
    cursor = sql_conn.cursor()
    cursor.execute(select_project_floorplan_counter, (project_id,))
    last_id = cursor.fetchone()
    cursor.close()

    return last_id[0]


def update_floorplan(project_id, floorplan_id, data, request_files):
    floorplan = load_floorplan(project_id, floorplan_id)

    if not all(field in floorplan_fields for field in data):
        raise AttributeError("Unknown floorplan attributes in request")

    if "name" in data:
        update_floorplan_name_field(data["name"], floorplan.id, floorplan.project_id)

    if "file" in request_files:
        update_floorplan_images(request_files["file"], floorplan.id, floorplan.project_id)

    sql_conn.commit()

    return True


def update_floorplan_name_field(name, floorplan_id, project_id):
    cursor = sql_conn.cursor()
    cursor.execute(update_floorplan_name, (name, floorplan_id, project_id))
    cursor.close()


def update_floorplan_images(file, floorplan_id, project_id):
    filename = file.filename
    name = filename[:filename.rfind(".")]
    extension = filename[filename.rfind("."):]
    thumb_filename = "{}_thumb{}".format(name, extension)
    large_filename = "{}_large{}".format(name, extension)
    store_temporary_images(file, filename)

    original = open(filename, "rb")
    thumb = open("{}_{}".format("thumb", filename), "rb")
    large = open("{}_{}".format("large", filename), "rb")

    image_cursor = sql_conn.cursor()
    image_cursor.execute(update_image, (original.read(), thumb.read(), large.read(), floorplan_id, project_id))

    original.close()
    thumb.close()
    large.close()
    image_cursor.close()
    delete_temporary_images(filename)

    resource_cursor = sql_conn.cursor()
    resource_cursor.execute(
        update_floorplan_resources,
        (image_resource_path(project_id, floorplan_id, filename),
         image_resource_path(project_id, floorplan_id, thumb_filename),
         image_resource_path(project_id, floorplan_id, large_filename),
         floorplan_id,
         project_id))
    resource_cursor.close()


def drop_floorplan(project_id, floorplan_id):
    floorplan = load_floorplan(project_id, floorplan_id)

    cursor = sql_conn.cursor()
    cursor.execute(delete_floorplan, (floorplan.id, floorplan.project_id))
    sql_conn.commit()
    cursor.close()

    return True


def fetch_image(project_id, floorplan_id, name, filepath):
    floorplan = load_floorplan(project_id, floorplan_id)

    if name not in floorplan.original_resource_url \
        and name not in floorplan.thumb_resource_url \
        and name not in floorplan.large_resource_url:
        print(name, floorplan.original_resource_url, floorplan.thumb_resource_url, floorplan.large_resource_url)
        raise ValueError("A file with the given name doesn't exists for the given project and floorplan")

    query = select_original_image
    if "thumb" in name:
        query = select_thumb_image
    elif "large"in name:
        query = select_large_image

    cursor = sql_conn.cursor()
    cursor.execute(query, (floorplan.id, floorplan.project_id))
    image_data = cursor.fetchone()
    cursor.close()

    with open(filepath, "wb+") as f:
        f.write(image_data[0])

    return True


def new_floorplan_resource(project_id, floorplan_id):
    return {"id": floorplan_id, "resource_path": "/projects/{}/floorplans/{}".format(project_id, floorplan_id)}


def new_project_resource(project_id):
    return {"id": project_id, "resource_path": "/projects/{}".format(project_id)}


def new_floorplan(project_id, floorplan_id, name, filename, created_at, last_modified_at):
    if not name:
        name = filename[:filename.rfind(".")]
    extension = filename[filename.rfind("."):]
    thumb_filename = "{}_thumb{}".format(name, extension)
    large_filename = "{}_large{}".format(name, extension)

    return Floorplan(
        floorplan_id,
        project_id,
        name,
        image_resource_path(project_id, floorplan_id, filename),
        image_resource_path(project_id, floorplan_id, thumb_filename),
        image_resource_path(project_id, floorplan_id, large_filename),
        created_at,
        last_modified_at)


def image_resource_path(project_id, floorplan_id, filename):
    return "/projects/{}/floorplans/{}/images/{}".format(project_id, floorplan_id, filename)


def filepath_for_image(project_id, floorplan_id, name):
    return os.path.join(upload_folder, "{}_{}_{}".format(project_id, floorplan_id, name))


def store_temporary_images(file, filename):
    file.save(filename)
    Image.open(filename).resize((100, 100)).save("{}_{}".format("thumb", filename))
    Image.open(filename).resize((2000, 2000)).save("{}_{}".format("large", filename))


def delete_temporary_images(filename):
    os.remove(filename)
    os.remove("{}_{}".format("thumb", filename))
    os.remove("{}_{}".format("large", filename))


def api_response(status, data=None, error=None):
    response = {
            "status" : status,
        }

    if data:
        response["data"] = data
    elif error:
        response["error"] = error

    return {
        "response" : response
    }