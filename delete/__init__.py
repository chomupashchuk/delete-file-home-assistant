import os
import time
import logging

ATTR_FILE = "file"
ATTR_FOLDER = "folder"
ATTR_TIME = "time"
ATTR_ONLY = "only_extensions"
ATTR_EXCEPT = "except_extensions"
SERVICE_FILE = "file"
SERVICE_FOLDER = "files_in_folder"
DEFAULT_FILE = ""
DEFAULT_FOLDER = ""
DEFAULT_EXTENSION = []
DEFAULT_TIME = 3600
DOMAIN = "delete"

_LOGGER = logging.getLogger(__name__)

def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    
    def handle_delete_file(call):
        """Handle the service call."""
        file_path = call.data.get(ATTR_FILE, DEFAULT_FILE)
    
        if os.path.isfile(file_path):
            os.remove(file_path)
            _LOGGER.warning("Deleted {}".format(file_path))
        else:
            _LOGGER.info("{} is not a file".format(file_path))
            raise

    def handle_delete_files_in_folder(call):
        """Handle the service call."""
        folder_path = call.data.get(ATTR_FOLDER, DEFAULT_FOLDER)
        folder_time = call.data.get(ATTR_TIME, DEFAULT_TIME)
        exceptions = call.data.get(ATTR_EXCEPT, DEFAULT_EXTENSION)
        specified = call.data.get(ATTR_ONLY, DEFAULT_EXTENSION)
        now = time.time()
        
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
            _LOGGER.info("Not allowed to mix extensions both only allowed and excluded")
            raise
        
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.stat(file_path).st_mtime < now - folder_time:
                    if os.path.isfile(file_path):
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
                        if remove_file:
                            _LOGGER.warning("Deleted {}".format(file_path))
                            os.remove(file_path)
        else:
            _LOGGER.info("{} is not a folder".format(folder_path))
            raise
        
    hass.services.register(DOMAIN, SERVICE_FILE, handle_delete_file)
    hass.services.register(DOMAIN, SERVICE_FOLDER, handle_delete_files_in_folder)
    # Return boolean to indicate that initialization was successfully.
    return True