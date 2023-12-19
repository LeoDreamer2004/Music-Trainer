from time import time
from midoWrapper import *
from train.pitch import GAForPitch
from train.rhythm import GAForRhythm

reference_file = "midi/reference.mid"
output_file = "midi/result.mid"
with_accompaniment = True

mutation_rate = 0.8
iteration_num = 1000
population_size = 20


def main():
    t_start = time()

    refmidi = Midi.from_midi(reference_file)
    ref_track, left_hand = refmidi.tracks
    bar_number = ref_track.bar_number
    population = [
        Track(ref_track.settings).generate_random_track(bar_number)
        for _ in range(population_size)
    ]
    ga_rhythm = GAForRhythm(population, mutation_rate)
    rhythm_track = ga_rhythm.run(iteration_num)

    # Use the rhythm of the track forever
    population_with_rhythm = [
        Track(ref_track.settings).generate_random_pitch_on_rhythm(rhythm_track)
        for _ in range(population_size)
    ]
    ga_pitch = GAForPitch(ref_track, population_with_rhythm, mutation_rate)
    result = ga_pitch.run(iteration_num)

    s = Midi(ref_track.settings)
    s.settings.BPM = 120
    s.tracks.append(result)

    # accompaniment (stolen from reference)
    if with_accompaniment:
        for note in left_hand.note:
            note.velocity = ref_track.settings.VELOCITY
        s.tracks.append(left_hand)

    s.save_midi(output_file)
    print(f"Time cost: {time() - t_start}s")


if __name__ == "__main__":
    main()
