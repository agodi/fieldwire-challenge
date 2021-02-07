class Project:
    def __init__(self, id, name, created_at, last_modified_at, floorplans_ids):
        self.id = id
        self.name = name
        if created_at:
            self.created_at = created_at
        if last_modified_at:
            self.last_modified_at = last_modified_at
        if floorplans_ids:
            self.floorplans = self.transform_floorplans_ids(floorplans_ids)

    def transform_floorplans_ids(self, floorplans_ids):
        floorplans = []
        for floorplan_id in floorplans_ids:
            floorplans.append(
                {
                    "id": floorplan_id[0],
                    "resource_path": "/projects/{}/floorplans/{}".format(self.id, floorplan_id[0])
                })
        return floorplans


class Floorplan:
    def __init__(self, id, project_id, name, original_resource_url, thumb_resource_url,
                 large_resource_url, created_at, last_modified_at):
        self.id = id
        self.name = name
        self.project_id = project_id
        self.thumb_resource_url = thumb_resource_url
        self.large_resource_url = large_resource_url
        self.original_resource_url = original_resource_url
        if created_at:
            self.created_at = created_at
        if last_modified_at:
            self.last_modified_at = last_modified_at
