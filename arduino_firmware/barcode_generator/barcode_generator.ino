/*
  Modified by:
    Jonah Pearl, Nov 2023

  Changes:
    -- mild renaming
    -- improved randomization using the Entropy library for Teensy's
    -- changed timer to use elapsedMillis library
    -- randomized barcode sequence and while preventing repeats (and it should be very unlikely to go ABAB.)

  Original authors:
    Optogenetics and Neural Engineering Core ONE Core
    University of Colorado, School of Medicine
    31.Oct.2021
    See bit.ly/onecore for more information, including a more detailed write up.
  
  Continuously ouputs highly randomized 32-bit digital barcodes; for synchronizing data streams

  Side note: Be sure to well tie together/understand your frequency of measurements (DAQ) and how that
  relates to the frequency of the barcodes. Nyst equation says that we should know the fastest
  oscillation of our signal. We can then FULLY measure that signal by sampling at just over two
  times as fast. That means, if we plan to measure at 2000Hz, we can reliably FULLY measure a
  1000Hz signal. This corresponds to a 1 msec period. Our chosen fastest barcode of 10 msec is
  well above this.

  Based heavily on the ideas of a barcode generation ino from Open Ephys at https://open-ephys.org/
*/

#include <Entropy.h>

const int INTER_BARCODE_INTERVAL = 5000;     // Total time between barcode initiation (includes initialization pulses) in milliseconds. The length of time between one barcode and the next
const int OUTPUT_PIN = 9;   // Digital pin to output the Barcode TTL
const int BARCODE_BITS = 32;  // number of bits in the barcode
const int BARCODE_TIME = 30;  // time for each bit of the barcode to be on/off in milliseconds
const int INITIALIZATION_TIME = 15;  // We warp the beginning and ending of the barcode with 'some signal', well distinct from a barcode pulse, in milliseconds
const int INITIALIZATION_PULSE_TIME = 4 * INITIALIZATION_TIME;
const int TOTAL_BARCODE_TIME = 2 * INITIALIZATION_PULSE_TIME + BARCODE_TIME * BARCODE_BITS; // the total time for the initialization train and barcode signal

elapsedMillis since_last_barcode; // a timer for when to do the next barcard
int barcode;   // initialize a variable to hold our barcode
int prev_barcode;  // will prevent from going back to the prev barcode just for safety

void setup() {

  // properly reseed the random seed. Entropy library is only on Teensy's. Can be slow, so only do once in beginning.
  Entropy.Initialize();
  randomSeed(Entropy.random());

  pinMode(OUTPUT_PIN, OUTPUT); // initialize digital pin
  barcode = random(0, pow(2, BARCODE_BITS)); // generates a random number between 0 and 2^32 (4294967296)
}

void loop() {
  if (since_last_barcode >= INTER_BARCODE_INTERVAL) // if it's time to do the next barcode
  {
    prev_barcode = barcode; // save the current barcode
    barcode = random(0, pow(2, BARCODE_BITS)); // generate a new barcode
    while (barcode == prev_barcode) // if the new barcode is the same as the old barcode
    {
      barcode = random(0, pow(2, BARCODE_BITS)); // generate a new barcode
    }
    since_last_barcode = since_last_barcode - INTER_BARCODE_INTERVAL; // reset the timer
    
    // start barcode with a distinct pulse to signal the start.
    digitalWrite(OUTPUT_PIN, HIGH); delay(INITIALIZATION_TIME);
    digitalWrite(OUTPUT_PIN, LOW); delay(INITIALIZATION_TIME);
    digitalWrite(OUTPUT_PIN, HIGH); delay(INITIALIZATION_TIME);
    digitalWrite(OUTPUT_PIN, LOW); delay(INITIALIZATION_TIME);

    // BARCODE SECTION
    for (int i = 0; i < BARCODE_BITS; i++) // for between 0-31 (we will read all 32 bits)
    {
      int barcodedigit = bitRead(barcode >> i, 0);
      // bitRead(x, n) Reads the bit of number x at bit n. The '>>' is a
      // rightshift bitwise operator. For i=0 (0000000000000101) outputs 1. For
      // i=1 (0000000000000010) outputs 0.

      if (barcodedigit == 1)    // if the digit is 1
      {
        digitalWrite(OUTPUT_PIN, HIGH);  // set the output pin to high
      }
      else
      {
        digitalWrite(OUTPUT_PIN, LOW);   // else set it to low
      }
      delay(BARCODE_TIME);   // delay 30 ms
    }

    // end barcode with a distinct pulse to signal the beginning. low, high, low
    digitalWrite(OUTPUT_PIN, HIGH); delay(INITIALIZATION_TIME);
    digitalWrite(OUTPUT_PIN, LOW); delay(INITIALIZATION_TIME);
    digitalWrite(OUTPUT_PIN, HIGH); delay(INITIALIZATION_TIME);
    digitalWrite(OUTPUT_PIN, LOW); delay(INITIALIZATION_TIME);
}