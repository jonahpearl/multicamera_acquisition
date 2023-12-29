# TODO
# - camera specific code (e.g. setting ain for basler) doesn't need to be in this file
# - there is no reason these parameters should be set in init file, we should move this 
#   to the init of the camera instead... 


# define the base camera

import numpy as np
import struct


def get_camera(
    brand="flir",
    index=0,
    config_file=None,
):
    """Get a camera object.
    Parameters
    ----------
    brand : string (default: 'flir')
        The brand of camera to use.  Currently only 'flir' is supported. If
        'flir', the software PySpin is used. if 'basler', the software pypylon
        is used.
    index : int or str (default: 0)
            If an int, the index of the camera to acquire.  
            If a string, the serial number of the camera.
    config_file : string (default: None)
        Path to a config file.  If None, the default config file for the given
        camera brand will be used.

    Returns
    -------
    cam : Camera object
        The camera object, specific to the brand.

    """
    if brand == "flir":
        from multicamera_acquisition.interfaces.camera_flir import FlirCamera as Camera

        cam = Camera(index=str(index))

        cam.init()

        # # set gain
        # cam.GainAuto = "Off"
        # cam.Gain = gain

        # # set exposure
        # cam.ExposureAuto = "Off"
        # cam.ExposureTime = exposure_time

        # # set trigger
        # if trigger == "arduino":
        #     # TODO - many of these settings are not related to the trigger and should
        #     # be redistributed
        #     # TODO - remove hardcoding
        #     cam.AcquisitionMode = "Continuous"
        #     cam.AcquisitionFrameRateEnable = True
        #     max_fps = cam.get_info("AcquisitionFrameRate")["max"]
        #     cam.AcquisitionFrameRate = max_fps
        #     cam.TriggerMode = "Off"
        #     cam.TriggerSource = trigger_line
        #     cam.TriggerOverlap = "ReadOut"
        #     cam.TriggerSelector = "FrameStart"
        #     cam.TriggerActivation = "RisingEdge"
        #     # cam.TriggerActivation = "FallingEdge"
        #     cam.TriggerMode = "On"

        # else:
        #     cam.LineSelector = trigger_line
        #     cam.AcquisitionMode = "Continuous"
        #     cam.TriggerMode = "Off"
        #     cam.TriggerSource = "Software"
        #     cam.V3_3Enable = True
        #     cam.TriggerOverlap = "ReadOut"

        # if roi is not None:
        #     raise NotImplementedError("ROI not implemented for FLIR cameras")

    elif brand == "basler":
        from multicamera_acquisition.interfaces.camera_basler import (
            BaslerCamera as Camera,
        )

        cam = Camera(index=index, config_file=config_file)
        cam.init()

    elif brand == "basler_emulated":
        from multicamera_acquisition.interfaces.camera_basler import (
            EmulatedBaslerCamera as Camera,
        )
        cam = Camera()
        cam.init()

        # set gain
        # cam.cam.GainAuto.SetValue("Off")
        # cam.cam.Gain.SetValue(gain)

        # # set exposure time
        # cam.cam.ExposureAuto.SetValue("Off")
        # cam.cam.ExposureTime.SetValue(exposure_time)

        # # set readout mode
        # # cam.cam.SensorReadoutMode.SetValue(readout_mode)

        # # set roi
        # if roi is not None:
        #     cam.cam.Width.SetValue(roi[2])
        #     cam.cam.Height.SetValue(roi[3])
        #     cam.cam.OffsetX.SetValue(roi[0])
        #     cam.cam.OffsetY.SetValue(roi[1])

    elif brand == "azure":
        from multicamera_acquisition.interfaces.camera_azure import (
            AzureCamera as Camera,
        )

        if "name" in kwargs:
            name = kwargs["name"]
        else:
            raise ValueError("Azure camera requires name")

        cam = Camera(
            serial_number=str(serial), name=name, azure_index=kwargs["azure_index"]
        )


    elif brand == 'lucid':
        from multicamera_acquisition.interfaces.camera_lucid import (
            LucidCamera as Camera,
        )
        cam = Camera(
            index=str(serial)
        )
        cam.init()

    return cam
