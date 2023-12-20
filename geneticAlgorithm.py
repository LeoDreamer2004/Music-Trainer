from time import time
from midoWrapper import Midi
from train import train

reference_file = "midi/reference.mid"
output_file = "midi/result.mid"
with_accompaniment = True


def main():
    t_start = time()

    refmidi = Midi.from_midi(reference_file)
    ref_track, left_hand = refmidi.tracks
    result = train(ref_track)

    s = Midi(ref_track.sts)
    s.sts.bpm = 120
    s.tracks.append(result)

    # accompaniment (stolen from reference)
    if with_accompaniment:
        for note in left_hand.note:
            note.velocity = ref_track.sts.velocity
        s.tracks.append(left_hand)

    s.save_midi(output_file)
    print(f"Time cost: {time() - t_start}s")


if __name__ == "__main__":
    main()
