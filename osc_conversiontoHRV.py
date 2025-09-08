import serial
import time
import keyboard
import re
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import threading


import mido
import time
import random
from music21 import stream, tempo, note, meter, chord

# Open serial connection
ser = serial.Serial('COM6', 115200)  # Replace 'COM6' with your port
time.sleep(2)  # Allow time for Arduino to initialize

# stops audio from playing
stop_flag = False


print("Reading serial data...\n")

# Define the regular expression patterns to extract the numbers
heart_rate_pattern = r"Heart Rate: (\d+)"
sdnn_pattern = r"SDNN: ([\d\.]+)"
rmssd_pattern = r"RMSSD: ([\d\.]+)"

# Load image
img_path = 'pic.png'  # Change this to your image file path
img = mpimg.imread(img_path)  # Read the image

# Initialize Heart Rate, SDNN, and RMSSD
heart_rate = None
sdnn = None
rmssd = None

# Function to handle serial data reading
def read_serial_data():
    global heart_rate, sdnn, rmssd, stop_flag
    try:
        while not stop_flag:
            if ser.in_waiting > 0:  # Check if there is data in the buffer
                data = ser.readline().decode('utf-8').strip()  # Read and decode data
                if data:  # Only process non-empty data

                    # Extract the Heart Rate, SDNN, and RMSSD using regular expressions
                    heart_rate_match = re.search(heart_rate_pattern, data)
                    sdnn_match = re.search(sdnn_pattern, data)
                    rmssd_match = re.search(rmssd_pattern, data)

                    # If a match is found, extract and store the values
                    if heart_rate_match:
                        heart_rate = int(heart_rate_match.group(1))  # Convert to integer
                        print(f"Heart Rate: {heart_rate} bpm")

                    if sdnn_match:
                        sdnn = float(sdnn_match.group(1))  # Convert to float
                        print(f"SDNN: {sdnn} ms")

                    if rmssd_match:
                        rmssd = float(rmssd_match.group(1))  # Convert to float
                        print(f"RMSSD: {rmssd} ms")
                    

    finally:
        # Ensure the serial connection is closed when the program ends
        ser.close()
        print("Serial connection closed.")

def display_image():
    global heart_rate, sdnn, stop_flag

    fig, ax = plt.subplots()
    ax.imshow(img)
    height, width, _ = img.shape

    center_x = width // 2
    center_y = height // 2
    dot, = ax.plot(center_x, center_y, 'ro')

    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.set_xticks([0, width])
    ax.set_yticks([height, 0])
    ax.set_yticklabels([20, 80])
    ax.set_xticklabels([50, 90])

    def update_dot(frame):
        global stop_flag
        if stop_flag:
            print("Stopping image display...")
            plt.close(fig)  # This will close the window
            return dot,  # Exit the animation loop
        if heart_rate is not None and sdnn is not None:
            x = (heart_rate -50) / (90 - 50) * width
            y = (80 - sdnn) / (80 - 20) * height
            x = max(0, min(x, width - 1))
            y = max(0, min(y, height - 1))
            dot.set_data([x], [y])
        return dot,

    from matplotlib.animation import FuncAnimation
    ani = FuncAnimation(fig, update_dot, blit=True, interval=100)
    

    plt.show()  # Non-blocking version of plt.show() to avoid blocking the main thread
    plt.pause(0.1)  # Allow for immediate updates and interaction


def play_chords():
    global heart_rate, sdnn, rmssd, stop_flag

    # Define chord progressions
    chord_definitions = {
        'C': ['C4', 'E4', 'G4'],
        'G': ['G3', 'B3', 'D4'],
        'Am': ['A3', 'C4', 'E4'],
        'F': ['F3', 'A3', 'C4'],
        'Dm': ['D4', 'F4', 'A4'],
        'Em': ['E4', 'G4', 'B4'],
        'Cmaj7': ['C4', 'E4', 'G4', 'B4'],
        'G7': ['G3', 'B3', 'D4', 'F4'],
        'Am7': ['A3', 'C4', 'E4', 'G4'],
        'Fmaj7': ['F3', 'A3', 'C4', 'E4'],
        'Dm7': ['D4', 'F4', 'A4', 'C5'],
        'Em7': ['E4', 'G4', 'B4', 'D5'],
        'C13': ['C4', 'E4', 'G4', 'B4', 'D5', 'A5'],
        'G13': ['G3', 'B3', 'D4', 'F4', 'A4', 'E5'],    
        'Am13': ['A3', 'C4', 'E4', 'G4', 'B4', 'F#5'],
        'Fmaj13': ['F3', 'A3', 'C4', 'E4', 'G4', 'D5'],
        'Dm13': ['D4', 'F4', 'A4', 'C5', 'E5', 'B5'],
        'Em13': ['E4', 'G4', 'B4', 'D5', 'F#5', 'C6'],

        'Ab': ['Ab3', 'C4', 'Eb4'],
        'Bbm': ['Bb3', 'Db4', 'F4'],
        'Cm': ['C3', 'Eb4', 'G4'],
        'Db': ['Db3', 'F4', 'Ab4'], 
        'Eb': ['Eb3', 'G4', 'Bb4'],
        'Fm': ['F3', 'Ab4', 'C5'],
        'Gm': ['G3', 'Bb4', 'D5'],
        'Abmaj7': ['Ab3', 'C4', 'Eb4', 'G4'],
        'Bbm7': ['Bb3', 'Db4', 'F4', 'Ab4'],
        'Cm7': ['C3', 'Eb4', 'G4', 'Bb4'],
        'Dbmaj7': ['Db3', 'F4', 'Ab4', 'C5'],
        'Eb7': ['Eb3', 'G4', 'Bb4', 'Db5'],
        'Fm7': ['F3', 'Ab4', 'C5', 'Eb5'],
        'Abmaj13': ['Ab3', 'C4', 'Eb4', 'G4', 'Bb4', 'F5'],
        'Bbm13': ['Bb3', 'Db4', 'F4', 'Ab4', 'C5', 'G5'],
        'Cm13': ['C3', 'Eb4', 'G4', 'Bb4', 'D5', 'Ab5'],
        'Dbmaj13': ['Db3', 'F4', 'Ab4', 'C5', 'Eb5', 'Bb5'],
        'Eb13': ['Eb3', 'G4', 'Bb4', 'Db5', 'F5', 'C6'],
        'Fm13': ['F3', 'Ab4', 'C5', 'Eb5', 'G5', 'D6'],
        }

    chord_chain = {

    # more complexity
    'C': {'Cmaj7': 0.3, 'Abmaj7': 0.3, 'G7': 0.2},
    'Cmaj7': {'Am7': 0.3, 'Fmaj7': 0.3, 'G7': 0.4, 'C13': 0.2},
    'Am7': {'Dm7': 0.4, 'Fmaj7': 0.3, 'Em7': 0.3, 'Am13': 0.2},
    'Fmaj7': {'Cmaj7': 0.4, 'Dm7': 0.3, 'G7': 0.3, 'Fmaj13': 0.2},
    'G7': {'Cmaj7': 0.5, 'Em7': 0.2, 'Am7': 0.3, 'G13': 0.2},
    'Dm7': {'Am7': 0.4, 'Fmaj7': 0.3, 'Em7': 0.3, 'Dm13': 0.2},
    'Em7': {'Am7': 0.5, 'Cmaj7': 0.3, 'G7': 0.2, 'Em13': 0.2},
    'C13': {'Am13': 0.3, 'Fmaj13': 0.3, 'G13': 0.4},
    'Am13': {'Dm13': 0.4, 'Fmaj13': 0.3, 'Em13': 0.3},
    'Fmaj13': {'C13': 0.4, 'Dm13': 0.3, 'G13': 0.3},
    'G13': {'C13': 0.5, 'Em13': 0.2, 'Am13': 0.3},
    'Dm13': {'Am13': 0.4, 'Fmaj13': 0.3, 'Em13': 0.3},
    'Em13': {'Am13': 0.5, 'C13': 0.3, 'G13': 0.2},
    

    # more complexity
    'Abmaj7': {'Bbm7': 0.3, 'Eb7': 0.4, 'Dbmaj7': 0.3},
    'Bbm7': {'Eb7': 0.4, 'Abmaj7': 0.3, 'Fm7': 0.3},
    'Eb7': {'Abmaj7': 0.5, 'Bbm7': 0.3, 'Cm7': 0.2},
    'Dbmaj7': {'Eb7': 0.5, 'Abmaj7': 0.3, 'Cm7': 0.2},
    'Abmaj13': {'Bbm13': 0.4, 'Eb13': 0.4, 'Dbmaj13': 0.2},
    'Bbm13': {'Eb13': 0.4, 'Abmaj13': 0.3, 'Fm7': 0.3},
    'Eb13': {'Abmaj13': 0.5, 'Bbm13': 0.3, 'Cm13': 0.2},
    'Dbmaj13': {'Eb13': 0.5, 'Abmaj13': 0.3, 'Bbm13': 0.2},
    'Fm7': {'Abmaj7': 0.5, 'Bbm7': 0.3, 'Cm7': 0.2},
    'Fm13': {'Abmaj13': 0.5, 'Bbm13': 0.3, 'Cm13': 0.2},
    'Cm7': {'Fm7': 0.4, 'Bbm7': 0.3, 'Eb7': 0.3},
    'Cm13': {'Fm13': 0.4, 'Bbm13': 0.3, 'Eb13': 0.3},

    }
    
    chord_chain1 = {
    # lower arousal
     'C': {'Ab': 0.3, 'Eb': 0.3, 'G': 0.2},  # C moves to more distant or ambiguous chords
    'Eb': {'Ab': 0.5, 'C': 0.2, 'Fm': 0.3},  # Eb can transition more freely to Fm or C
    'Ab': {'C': 0.4, 'G': 0.3, 'Fm': 0.3},  # Ab can make a surprise jump to G or Fm
    'G': {'Ab': 0.4, 'Eb': 0.3, 'Fm': 0.3},  # G can lead to more unexpected shifts like Ab or Fm
    'Fm': {'C': 0.3, 'Ab': 0.4, 'Eb': 0.3},  # Fm is introduced as a transitional chord with flexibility
    }
    chord_chain2 = {
    # less complexity
    'C': {'Am': 0.3, 'F': 0.3, 'Ab': 0.2},
    'Am': {'F': 0.3, 'Em': 0.3, 'Dm': 0.2},
    'F': {'C': 0.4, 'Dm': 0.3, 'G': 0.2},
    'G': {'C': 0.5, 'Em': 0.2},
    'Dm': {'Am': 0.4, 'Em': 0.3},
    'Em': {'Am': 0.4, 'C': 0.3},

    # less complexity
    'Ab': {'Bbm': 0.4, 'Eb': 0.4, 'Db': 0.2},
    'Bbm': {'Eb': 0.5, 'Ab': 0.3, 'Fm': 0.2},
    'Eb': {'Ab': 0.4, 'Cm': 0.3, 'Bbm': 0.3},
    'Db': {'Eb': 0.5, 'Ab': 0.3, 'Bbm': 0.2},
    'Cm': {'Fm': 0.4, 'Eb': 0.3, 'Bbm': 0.3},
    'Fm': {'Ab': 0.5, 'Bbm': 0.3, 'Cm': 0.2},
    }


    # Function to convert chord to MIDI notes
    def chord_to_midi(chord_input):
    
        # Check if the input is a chord name (string)
        if isinstance(chord_input, str):
            # Retrieve the corresponding list of note names from the chord_definitions dictionary
            if chord_input in chord_definitions:
                chord_list = chord_definitions[chord_input]
                print(f"Current chord being played: {chord_input} ({', '.join(chord_list)})")  # Print the chord and its notes
            else:
                raise ValueError(f"Chord name '{chord_input}' not found in definitions.")
        elif isinstance(chord_input, list):
            # If input is already a list of note names
            chord_list = chord_input
            print(f"Current chord being played: {', '.join(chord_list)}")  # Print the notes directly
        else:
            raise ValueError(f"Invalid input type: {type(chord_input)}. Expected string or list.")
        
        # Convert note names (e.g., 'C4', 'E4') to MIDI numbers
        return [note.Note(n).pitch.midi for n in chord_list]
    
    

    outport = mido.open_output('PythontoLive 1')  # Replace with your actual port name

    # Wait until heart rate and SDNN are available
    while heart_rate is None or sdnn is None:
        time.sleep(0.1)

    music_stream = stream.Stream()

    # 🎛️ CC mappings
    cc_mapping = {
        'rmssd_filter': 91,  # Example: reverb or any knob you map
        'sdnn_sustain': 74,   # Example: filter cutoff
        'rmssd_release': 11,  # New CC 11 for release time (based on RMSSD)
        'heart_rate_attack': 10  # New CC 10 for pan control (based on heart rate)
    }

    last_cc_sent = {param: -1 for param in cc_mapping.keys()}

    last_chord_time = time.time()
    last_cc_time = time.time()
    last_hr_value = None
    last_hr_check_time = 0  # Last time we compared heart rates
    last_rmssd_check_time = 0
    last_rmssd_value = None
    rmssd_change_threshold = 10  # Minimum RMSSD change to consider significant
    hr_change_threshold = 3  # Minimum BPM change to consider significant
    
    # release controls
    release_length = 4.5  # Initial release length
    max_release_length = 8.0  # Maximum release length
    min_release_length = 0.5  # Minimum release length


    # Note length control
    note_length = 0.5
    max_note_length = 8.0
    min_note_length = 0.1

    current_chord = "C"

    while not stop_flag:
        now = time.time()

        # CC
        if now - last_cc_time > 0.05:
            for param, cc_num in cc_mapping.items():
                value = 0

                # Handle CCs based on parameters
                if param == 'rmssd_filter' and rmssd is not None:
                    value = int(min(max((rmssd - 10) * (127 / 160), 0), 127))
                elif param == 'sdnn_sustain' and sdnn is not None:
                    value = int(min(max((sdnn - 10) * 2, 0), 127))  # Scale SDNN
                elif param == 'heart_rate_attack' and heart_rate is not None:
                    # Linearly scale heart_rate from 50 to 90 to range 0-127
                    value = int(min(max((90 - heart_rate) * (127 / 40), 0), 127))
                elif param == 'rmssd_release' and release_length is not None:
                    value = int(min(max((release_length - 0.5) * (127 / 7.5), 0), 127))
                

                # Only send if value changed
                if value != last_cc_sent[param]:
                    outport.send(mido.Message('control_change', control=cc_num, value=value))
                    last_cc_sent[param] = value
                    print(f"[CC] Sent {param} -> CC{cc_num} = {value}")

            last_cc_time = now

        # Heart Rate Change every 20 seconds
        if now - last_hr_check_time >= 20 and heart_rate is not None:
            if last_hr_value is None:
                last_hr_value = heart_rate  # First measurement
            else:
                # Calculate change from last 20-second window
                hr_change = abs(heart_rate - last_hr_value)
                stable = hr_change <= hr_change_threshold

                # Adjust note length based on stability
                target_length = max_note_length if stable else min_note_length
                note_length = note_length * 0.9 + target_length * 0.1  # Smooth transition

                print(f"[HR] Change: {hr_change:.1f} BPM | Stable: {stable} | Note Length: {note_length:.2f}s")
            
            last_hr_value = heart_rate  # Store for next comparison
            last_hr_check_time = now  # Reset timer

        # RMSSD every 20 seconds
        if now - last_rmssd_check_time >= 20 and rmssd is not None:
            if last_rmssd_value is None:
                last_rmssd_value = rmssd  # First measurement
            else:
                # Calculate change from last 20-second window
                rmssd_change = abs(rmssd - last_rmssd_value)
                stable_rmssd = rmssd_change <= rmssd_change_threshold

                # Adjust note length based on stability
                target_length_rmssd = max_release_length if stable_rmssd else min_release_length
                release_velocity = (target_length_rmssd - release_length) * 0.5  # 0.1 = acceleration rate
                release_length += release_velocity

                print(f"[Release] Change: {rmssd_change:.1f} Release | Stable: {stable_rmssd} | Release Length: {release_length:.2f}s")
            
            last_rmssd_value = rmssd  # Store for next comparison
            last_rmssd_check_time = now  # Reset timer

        # CHORD COMPLEXITY
        
        if now - last_chord_time > note_length:
            previous_chord = current_chord
            # Select the next chord based on SDNN value
            if heart_rate is not None and heart_rate < 65:
                # Less complex chords (simpler)
                possible_chords = chord_chain
            elif heart_rate is not None and heart_rate > 85:
                # More complex chords (advanced)
                possible_chords = chord_chain2
            else:
                # More complex chords (advanced)
                possible_chords = chord_chain1

            if previous_chord not in possible_chords:
                current_chord = "C"  # reset to safe default
            else:
                current_chord = previous_chord
    

            # Get the probabilities for the current chord
            next_chord_probabilities = possible_chords[current_chord]
            # Choose next chord based on the Markov chain probabilities
            next_chord = random.choices(list(next_chord_probabilities.keys()), weights=next_chord_probabilities.values())[0]
            
            current_chord = next_chord  # Update current chord

            # Convert the current chord to MIDI notes
            midi_notes = chord_to_midi(current_chord)

            # Send MIDI notes for the current chord
            for midi_note in midi_notes:
                outport.send(mido.Message('note_on', note=midi_note, velocity=100))
        
            time.sleep(note_length)
        
            # Stop the MIDI notes
            for midi_note in midi_notes:
                outport.send(mido.Message('note_off', note=midi_note, velocity=100))
        
            # Update last chord time
            last_chord_time = now

        time.sleep(0.1)  # Small sleep to reduce CPU usage

serial_thread = threading.Thread(target=read_serial_data)
serial_thread.daemon = True
serial_thread.start()

music_thread = threading.Thread(target=play_chords)
music_thread.daemon = True
music_thread.start()

display_image()

# Monitor for 'i' key to stop threads
try:
    while True:
        if keyboard.is_pressed('i'):
            print("[SYSTEM] 'i' key pressed. Stopping all threads.")
            stop_flag = True
            break
        time.sleep(0.1)
except KeyboardInterrupt:
    stop_flag = True
    print("[SYSTEM] Ctrl+C detected. Exiting...")


# Wait for threads to exit
serial_thread.join()
music_thread.join()
