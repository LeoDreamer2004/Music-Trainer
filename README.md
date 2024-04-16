# Music Trainer

Midterm Assignment for Math In Music course in 2023 Autumn.

---

## What is this

The target is to create short music piece by machine with genetic algorithm.
Meanwhile, we provide an easy API `midoWrapper` for `mido`. See the docstrings for more information.

For more detailed information, you can find our report in [report/report.md](report/report.md) or [report/report.pdf](report/report.pdf).

## Preparation

Make sure you have installed `python3` and `pip`. All used third parties are saved in the config text. You can use

```shell
git clone https://github.com/LeoDreamer2004/PKU-MathInMusic-2023.git
```

to copy the repository to your folder, and then execute in the command line within this folder:

```shell
pip install -r requirements.txt
```

## How to use

We apply one demo to parse the midi and the other to train for music in genetic algorithm. Visit all the results in `./midi` folder.

```shell
python ./wrapperTest.py
python ./geneticAlgorithm.py
```

- `wrapperTest.py` will try to parse the `test.mid` and print the result. Meanwhile, it is supposed to generate a new midi file `random.mid` with two retrograde tracks.
- `geneticAlgorithm.py` will try to generate a midi file `result.mid` with genetic algorithm.

If you have passed the midterm, you can try to run the `main.py`, which support a GUI for you to play with.

The GUI is based on `pyqt5` and `pyqt_fluent`. Run in terminal:

```shell
python ./main.py
```

If you find an error message box, you probably need to install some third party modules. See the build section above. Enjoy it!

## License

MIT
