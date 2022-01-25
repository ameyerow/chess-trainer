# Chess Repertoire Trainer
Use this program to improve your recall of opening preparation. Using this you to play against a computer that follows the moves in your opening pgn files. By default this plays through the French Defense, but this can be changed by adding a new file in the ``./pgns`` folder. If the pgn file you add is not named ``FrenchDefense.pgn`` you must change the path in ``./src/main.py`` to point to your new file (this is on line 29).

# Prerequisites
Python versions and dependencies are managed with pipenv. If you do not have pipenv already,
install and verify the installation.
```
pip install pipenv
pipenv -h
```

# Running
When running the project for the first time, it is necessary to install dependencies. Run the 
following commands from the root directory to properly set up your environment and run the program.
```
pipenv install
pipenv shell
python -m src.main
```
On subsequent runs, the python enviornment will already have been created via pipenv so you can simply activate it and run the trainer.
```
pipenv shell
python -m src.main
```