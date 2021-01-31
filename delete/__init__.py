import os
import time
import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

ATTR_FILE = "file"
ATTR_FOLDER = "folder"
ATTR_TIME = "time"
ATTR_ONLY_EXT = "only_extensions"
ATTR_EXCEPT_EXT = "except_extensions"
ATTR_EXCEPT_FILE = "except_files"
ATTR_SCAN_FOLDERS = "scan_subfolders"
ATTR_DEL_FOLDERS = "remove_subfolders"

EXCLUSIVE_GROUP = "extensions"

SERVICE_FILE = "file"
SERVICE_FOLDER = "files_in_folder"

DEFAULT_TIME = 3600

DOMAIN = "delete"

DELETE_FILE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_FILE, msg='Mandatory key "file" is missing.'): vol.Any(cv.isfile, cv.isdir),
    },
    extra=vol.ALLOW_EXTRA
)

DELETE_FILES_SCHEMA = vol.Schema(   
    {
        vol.Required(ATTR_FOLDER, msg='Mandatory key "folder" is missing.'): cv.isdir,
        vol.Optional(ATTR_TIME, default=DEFAULT_TIME): cv.positive_int,
        vol.Optional(ATTR_EXCEPT_FILE, default=[]): vol.Any(cv.ensure_list, cv.string),
        vol.Optional(ATTR_SCAN_FOLDERS, default=False): cv.boolean,
        vol.Optional(ATTR_DEL_FOLDERS, default=False): cv.boolean,
        vol.Exclusive(ATTR_ONLY_EXT, EXCLUSIVE_GROUP): vol.Any(cv.ensure_list, cv.string),
        vol.Exclusive(ATTR_EXCEPT_EXT, EXCLUSIVE_GROUP): vol.Any(cv.ensure_list, cv.string),
    },
    extra=vol.ALLOW_EXTRA
)

_LOGGER = logging.getLogger(__name__)

def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    
    def _rem_file(path):
        try:
            os.remove(path)
            _LOGGER.warning("Deleted file {}".format(path))
        except Exception as ex:
            _LOGGER.error("File {} could not be deleted due to error (probably permission): {}".format(path, ex))
    
    def _rem_folder(path, error=False):
        try:
            os.rmdir(path)
            _LOGGER.warning("Deleted empty folder {}".format(path))
        except Exception as ex:
            if ex.args[0] != 39:
                _LOGGER.error("Folder {} could not be deleted due to error (probably permission): {}".format(path, ex))
            else:
                if error:
                    _LOGGER.error("Folder {} is not empty and cannot be deleted.".format(path))
                else:
                    _LOGGER.info("Folder {} is not empty and cannot be deleted.".format(path))
    
    def handle_delete_file(call):
        """Handle the service call."""
        file_path = call.data.get(ATTR_FILE)
    
        if os.path.isfile(file_path):
            _rem_file(file_path)
        elif os.path.isdir(file_path):
            _rem_folder(file_path, error=True)
        else:
            _LOGGER.error("{} is not recognized as a file".format(file_path))
            raise Exception("{} is not recognized as a file".format(file_path))

    def handle_delete_files_in_folder(call):
        """Handle the service call."""
        folder_path = call.data.get(ATTR_FOLDER)
        folder_time = call.data.get(ATTR_TIME)
        except_extensions = call.data.get(ATTR_EXCEPT_EXT)
        except_files = call.data.get(ATTR_EXCEPT_FILE)
        only_extensions = call.data.get(ATTR_ONLY_EXT)
        subfolders = call.data.get(ATTR_SCAN_FOLDERS)
        delete_folders = call.data.get(ATTR_DEL_FOLDERS)
        
        if type(except_files) is str:
            except_files = list(except_files)
        
        if not except_extensions:
            except_extensions = list()
        
        if not only_extensions:
            only_extensions = list()
        
        if type(except_extensions) is str:
            except_extensions = list(except_extensions)
        
        if type(only_extensions) is str:
            only_extensions = list(only_extensions)
        
        now = time.time()
        
        # if only_extensions != [] and except_extensions != []:
        #     _LOGGER.error("Not allowed to mix allowed and excluded extensions.")
        #     raise Exception("Not allowed to mix allowed and excluded extensions.")
        
        if os.path.isdir(folder_path):
        
            for instance_path, instance_dirs, instance_files in os.walk(folder_path, topdown=False):
            
                if not subfolders and instance_path != folder_path:
                    continue
                    
                for file in instance_files:
                    file_path = os.path.join(instance_path, file)
                    if os.stat(file_path).st_mtime < now - folder_time:
                        remove_file = True
                        if only_extensions != []:
                            remove_file = False
                            for extension in only_extensions:
                                if file.lower().endswith(extension.lower()):
                                    remove_file = True
                                    break
                        if except_extensions != []:
                            for extension in except_extensions:
                                if file.lower().endswith(extension.lower()):
                                    remove_file = False
                                    break
                        if except_files != []:
                            if file in except_files:
                                remove_file = False
                        if remove_file:
                            _rem_file(file_path)
                  
                if delete_folders:                  
                    for subfolder in instance_dirs:
                        subfolder_path = os.path.join(instance_path, subfolder)
                        #if os.stat(subfolder_path).st_mtime < now - folder_time:
                        _rem_folder(subfolder_path)
        
        else:
            _LOGGER.error("{} is not recognized as a folder".format(folder_path))
            raise Exception("{} is not recognized as a folder".format(folder_path))
        
    hass.services.register(DOMAIN, SERVICE_FILE, handle_delete_file, schema=DELETE_FILE_SCHEMA)
    hass.services.register(DOMAIN, SERVICE_FOLDER, handle_delete_files_in_folder, schema=DELETE_FILES_SCHEMA)
    # Return boolean to indicate that initialization was successful.
    return True