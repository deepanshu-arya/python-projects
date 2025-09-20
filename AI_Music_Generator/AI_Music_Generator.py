import random
from mingus.containers import Note, Bar
from mingus.midi import midi_file_out
import os

# Function to create a random melody
def generate_melody(length=4):
    melody = []
    scale = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

    for _ in range(length):
        bar = Bar()
        for _ in range(4):  # 4 notes per bar
            note = Note(random.choice(scale))
            bar.place_notes(note, 4)  # quarter notes
        melody.append(bar)
    return melody

# Function to save melody as MIDI file
def save_midi(melody, filename):
    if len(melody) == 1:
        midi_file_out.write_Bar(filename, melody[0])
    else:
        # Remove old file if exists
        if os.path.exists(filename):
            os.remove(filename)

        # Write each bar to the same file
        for bar in melody:
            midi_file_out.write_Bar(filename, bar)

# Main function
def main():
    print("🎶 AI Music Generator 🎶")
    melody = generate_melody(4)  # 4 bars melody
    save_midi(melody, "ai_music.mid")
    print("✅ Melody saved as ai_music.mid")

if __name__ == "__main__":
    main()
