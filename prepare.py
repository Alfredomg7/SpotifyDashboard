import pandas as pd

def drop_duplicates(df):
    df = df.drop_duplicates(subset=['track_name', 'artists', 'genre'], keep='first')
    return df

def combine_duplicates(df):
    combined_genres = df.groupby('track_id').agg(
        genres=('genre', lambda x: '-'.join(pd.unique(x)))
    ).reset_index()
    df_unique = df.drop_duplicates(subset='track_id', keep='first')
    combined_df = df_unique.merge(combined_genres, on='track_id')
    return combined_df

def convert_duration_column_to_min(df):
    df['duration_min'] = round(df['duration_ms'] / 60000, 2)
    return df

def convert_bool_to_string(df, column):
    df[column] = df[column].astype(str)
    df[column] = df[column].str.replace('True', 'Yes')
    df[column] = df[column].str.replace('False', 'No')
    return df

def format_artist_name(df, artist_column):
    df[artist_column] = df[artist_column].str.replace(';',' ft. ')
    return df

def map_genre(df, genre_map_df):
    genre_mapping = pd.Series(genre_map_df.general_genre.values, index=genre_map_df.genre).to_dict()
    df['general_genre'] = df['genre'].map(genre_mapping)
    return df

def create_histogram_data(df, column):
    bins = [0, 25, 50, 75, 100]
    labels = [f'{i}-{j}' for i, j in zip(bins[:-1], bins[1:])]
    df[f'{column}_bin'] = pd.cut(df[column], bins=bins, labels=labels, right=False)
    histogram_data = df.groupby('popularity_bin', observed=True).agg(
        count=('track_id', 'count'),
        popularity=('popularity', 'mean'),
        duration_min=('duration_min', 'mean'),
        danceability=('danceability', 'mean'),
        energy=('energy', 'mean'),
        key=('key', 'mean'),
        loudness=('loudness', 'mean'),
        mode=('mode', 'mean'),
        speechiness=('speechiness', 'mean'),
        acousticness=('acousticness', 'mean'),
        instrumentalness=('instrumentalness', 'mean'),
        liveness=('liveness', 'mean'),
        valence=('valence', 'mean')
    ).reset_index()
    histogram_data = histogram_data.round(decimals=2)
    return histogram_data

def prepare():
    input_file_path = "https://raw.githubusercontent.com/plotly/Figure-Friday/main/2024/week-34/dataset.csv"
    map_file_path = "data/genre_map.csv"
    prepared_file_path = "data/spotify_data_prepared.csv"
    histogram_data_path = "data/histogram_data.csv"
    df = pd.read_csv(input_file_path)
    genre_map_df = pd.read_csv(map_file_path)
    
    df = df.rename(columns={'track_genre': 'genre'})
    prepared_df = drop_duplicates(df)
    prepared_df = combine_duplicates(prepared_df)
    prepared_df = convert_duration_column_to_min(prepared_df)
    prepared_df = convert_bool_to_string(prepared_df, 'explicit')
    prepared_df = map_genre(prepared_df, genre_map_df)
    prepared_df = prepared_df.reset_index()
    prepared_df = prepared_df.drop(columns=['Unnamed: 0', 'duration_ms'])
    prepared_df = format_artist_name(df, 'artists')
    prepared_df.to_csv(prepared_file_path, index=False)
    histogram_df = create_histogram_data(prepared_df, 'popularity')
    histogram_df.to_csv(histogram_data_path, index=False)

if __name__ == "__main__":
    prepare()