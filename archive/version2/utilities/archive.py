#!/usr/bin/python
import topy
from config import projects_path, archive_path

def archive(projects_list, archive_list):
    save_projects = False
    if isinstance(projects_list, str):
        projects_list = topy.from_file(projects_path)
        save_projects = True

    save_archive = False
    if isinstance(archive_list, str):
        archive_list = topy.from_file(archive_path)
        save_archive = True

    topy.archive(projects_list, archive_list)

    if save_projects:
        projects_list.to_file(projects_path)
    if save_archive:
        archive_list.to_file(archive_list)

    return projects_list, archive_list

if __name__ == '__main__':
    archive(projects_path, archive_path)
