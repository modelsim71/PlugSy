'''
Plugsy - Software Development Kit
'''

# Import libs
import os
import re
import sys
import importlib
import inspect
from .Plugin import Plugin
from .Exceptions import *
from ..Exceptions import *

class Sdk():
    '''
    SDK Class
    '''

    PLUGIN_NAME_REGEX = re.compile("^[a-zA-Z]+[a-zA-Z0-9_]*$")
    PLUGIN_NAME_MIN_LEN = 3
    PLUGIN_NAME_MAX_LEN = 35

    def __init__(self, plugins_home_path):
        '''
        Constructor
        @param plugins_home_path: The path of the plugins package directory
        '''
        # Check plugins home exists
        if not os.path.isdir(plugins_home_path):
            raise PluginsHomeNotFound(plugins_home_path)

        self.__plugins_dir_path = plugins_home_path

        # Add plugins home dir to path
        sys.path.append(plugins_home_path)


    def create_plugin(self, plugin_type, name):
        '''
        Creates a new plugin
        :return:
        '''

        # Check name
        if not self.__is_valid_plugin_name(name):
            raise BadPluginName(name)
        # Check type
        if not self.__is_valid_plugin_type(plugin_type):
            raise BadPluginType(plugin_type)


        # Initiate plugin
        new_plugin = Plugin(
            plugins_dir_path=self.__plugins_dir_path, name=name, plugin_type=plugin_type
        )

        # Create
        new_plugin.create()

        # Add new plugin package to subpackage (core, addon) __init__
        self.__add_plugin_to_init(new_plugin)


    def delete_plugin(self, name):
        '''
        Deletes an existing plugin
        @param name: The name of the plugin to delete
        '''

        # Initiate plugin and delete
        existing_plugin = Plugin(self.__plugins_dir_path, name)
        existing_plugin.delete()

        # Remove from init
        self.__remove_plugin_from_init(existing_plugin)


    def __add_plugin_to_init(self, new_plugin):
        '''
        Adds the new plugin import to the relevant subpackage
        @return:
        '''
        init_contents = ""
        subpackage_init_path = os.path.join(
            self.__plugins_dir_path,
            "core" if new_plugin.is_core_plugin() else "addon",
            "__init__.py"
        )

        # Read subpackage init
        if os.path.isfile(subpackage_init_path):
            with open(subpackage_init_path, "r") as init_file:
                init_contents = init_file.read()

        # Add new Plugin package import
        if init_contents and not init_contents.endswith("\n") and not init_contents.endswith("\r"):
            init_contents += "\nfrom . import %s" % new_plugin.get_name()
        else:
            init_contents += "from . import %s\n" % new_plugin.get_name()

        # Write init
        with open(subpackage_init_path, "w") as init_file:
            init_file.write(init_contents)


    def __remove_plugin_from_init(self, existing_plugin):
        '''
        Removes the Plugin package import from the subpackage __init__
        @param name: The name of the plugin to remove
        @return:
        '''
        subpackage_init_path = os.path.join(
            self.__plugins_dir_path,
            "core" if existing_plugin.is_core_plugin() else "addon",
            "__init__.py"
        )

        if os.path.isfile(subpackage_init_path):
            # Read subpackage init
            with open(subpackage_init_path, "r") as init_file:
                init_contents = init_file.read()

            # Remove import
            init_contents = init_contents.replace("from . import %s\n" % existing_plugin.get_name(), "")

            # Write subpackage init
            with open(subpackage_init_path, "w") as init_file:
                init_file.write(init_contents)


    def get_plugins(self):
        '''
        Fetches current plugins in plugin home
        @return: Dict of core and addon plugin lists
        '''
        plugins = {
            "core": [],
            "addon": []
        }

        # Check for core and addon folders
        plugin_subdirs = os.listdir(self.__plugins_dir_path)
        for subpackage in ["core", "addon"]:
            if subpackage in plugin_subdirs:
                subpackage_path = os.path.join(self.__plugins_dir_path, subpackage)
                subpackage_import = importlib.reload(importlib.import_module(subpackage))

                for member in inspect.getmembers(subpackage_import):
                    if inspect.ismodule(member[1]):
                        # Create object for plugin and Set type
                        plugin = Plugin(self.__plugins_dir_path, member[0], plugin_type=subpackage)

                        # Add to package plugins
                        plugins[subpackage].append(plugin)


        return plugins



    #############
    ## GETTERS ##
    #############
    def __is_valid_plugin_name(self, name):
        '''
        Validates the specified plugin name
        @param name: The name to check
        @return: True if name is valid, otherwise False
        '''

        if (
                (not self.PLUGIN_NAME_REGEX.match(name)) or
                (len(name) < self.PLUGIN_NAME_MIN_LEN) or
                (len(name) > self.PLUGIN_NAME_MAX_LEN)
        ):
            return False
        else:
            return True


    def __is_valid_plugin_type(self, plugin_type):
        '''
        Validates the plugin type
        @param plugin_type: plugin type
        @return: True if valid, else False
        '''

        if plugin_type.lower() == "core" or plugin_type.lower() == "addon":
            return True
        else:
            return False


