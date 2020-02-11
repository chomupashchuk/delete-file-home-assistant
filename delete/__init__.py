import os
import logging

ATTR_FILE = "file"
SERVICE = "file"
DEFAULT_FILE = ""
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
    
    hass.services.register(DOMAIN, SERVICE, handle_delete_file)
    # Return boolean to indicate that initialization was successfully.
    return True