from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import components as cmp
import polars as pl
from operations import calculate_difference, count_by_category
from utils import format_label, get_avg_metrics

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

all_data_path = 'data/spotify_data_prepared.csv'
all_data_df = pl.read_csv(all_data_path)
all_data_df = all_data_df.sort('popularity', descending=True)

histogram_data_path = 'data/histogram_data.csv'
histogram_df = pl.read_csv(histogram_data_path)

excluded_columns = ['popularity_bin', 'popularity']
metric_columns = [col for col in histogram_df.columns if col not in excluded_columns]
avg_metrics = get_avg_metrics(metric_columns, all_data_df, histogram_df)

category_columns = ['general_genre', 'explicit', 'time_signature']
popularity_bins = ['0-25', '25-50', '50-75', '75-100']

top_bin = popularity_bins[-1]
bottom_bin = popularity_bins[0]
top_tracks_df = histogram_df.filter(pl.col('popularity_bin') == top_bin)
bottom_tracks_df = histogram_df.filter(pl.col('popularity_bin') == bottom_bin)

logo_img = html.Img(src='assets/logo.png', height='50px')
title = html.H1('Spotify Tracks Dashboard', style={'color': cmp.PRIMARY_COLOR}, className='text-center')
subtitle = html.P('Snapshot from October 2022', style={'color': cmp.PRIMARY_COLOR}, className='lead')

label_style = {'color': cmp.PRIMARY_COLOR, 'font-weight': '500', 'font-size': '20px'}
category_label = dbc.Label('Category', style=label_style)
popularity_label = dbc.Label('Popularity Bin', style=label_style)

metric_tabs = cmp.create_tabs('metric-tabs', metric_columns)
category_tabs = cmp.create_tabs('category-tabs', category_columns)
popularity_tabs = cmp.create_tabs('popularity-tabs', popularity_bins)

chart_style = {'height': '40vw'}
histogram_chart = dcc.Graph(id='histogram-chart', style=chart_style)
butterfly_chart = dcc.Graph(id='butterfly-chart', style=chart_style)
table_container = html.Div(id='table')

avg_metric_card = cmp.create_card(text_id='avg-card-text', title_id='avg-card-title')
most_popular_tracks_card = cmp.create_card(text_id='popular-tracks-text')
least_popular_tracks_card = cmp.create_card(text_id='unpopular-tracks-text')

footer = cmp.create_footer()

app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                logo_img
            ], md=2, sm=3, xs=12, className='mb-2 mt-2'),
            dbc.Col([
                title
            ], md=6, sm=9, xs=12, className='mb-2 mt-2'),
            dbc.Col([
                subtitle
            ], md=4, sm=12, className='mb-2 mt-2'),
        ], className='mb-2 mt-2 text-center'),
        dbc.Row([
            dbc.Col([
                metric_tabs
            ], width=12, className='mb-4')
        ], className='mb-4'),
        dbc.Row([
            dbc.Col([
                histogram_chart
            ], width=12, className='mb-4'),
            dbc.Col([
                avg_metric_card
            ], md=4, sm=12, className='mb-4'),
            dbc.Col([
                most_popular_tracks_card
            ], md=4, sm=12, className='mb-4'),
            dbc.Col([
                least_popular_tracks_card
            ], md=4, sm=12, className='mb-4')
        ], className='mb-4'),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col(category_label, md=3, sm=12, className='mb-2 text-center'),
                    dbc.Col(category_tabs, md=9, sm=12, className='mb-2')
                ], 
                align='center'
                )
            ], lg=6, md=12, className='mb-2'),
            dbc.Col([
                dbc.Row([
                    dbc.Col(popularity_label, md=3, sm=12, className='mb-2 text-center'),
                    dbc.Col(popularity_tabs, md=9, sm=12, className='mb-2')
                ], 
                align='center'
                )
            ], lg=6, md=12, className='mb-2')
        ], className='mb-2'),
        dbc.Row([
            dbc.Col([
                butterfly_chart
            ], width=12, className='mb-4')
        ], className='mb-4'),
        dbc.Row([
            dbc.Col([
                table_container
            ], width=12, className='mb-4')
        ], className='mb-4')
    ],  
    fluid=True,
    className='mx-auto'
    ),
    footer
], style={'background-color': cmp.BACKGROUND_COLOR})

@app.callback(
    Output('histogram-chart', 'figure'),
    Output('avg-card-title', 'children'),
    Output('avg-card-text', 'children'),
    Output('popular-tracks-text', 'children'),
    Output('unpopular-tracks-text', 'children'),
    [Input('metric-tabs', 'active_tab')]
)
def update_distribution_charts(metric):
    x = 'popularity_bin'
    y = metric
    
    fig = cmp.create_custom_histogram(histogram_df, x, y)
    
    title = f'AVG {format_label(metric)}'
    avg_value = avg_metrics.get(metric, 'N/A')
    avg_value_text = str(avg_value)
    top_tracks_diff = calculate_difference(top_tracks_df, metric, avg_metrics[metric])
    bottom_tracks_diff = calculate_difference(bottom_tracks_df, metric, avg_metrics[metric])

    top_tracks_text = cmp.create_difference_text(top_bin, top_tracks_diff, metric)
    bottom_tracks_text = cmp.create_difference_text(bottom_bin, bottom_tracks_diff, metric)

    return fig, title, avg_value_text, top_tracks_text, bottom_tracks_text

@app.callback(
    Output('butterfly-chart', 'figure'),
    Output('table', 'children'),
    [Input('category-tabs', 'active_tab'),
    Input('popularity-tabs', 'active_tab')]
)
def update_category_chart(category, popularity_bin):
    min_popularity, max_popularity = map(int, popularity_bin.split('-'))
    filtered_df = all_data_df.filter((pl.col('popularity') >= min_popularity) & (pl.col('popularity') <= max_popularity))
    
    total_count_by_category_df = count_by_category(all_data_df, category, alias='total_count')
    bin_count_by_category_df = count_by_category(filtered_df, category, alias='bin_count')
    merged_df = total_count_by_category_df.join(bin_count_by_category_df, on=category)
    fig = cmp.create_butterfly_chart(merged_df, 'total_count', 'bin_count', category)
    
    selected_columns = ['track_name', 'artists', 'album_name', 'genres', 'general_genre', 'explicit', 'popularity']
    table_data = filtered_df.select(selected_columns).to_pandas()
    table = cmp.create_table(table_data)
    return fig, table

if __name__ == '__main__':
    app.run_server(debug=False)
