# Music Similarity Explorer

A Python desktop application for exploring music similarity using Spotify-style audio features. The app loads a CSV dataset, compares tracks or artists using several similarity metrics, and shows the closest recommendations in a Tkinter-based graphical interface.

## Overview

This project builds a lightweight recommendation and similarity search tool around a dataset of tracks with numeric audio attributes such as:

- danceability
- energy
- valence
- tempo
- acousticness
- instrumentalness
- liveness
- speechiness
- popularity

Users can:

- compare two tracks by similarity
- compare two artists by the average feature vector of their tracks
- find the five most similar tracks for a given track ID
- find the five most similar artists for a given artist name
- view summary statistics for the dataset

## Features

- Similarity metrics:
  - cosine
  - pearson
  - euclidean
  - manhattan
- Track-level and artist-level comparison
- Recommendations based on scaled numeric features
- Cleaned dataset parsing and validation
- Desktop GUI built with Tkinter
- Docker support for browser-based access via noVNC

## Project structure

```text
Recommendation/
├── app/
│   ├── __init__.py
│   ├── load_dataset_module.py
│   ├── similarity_module.py
│   ├── statistics_module.py
│   └── user_interface_module.py
├── data/
│   └── data.csv
├── Dockerfile
├── README.md
├── main.py
├── pyproject.toml
├── requirements.txt
├── start.sh
└── .venv/
```

## Dataset requirements

The app expects a CSV file with at least the following columns:

- `id`
- `name`
- `artists`

The dataset should also include numeric feature columns such as:

- `danceability`
- `energy`
- `valence`
- `tempo`
- `acousticness`
- `instrumentalness`
- `liveness`
- `speechiness`
- `popularity`

The loader automatically cleans the dataset by removing empty rows, duplicate rows, and converting artist values into a readable string format.

## Setup

### Local environment

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python -m main
```

## Running the app

When the app starts, a Tkinter window opens with the following options:

- select whether to compare tracks or artists
- choose a similarity metric
- enter a track ID or artist name
- compare two values directly
- review dataset statistics

## Docker usage

A Docker setup is included for running the GUI in a containerized environment.

### Build the image

```bash
docker build -t music-similarity-app .
```

### Run the container

```bash
docker run -p 6080:6080 -p 5900:5900 music-similarity-app
```

Then open the noVNC client in a browser:

```text
http://localhost:6080/vnc.html
```

## Notes

- The application expects the dataset to be located at `data/data.csv`.
- The recommendation engine uses min-max scaling to normalize feature values before comparing items.
- Similarity scores are returned in the range from `0` to `1`, where higher values indicate greater similarity.

## License

This project is provided as-is for educational and personal use.
