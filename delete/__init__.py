import os
import time
import logging

ATTR_FILE = "file"
ATTR_FOLDER = "folder"
ATTR_TIME = "time"
ATTR_ONLY = "only_extensions"
ATTR_EXCEPT_EXT = "except_extensions"
ATTR_EXCEPT_FILE = "except_files"
ATTR_SCAN_FOLDERS = "scan_subfolders"
ATTR_DEL_FOLDERS = "remove_subfolders"

SERVICE_FILE = "file"
SERVICE_FOLDER = "files_in_folder"

DEFAULT_FILE = ""
DEFAULT_FOLDER = ""
DEFAULT_EXTENSION = []
DEFAULT_FILES = []
DEFAULT_TIME = 3600

DOMAIN = "delete"

_LOGGER = logging.getLogger(__name__)

def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    
    def _rem_file(path):
        try:
            os.remove(path)
            _LOGGER.warning("Deleted file {}".format(path))
        except Exception as ex:
            _LOGGER.error("File {} could not be deleted due to error (probably permission): {}".format(path, ex))
    
    def _rem_folder(path):
        try:
            os.rmdir(path)
            _LOGGER.warning("Deleted empty folder {}".format(path))
        except Exception as ex:
            if ex.args[0] != 39:
                _LOGGER.error("Folder {} could not be deleted due to error (probably permission): {}".format(path, ex))
            else:
                _LOGGER.info("Folder {} is not empty and cannot be deleted.".format(path))
    
    def handle_delete_file(call):
        """Handle the service call."""
        file_path = call.data.get(ATTR_FILE, DEFAULT_FILE)
    
        if file_path == DEFAULT_FILE:
            _LOGGER.error("Value of 'file' was not detected. Check the syntax of the service.")
            raise Exception("Value of 'file' was not detected. Check the syntax of the service.")
    
        if os.path.isfile(file_path):
            _rem_file(file_path)
        elif os.path.isdir(file_path):
            _rem_folder(file_path)
        else:
            _LOGGER.error("{} is not recognized as a file".format(file_path))
            raise Exception("{} is not recognized as a file".format(file_path))

    def handle_delete_files_in_folder(call):
        """Handle the service call."""
        folder_path = call.data.get(ATTR_FOLDER, DEFAULT_FOLDER)
        folder_time = call.data.get(ATTR_TIME, DEFAULT_TIME)
        exceptions = call.data.get(ATTR_EXCEPT_EXT, DEFAULT_EXTENSION)
        except_files = call.data.get(ATTR_EXCEPT_FILE, DEFAULT_FILES)
        specified = call.data.get(ATTR_ONLY, DEFAULT_EXTENSION)
        subfolders = call.data.get(ATTR_SCAN_FOLDERS, False)
        delete_folders = call.data.get(ATTR_DEL_FOLDERS, False)
        now = time.time()
        
        if folder_path == DEFAULT_FOLDER:
            _LOGGER.error("Value of 'folder' was not detected. Check the syntax of the service.")
            raise Exception("Value of 'folder' was not detected. Check the syntax of the service.")
    
        except_extensions = []
        if isinstance(exceptions, str):
            except_extensions.append(exceptions)
        elif isinstance(exceptions, list):
            except_extensions = exceptions
        
        only_extensions = []
        if isinstance(specified, str):
            only_extensions.append(specified)
        elif isinstance(specified, list):
            only_extensions = specified
        
        if only_extensions != [] and except_extensions != []:
            _LOGGER.error("Not allowed to mix extensions both only allowed and excluded")
            raise Exception("Not allowed to mix extensions both only allowed and excluded")
        
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
                                if file.endswith(extension):
                                    remove_file = True
                                    break
                        if except_extensions != []:
                            for extension in except_extensions:
                                if file.endswith(extension):
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
        
    hass.services.register(DOMAIN, SERVICE_FILE, handle_delete_file)
    hass.services.register(DOMAIN, SERVICE_FOLDER, handle_delete_files_in_folder)
    # Return boolean to indicate that initialization was successfully.
    return True