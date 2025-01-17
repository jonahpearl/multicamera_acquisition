import unittest, shutil
import os
import tempfile
from pathlib import Path
import logging
from pypylon import pylon
import multiprocessing as mp
from datetime import datetime, timedelta

from multicamera_acquisition.tests.interfaces.test_camera_basler import PylonEmuTestCase
from multicamera_acquisition.acquisition import AcquisitionLoop, end_processes, Writer
from multicamera_acquisition.paths import ensure_dir

class EmulatedBaslerTestCase(unittest.TestCase):

    def setUp(self):
        
        # Parameters for an emulated basler
        self.camera_dict = {
            "brand": "basler_emulated",
            "name": "emulated",  # shouldnt be required
            "gpu": 0,  # shouldnt be required
            "gain": 0,
            "exposure_time": 1000,
            "trigger": "software",
            "frame_timeout": 1000,
            "roi": None,
            "readout_mode": "SensorReadoutMode_Normal",
        }
        
        self.ffmpeg_options = {"fps": 90, "gpu": 0}

        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_acquire_no_arduino(self):
        """Test acquiring images without an arduino"""

        vid_path = Path(f"{self.test_dir}/test_vid.mp4")
        metadata_path = Path(f"{self.test_dir}/metadata.csv")

        # Set up the writer
        write_queue = mp.Queue()
        writer = Writer(
            queue=write_queue,
            video_file_name=vid_path,
            metadata_file_name=metadata_path,
            camera_serial="emulated",
            fps=90,
            camera_name="emulated",
            camera_brand=self.camera_dict["brand"],
            ffmpeg_options=self.ffmpeg_options
        )

        # Set up the emulated camera
        acquisition_loop = AcquisitionLoop(
            write_queue=write_queue,
            display_queue=None,
            **self.camera_dict,
        )

        acquisition_loop.prime()

        # Start the acquisition
        writer.start()
        acquisition_loop.start()

        # Wait for a few seconds while it goes
        recording_duration_s = 2
        datetime_prev = datetime.now()
        endtime = datetime_prev + timedelta(seconds=recording_duration_s + 0.5)
        while datetime.now() < endtime:
            pass
        
        # End the acquisition loop
        end_processes([acquisition_loop], [writer], None, writer_timeout=3)

        # Check that the video was saved
        self.assertTrue(vid_path.exists())

        # Check that the video is more than 0 B
        self.assertTrue(vid_path.stat().st_size > 0)

        # Check that the metadata was saved
        self.assertTrue(metadata_path.exists())

        # Check that the metadata has more rows than just the header
        with open(metadata_path, "r") as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 1)