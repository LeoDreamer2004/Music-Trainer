from midi.Track import *
from GA.TrackPopulation import TrackPopulation
from readMidi import get_midi

def main():
    from time import time
    from random import seed
    
    seed(0)
    
    KEY = 'E'
    t0 = time()
    
    ref_midi = mido.MidiFile('reference.mid')
    ref_track = Track.from_track(ref_midi.tracks[0])
    
    population = [Track(0, KEY).generate_random_track_plus(8) for _ in range(10)]
    ga = TrackPopulation(ref_track, population, mutation_rate)
    result = ga.run(2000)
    
    s = get_midi(KEY)
    s.tracks.append(result.to_track())
    
    # ref_track2 = Track.from_track(ref_midi.tracks[1])
    # population2 = [Track(0, KEY).generate_random_track(8) for _ in range(10)]
    # ga2 = TrackPopulation(ref_track2, population2, 0.8)
    # result2 = ga2.run(1000)
    # s.tracks.append(result2.to_track())
    
    s.save('result.mid')
    
    print(f"Time cost: {time() - t0} s")


if __name__ == '__main__':
    main()
