import configparser
import os

from jinja2 import Template


def get_rpath(name, path):
    rpath = os.path.join(path, name)
    if os.path.exists(rpath):
        return os.path.relpath(rpath)


def includes():
    pass


config = configparser.ConfigParser()
config.read('config.ini')
project_name = config.get("Project", "name")
sdk_path = config.get("Project", 'sdk_path')
get_rpath('integration', sdk_path)
includes = list()
includes.append('../config')
include_str = config.get("c_user_include_directories", "list")
for dir_name in include_str.split():
    includes.append(get_rpath(dir_name, sdk_path).replace('\\', '/'))
c_user_include_directories = ';'.join(includes)
c_preprocessor_definitions = config.get("c_preprocessor_definitions", "list").replace('\n', ';')[1:]
with open('template.project') as f:
    tmp = f.read()
template = Template(tmp)

# add main.c and config/sdk_config.h
folders = dict()
for i in range(1, 10):
    folder = 'folder{}'.format(i)
    if folder in config:
        folder_name = config.get(folder, "name")
        folder_list = config.get(folder, "list")
        folder_content = list()
        for item in folder_list.split():
            try:
                folder_content.append(
                    get_rpath(item, sdk_path).replace('\\', '/'))
            except AttributeError as e:
                pass
        folders[folder_name] = folder_content
folders['Application'] = ['../main.c', '../config/sdk_config.h']
output = template.render(name=project_name, c_user_include_directories=c_user_include_directories, folders=folders,
                         sdk_path=get_rpath('', sdk_path).replace('\\', '/'),
                         c_preprocessor_definitions=c_preprocessor_definitions)

with open("{}.emProject".format(project_name), "w") as fh:
    fh.write(output)
