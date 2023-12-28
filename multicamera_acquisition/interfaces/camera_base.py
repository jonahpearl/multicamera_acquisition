import numpy as np
import yaml

class CameraError(Exception):
    pass


class BaseCamera(object):
    """
    A class used to encapsulate a Camera.
    Attributes
    ----------
    cam : PySpin Camera
    running : bool
        True if acquiring images
    camera_attributes : dictionary
        Contains links to all of the camera nodes which are settable
        attributes.
    camera_methods : dictionary
        Contains links to all of the camera nodes which are executable
        functions.
    camera_node_types : dictionary
        Contains the type (as a string) of each camera node.
    lock : bool
        If True, attribute access is locked down; after the camera iacquisition_loopss
        initialized, attempts to set new attributes will raise an error.  This
        is to prevent setting misspelled attributes, which would otherwise
        silently fail to acheive their intended goal.
    intialized : bool
        If True, init() has been called.
    In addition, many more virtual attributes are created to allow access to
    the camera properties.  A list of available names can be found as the keys
    of `camera_attributes` dictionary, and a documentation file for a specific
    camera can be genereated with the `document` method.
    Methods
    -------
    init()
        Initializes the camera.  Automatically called if the camera is opened
        using a `with` clause.
    close()
        Closes the camera and cleans up.  Automatically called if the camera
        is opening using a `with` clause.
    start()
        Start recording images.
    stop()
        Stop recording images.
    get_image()
        Return an image using PySpin's internal format.
    get_array()
        Return an image as a Numpy array.
    get_info(node)
        Return info about a camera node (an attribute or method).
    document()
        Create a Markdown documentation file with info about all camera
        attributes and methods.
    """

    def __init__(self, index=0, config_file=None):
        """Create a camera instance connected to a camera, without actually "open"ing it (i.e. without starting the connection).
        Parameters
        ----------
        index : int or str (default: 0)
            If an int, the index of the camera to acquire.  If a string,
            the serial number of the camera.
        config : path-like str or Path (default: None)
            Path to config file. If None, uses the camera's default config file.
        """
        self.index = index
        self.config_file = config_file

    def save_config(self):
        """Save the current camera configuration to a YAML file.
        """
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def load_config(self, check_if_valid=False):
        """Load a camera configuration YAML file.
        """
        with open(self.config_file, 'r') as f:
            config = yaml.load(f)
        self.config = config

        if check_if_valid:
            self.check_config()

    def update_config(self, new_config):
        """Update the config file.

        Parameters
        ----------
        new_config: dict
            Dictionary of new config values
        """
        def recursive_update(config, updates):
            for key, value in updates.items():
                if key in config and isinstance(config[key], dict):
                    # If the key is a dictionary, recurse
                    recursive_update(config[key], value)
                else:
                    # Otherwise, update the value directly
                    config[key] = value
            return config
        
        tmp_config = recursive_update(self.config, new_config)
        if self.check_config(tmp_config):
            self.config = tmp_config
            self.save_config()

    def check_config(self, config=None):
        """Check if the camera configuration is valid.
        """
        pass  # defined in each camera subclass

    def init(self):
        """Initializes the camera.  Automatically called if the camera is opened
        using a `with` clause."""
        raise NotImplementedError

    def __enter__(self):
        self.init()
        return self

    def close(self):
        """Closes the camera and cleans up.  Automatically called if the camera
        is opening using a `with` clause."""

        self.stop()
        del self.cam
        self.camera_attributes = {}
        self.camera_methods = {}
        self.camera_node_types = {}
        self.initialized = False
        # self.system.ReleaseInstance()

    def __exit__(self, type, value, traceback):
        self.close()

    def start(self):
        "Start recording images."
        raise NotImplementedError

    def stop(self):
        "Stop recording images."
        raise NotImplementedError

    def get_image(self, timeout=None):
        raise NotImplementedError

    def get_array(self, timeout=None, get_chunk=False, get_timestamp=False):
        """Get an image from the camera, and convert it to a numpy array.
        Parameters
        ----------
        timeout : int (default: None)
            Wait up to timeout milliseconds for an image if not None.
                Otherwise, wait indefinitely.
        get_timestamp : bool (default: False)
            If True, returns timestamp of frame f(camera timestamp)
        Returns
        -------
        img : Numpy array
        tstamp : int
        """
        raise NotImplementedError

    # def __getattr__(self, attr):
    #    '''Get the value of a camera attribute or method.'''
    #    raise NotImplementedError

    # def __setattr__(self, attr, val):
    #    '''Set the value of a camera attribute.'''
    #    raise NotImplementedError

    def get_info(self, name):
        """Gen information on a camera node (attribute or method).
        Parameters
        ----------
        name : string
            The name of the desired node
        Returns
        -------
        info : dict
            A dictionary of retrieved properties.  *Possible* keys include:
                - `'access'`: read/write access of node.
                - `'description'`: description of node.
                - `'value'`: the current value.
                - `'unit'`: the unit of the value (as a string).
                - `'min'` and `'max'`: the min/max value.
        """
        raise NotImplementedError

    def document(self):
        """Creates a MarkDown documentation string for the camera."""
        raise NotImplementedError

