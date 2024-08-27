## Overview
Dash web application that visualizes a dataset of Spotify tracks. The application allows users to explore various metrics and categories of tracks. The dataset used is a snapshot of Spotify tracks from October 2022.

## Project Structure
- `app.py`: The main Dash application that runs the web dashboard.
- `prepare.py`: Script for data preprocessing and preparation.
- `components.py`: Defines the UI components of the Dash app.
- `operations.py`: Handles data manipulation and analysis operations.
- `utils.py`: Contains utility functions used across the project.
- `assets/`: Folder containing static files.
- `data/`: Directory where the raw and processed datasets are stored.

## Installation

Clone the repository:

```bash
git clone https://github.com/your-repo/spotify-tracks-analysis.git
cd spotify-tracks-analysis
```

Create and activate a virtual environment:

```bash
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

(Optional) Run the data preparation script:

To replicate the data preparation process, you can run the `prepare.py` script. This will process the raw dataset to prepare it for analysis and visualization.

```bash
python prepare.py
```

Run the Dash app:

```bash
python app.py
```

## Acknowledgments

This project uses the Spotify Tracks Dataset from Kaggle,by Maharshi Pandya. You can find the dataset [here](https://www.kaggle.com/maharshibasu/spotify-tracks-dataset).
