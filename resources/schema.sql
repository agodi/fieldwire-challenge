CREATE DATABASE IF NOT EXISTS fieldwire;

USE fieldwire;

CREATE TABLE IF NOT EXISTS project (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name CHAR(50) NOT NULL,
    floorplan_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS floorplan (
    id INT NOT NULL,
    project_id INT NOT NULL,
    name CHAR(50) NOT NULL,
    original_resource_url CHAR(150) NOT NULL,
    thumb_resource_url CHAR(150) NOT NULL,
    large_resource_url CHAR(150) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id, project_id),
    CONSTRAINT `fk_floorplan_project`
        FOREIGN KEY (project_id) REFERENCES project (id)
        ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS floorplan_image (
    id INT NOT NULL,
    project_id INT NOT NULL,
    original_image LONGBLOB NOT NULL,
    thumb_image BLOB NOT NULL,
    large_image MEDIUMBLOB NOT NULL,
    CONSTRAINT `fk_floorplan_image`
        FOREIGN KEY (id, project_id) REFERENCES floorplan (id, project_id)
        ON DELETE CASCADE
) ENGINE = InnoDB;
