import multiprocessing as mp

import tkinter as tk
import PIL
from PIL import Image, ImageTk
import cv2
import numpy as np
import logging
import time
import matplotlib.pyplot as plt
import pandas as pd

def get_latest(queue, timeout=0.1):
    start_time = time.time()
    try:
        item = queue.get(timeout=timeout)
        while True:
            try:
                elapsed_time = time.time() - start_time
                remaining_time = timeout - elapsed_time

                if remaining_time > 0:
                    next_item = queue.get(timeout=remaining_time)
                    item = next_item
                else:
                    break
            except queue.Empty:
                break
    except queue.Empty:
        item = None

    return item


class MultiDisplay(mp.Process):
    def __init__(
        self,
        queues,
        camera_names,
        display_ranges,
        display_downsample=4,
        cameras_per_row=3,
        display_size=(300, 300),
    ):
        super().__init__()
        self.pipe = None
        self.queues = queues
        self.camera_names = camera_names
        self.num_cameras = len(camera_names)
        self.downsample = display_downsample
        self.cameras_per_row = cameras_per_row
        self.display_size = display_size
        self.display_ranges = display_ranges

    def run(self):
        """Displays an image to a window."""

        root = tk.Tk()
        xdim = self.display_size[0] * self.cameras_per_row
        ydim = self.display_size[1] * int(
            np.ceil(self.num_cameras / self.cameras_per_row)
        )
        root.title("Camera view")  # this is the title of the window
        root.geometry(f"{xdim}x{ydim}")  # this is the size of the window

        rowi = 0
        labels = []
        # create a label to hold the image
        for ci, camera_name in enumerate(self.camera_names):
            # create the camera name label
            label_text = tk.Label(root, text=camera_name)
            label_text.grid(row=rowi, column=ci % self.cameras_per_row, sticky="nsew")

            # create the camerea image label
            label = tk.Label(root)  # this is where the image will go
            label.grid(row=rowi + 1, column=ci % self.cameras_per_row, sticky="nsew")

            if (ci + 1) % self.cameras_per_row == 0:
                rowi += 2

            labels.append(label)

        for i in range(self.cameras_per_row):
            root.grid_columnconfigure(i, weight=1)
        for i in range(rowi):
            root.grid_rowconfigure(i, weight=1)

        # quit the loop if an empty array is passed
        quit = False
        while True:
            # initialized checks to see if recording has started
            initialized = np.zeros(len(self.queues)).astype(bool)
            for qi, (queue, camera_name) in enumerate(zip(self.queues, self.camera_names)):
                try:
                    if queue.qsize() > 1:
                        while queue.qsize() > 1:
                            data = get_latest(queue, timeout=0.01)
                    else:
                        data = queue.get(timeout=0.01)
                except Exception as error:
                    if initialized[qi]:
                        logging.info(
                            "{}: Timeout occurred {}".format(
                                camera_name, str(error)
                            )
                        )
                    continue
                if len(data) == 0:
                    quit = True
                    break

                # retrieve frame
                if data[0] is not None:
                    initialized[qi] = True
                    frame = data[0][:: self.downsample, :: self.downsample]

                    frame = cv2.resize(frame, self.display_size)

                    # int16 should be azure data
                    if frame.dtype == np.uint16 or ("lucid" in camera_name):
                        # normalize in range
                        if self.display_ranges[qi] is not None:
                            frame = normalize_array(
                                frame,
                                min_value=self.display_ranges[qi][0],
                                max_value=self.display_ranges[qi][1],
                            ).astype(np.uint8)
                        else:
                            frame = normalize_array(frame).astype(np.uint8)

                        # Convert frame to turbo/jet colormap
                        colormap_frame = cv2.applyColorMap(frame, cv2.COLORMAP_TURBO)

                        # convert frame to PhotoImage
                        img = ImageTk.PhotoImage(
                            image=PIL.Image.fromarray(colormap_frame)
                        )
                    else:
                        # convert frame to PhotoImage
                        img = ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                    # update label with new image
                    labels[qi].config(image=img)
                    labels[qi].image = img
                else:
                    continue
                    # print(f"No data: {self.camera_names[qi]}")

            if quit:
                break
            # update tkinter window
            root.update()
        root.destroy()


def normalize_array(frame, min_value=None, max_value=None):
    if min_value is None:
        min_value = np.min(frame)
        max_value = np.max(frame)
    frame[frame > max_value] = min_value
    frame[frame < min_value] = min_value
    # frame = np.clip(frame, min_value, max_value)  # Ensure values are in the range [min_value, max_value]
    frame = (
        (frame - min_value) / (max_value - min_value)
    ) * 255.0  # Normalize to [0, 255]
    return frame.astype(np.uint8)


def plot_video_stats(csv_path, name):

    # Load the data
    df = pd.read_csv(csv_path)

    # Set up plot
    fig, axs = plt.subplots(
        ncols = 1, 
        nrows = 5, 
        gridspec_kw= {'height_ratios':[1,1,1,1,1]},
        figsize=(10,8),
        sharex=True
    )
    
    # Plot frame diffs (ie, check for dropped frames)
    axs[0].set_title(f"{name}: frame diff (dropped frames?)")
    axs[0].plot(np.diff(df.frame_id.values))

    # Plot camera timestamp diffs
    diffs = np.diff(df.frame_timestamp.values)
    axs[1].set_title(f"{name}: camera timestamp diff")
    axs[1].plot(diffs / np.median(diffs))

    # Plot computer timestamp diffs
    axs[2].set_title(f"{name}: computer timestamp (uid) diff")
    axs[2].plot(np.diff(df.frame_image_uid.values) / np.median(np.diff(df.frame_image_uid.values)))

    # Plot queue size
    axs[3].set_title(f"{name}: queue size")
    axs[3].plot(df.queue_size.values)
    axs[3].set_xlabel('Frames')
    axs[3].set_title('Queue size')

    # Plot relative occurrence of framerates
    axs[4].hist(1/(np.diff(df.frame_timestamp.values)* 1e-9), bins=100);
    axs[4].set_xlabel('Framerate')
    axs[4].set_ylabel('Count')
    axs[4].set_title(f"{name}: framerate histogram")
    
    # Format plot
    plt.tight_layout()
    plt.show()
    
    # Print some info 
    time_elapsed = (df.frame_timestamp.values[-1] - df.frame_timestamp.values[0]) * 1e-9
    avg_diffs = np.mean(diffs)
    print(f"Total time elapsed: {time_elapsed} seconds")
    print(f"Average framerate: {1 / (avg_diffs* 1e-9)} Hz")

    return