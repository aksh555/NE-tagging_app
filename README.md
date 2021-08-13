# NER Tagger

## Installation
First, [install MongoDB](https://docs.mongodb.com/manual/installation/). Then create a virtual environment and install all dependencies by running:
```
$ pip install pipenv
$ pipenv shell
$ pipenv install
```

## Import data
To import the prepared JSON file (xyz.json) to populate the database, run:
```
$ sudo service mongod start
$ mongoimport --db ner_corpus --collection sentences --file <full path to xyz.json> --jsonArray
```

## Usage
To run the program, ensure MongoDB is running, start it using:
```
$ sudo service mongod start
```
then, run the program:
```
$ python app.py
```
Open the browser and go to `localhost:5000` to see the running program.

## Exporting votes
```
$ mongoexport --db ner_corpus --collection sentences --out <xyz.json> --jsonArray --pretty
```