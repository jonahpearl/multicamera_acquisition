import numpy as np
import csv
import timewizard.perievent as tw
import pandas as pd

import pdb


def generate_test_file(path, num_cycles):
    INTER_BARCODE_INTERVAL = 5000  # Total time between barcode initiation (includes initialization pulses) in milliseconds. The length of time between one barcode and the next
    BARCODE_TIME = 30  # time for each bit of the barcode to be on/off in milliseconds
    BARCODE_BITS = 32  # number of bits in the barcode
    INITIALIZATION_TIME = 15  # We warp the beginning and ending of the barcode with 'some signal', well distinct from a barcode pulse, in milliseconds
    INITIALIZATION_PULSE_TIME = 4 * INITIALIZATION_TIME
    TOTAL_BARCODE_TIME = 2 * INITIALIZATION_PULSE_TIME + BARCODE_TIME * BARCODE_BITS # the total time for the initialization train and barcode signal

    # Generate the test file
    with open(path, "w") as triggerdata_f:
        triggerdata_writer = csv.writer(triggerdata_f)

        # Write a header to the file
        triggerdata_writer.writerow(['time', 'cycle', 'state', 'led1', 'led2', 'led3'])

        current_millis = current_millis_init = 1
        current_cycle = 0  # assume recording at 120 hz, then 1 cycle = 1/120 = 8.333 ms
        state = 1

        for i in range(num_cycles):
            barcode = np.random.randint(2, size=BARCODE_BITS)

            # Generate the rows between the barcodes
            for _ in range(INTER_BARCODE_INTERVAL - TOTAL_BARCODE_TIME):
                triggerdata_writer.writerow([current_millis, current_cycle, '0', '0', '0', '0'])
                current_millis += 1
                current_cycle = int((current_millis - current_millis_init) / 8.333)

            # Generate the initialization train
            state = 1
            for j in range(INITIALIZATION_PULSE_TIME):
                if j % INITIALIZATION_TIME == 0:
                    state = 1 - state
                triggerdata_writer.writerow([current_millis, current_cycle, str(state), '0', '0', '0'])
                current_millis += 1
                current_cycle = int((current_millis - current_millis_init) / 8.333)

            # Generate the barcode
            for bit in barcode:
                for _ in range(BARCODE_TIME):
                    triggerdata_writer.writerow([current_millis, current_cycle, str(bit), '0', '0', '0'])
                    current_millis += 1
                    current_cycle = int((current_millis - current_millis_init) / 8.333)

            # Generate the ending train
            state = 1
            for j in range(INITIALIZATION_PULSE_TIME):
                if j % INITIALIZATION_TIME == 0:
                    state = 1 - state
                triggerdata_writer.writerow([current_millis, current_cycle, str(state), '0', '0', '0'])
                current_millis += 1
                current_cycle = int((current_millis - current_millis_init) / 8.333)


def decode_barcode(barcode_train, timestamps, barcode_bits=32, bit_pulse_duration=0.030, init_pulse_duration=0.015, fs=None):
    """ Decode a train of 0s/1s with 32-bit temporal barcodes

    Parameters
    ----------
    barcode_train : array_like
        A train of 0s and 1s
    
    timestamps : array_like (in seconds)
        The timestamps of the barcode train

    Returns
    -------
    df : pandas.DataFrame
        Dataframe including the barcode start + end times (start /end of the init/finish sequence), each barcode's value, and the overall index of each code for that recording
    """
    
    # First, estimate the sampling rate and interpolate if none is given
    if fs is None:
        fs = 1 / np.mean(np.diff(timestamps))
        interp_train = tw.map_values(timestamps, barcode_train, np.arange(timestamps[0], timestamps[-1], 1 / fs), interpolate=True)
    else:
        interp_train = barcode_train
    
    # Next, find the initiation and ending sequences by template matching
    # Both the init and end pulses are 15 msec of ON, then 15 OFF, then ON, then OFF
    pdb.set_trace()
    init_template = np.array([1] * int(init_pulse_duration * fs) + [0] * int(init_pulse_duration * fs) + [1] * int(init_pulse_duration * fs) + [0] * int(init_pulse_duration * fs))
    c = convolve(df['state'].values, (2*init_template-1)[::-1], mode='valid')
    match = np.argwhere(c == init_template.sum())
    init_match_df = tw.event_epochs(init_match, timestamps, mode="initial_onset", block_min_spacing=0.5)

    return init_match_df
    # This df should now contain both init and end pulses. Each pair of init/end pulses should be separated by 32 bits * 30 msec/bit = 960 msec.
    # We can use this to pair the init and end pulses. We can also use this to find the start and end times of each barcode.
    # Any initial end pulses without an init first should be trimmed, and any final init pulses without an end should be trimmed.

    # First, trim the init pulses


    
if __name__ == "__main__":
    # Generate a test file
    generate_test_file('./scratch/tmp.txt', 20)

    # Read the test file
    df = pd.read_csv('./scratch/tmp.txt', header=0)
    df["time"] = df.time / 1000  # convert to seconds
    print(decode_barcode(df.state.values, df.time.values, fs=1000))
