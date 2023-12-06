from midoWrapper import *
import mido
from copy import deepcopy


def generate_random_midi_test():
    s = get_midi()
    track = Track(0, "G#m")
    track.generate_random_track(4)  # 4 bars
    s.tracks.append(track.to_track())
    retrograde_track = deepcopy(track)  # MUST use deepcopy
    retrograde_track.retrograde()
    s.tracks.append(retrograde_track.to_track())
    save_midi(s, "midi/random.mid")

    # Expected result:
    # random.mid: A random piece with 4 bars in G sharp minor which has 2 tracks,
    # one is the original track, the other is the retrograde track.


def read_midi_test():
    s = mido.MidiFile("midi/test.mid")
    right_hand = Track.from_track(s.tracks[0])
    right_hand.print_brief_info()
    print("----------------")
    left_hand = Track.from_track(s.tracks[1])
    left_hand.print_brief_info()
    # For more information, use print(track) to see the detailed notes.
    print(left_hand.bar_number)

    # Expected output:
    # Key: D
    # Instrument: 0
    # Length: 15353
    # Bar: 8
    # ----------------
    # Key: D
    # Instrument: 0
    # Length: 15347
    # Bar: 8


def main():
    generate_random_midi_test()
    read_midi_test()


if __name__ == "__main__":
    main()
