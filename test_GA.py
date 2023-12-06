from midi.Track import *
from readMidi import get_midi
from parameter.pitchParam import *
from time import time
from GA.GAForPitch import GAForPitch
from GA.GAForRhythm import GAForRhythm

def main():
    t_start = time()
    
    ref_midi = mido.MidiFile(reference_file)
    ref_track = Track.from_track(ref_midi.tracks[0])
    
    population = [
        Track(0, key_mode).generate_random_track(bar_number) for _ in range(population_size)
    ]
    ga_rhythm = GAForRhythm(population, mutation_rate)
    rhythm_track = ga_rhythm.run(iteration_num)
    
    # Use the rhythm of the track forever
    population_with_rhythm = [
        Track(0, key_mode).generate_random_pitch_on_rhythm(rhythm_track)
        for _ in range(population_size)
    ]
    ga_pitch = GAForPitch(ref_track, population_with_rhythm, mutation_rate)
    result = ga_pitch.run(iteration_num)
    
    s = get_midi(key_mode)
    s.tracks.append(result.to_track())
    # accompaniment (stolen from reference)
    if with_accompaniment:
        left_hand = Track.from_track(ref_midi.tracks[1])
        for note in left_hand.note:
            note.velocity = VELOCITY
        s.tracks.append(left_hand.to_track())
    
    s.save(output_file)
    print(f"Time cost: {time() - t_start}s")


if __name__ == '__main__':
    main()
