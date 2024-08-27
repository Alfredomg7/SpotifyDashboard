from dash import html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from utils import format_label, convert_hex_to_rgba
import polars as pl

PRIMARY_COLOR = '#1DB954'
SECONDARY_COLOR = '#95e037'
PRIMARY_COLOR_RGBA = convert_hex_to_rgba(PRIMARY_COLOR, alpha=0.5)
BACKGROUND_COLOR = '#191414'
ALTERNATIVE_COLOR = '#1f1E1E'

def create_tabs(id, options):
    tabs = dbc.Tabs(id=id, 
                    children=[
                        dbc.Tab(
                            label=format_label(option), 
                            tab_id=option,
                            tab_style={'background-color': ALTERNATIVE_COLOR},
                            label_style={'color': PRIMARY_COLOR, 'font-size': '18px', 'font-weight': '500'},
                            active_label_style={'color': 'white', 'background-color': PRIMARY_COLOR}
                            )
                            for option in options
                        ],
                    active_tab=options[0],
                    className='nav-pills justify-content-center',
                    style={'border': 'none'}
                    )
    return tabs

def create_card(text_id, title_id=None):
    card_style = {
    "background-color": ALTERNATIVE_COLOR,
    "border": "none",
    "box-shadow": f"4px 4px 8px {PRIMARY_COLOR_RGBA}",
    "transition": "transform 0.2s"
    }
    if title_id:
        card_body = [
            html.H5(id=title_id, className="card-title text-white text-center mb-3"),
            html.H3(id=text_id, className="card-text text-center", style={'color': PRIMARY_COLOR})
        ]
    if not title_id:
        card_body = [
            html.H6(id=text_id, className='card-text text-center text-white')
        ]
    card = dbc.Card(
        dbc.CardBody(card_body),
        className="p-2 w-100 h-100",
        style=card_style
    )
    return card

def create_difference_text(popularity_bin, difference, metric):
    difference_style = {
        'color': PRIMARY_COLOR,
        'font-weight': 'bold',
        'font-size': '18px'
    }

    first_sentence = ''
    if popularity_bin == '0-25':
        first_sentence = f"Least popular tracks ({popularity_bin}) have"
    elif popularity_bin == '75-100':
        first_sentence = f"Most popular tracks ({popularity_bin}) have"
    
    comparison_text = ''
    if difference > 0:
        comparison_text = f" {difference}% higher"
    elif difference < 0:
        comparison_text = f" {abs(difference)}% lower"
    else:
        comparison_text = " the same"
    
    return html.Div([
        html.H6(first_sentence),
        html.Span(comparison_text, style=difference_style),
        html.H6(f" {format_label(metric).lower()} than the overall average.")
    ])

def style_fig(fig, axis='y'):
    if axis == 'y':
        y_min = min([trace.y.min() for trace in fig.data])
        y_max = max([trace.y.max() for trace in fig.data])
        fig.update_yaxes(range=[min(0, y_min * 1.20), y_max * 1.20])

    elif axis == 'x':
        x_min = min([trace.x.min() for trace in fig.data])
        x_max = max([trace.x.max() for trace in fig.data])
        fig.update_xaxes(
            range=[min(0, x_min * 1.20), x_max * 1.20],
            showticklabels=False
        )
        
    fig.update_layout(
        title={
            'x': 0.5, 
            'xanchor': 'center', 
            'yanchor': 'top', 
            'font': {
                'size': 20,
                'color': PRIMARY_COLOR,
                'family': 'Arial, sans-serif',
            }
        },
        xaxis=dict(
            titlefont=dict(
                size=16,
                color=PRIMARY_COLOR,
                family='Arial, sans-serif',
            ),
            tickfont=dict(
                size=14,
                color=PRIMARY_COLOR,
                family='Arial, sans-serif',
            ),
            title_standoff=15,
            showline=True,
            linewidth=2,
            linecolor=PRIMARY_COLOR
        ),
        yaxis=dict(
            titlefont=dict(
                size=16,
                color=PRIMARY_COLOR,
                family='Arial, sans-serif',
            ),
            tickfont=dict(
                size=14,
                color=PRIMARY_COLOR,
                family='Arial, sans-serif',
            ),
            title_standoff=15,
            showline=True,
            linewidth=2,
            linecolor=PRIMARY_COLOR
        )
    )

def create_custom_histogram(df, x, y):
    title = f'Average {format_label(y)} by Popularity' if y != 'count' else 'Track Count by Popularity'
    x_label = format_label(x)
    y_label = f'Average {format_label(y)}' if y != 'count' else 'Count'
    if y == 'duration_min':
        y_label += ' (min)'

    fig = px.bar(
        df, 
        x=x, 
        y=y, 
        color_discrete_sequence=[PRIMARY_COLOR], 
        title=title, 
        labels={x: x_label, y: y_label},
        template='plotly_dark'
        )
    
    style_fig(fig)
    
    text_template = '%{y}'
    fig.update_traces(
    texttemplate=text_template, 
    textposition='outside',
    textfont=dict(
        size=16, 
        color=PRIMARY_COLOR, 
        family='Arial, sans-serif',
        weight='bold'
    ),
    hovertemplate=text_template, 
)
    return fig

def create_butterfly_chart(df, x1, x2, y):
    title = f'Track Count by {format_label(y)}'
    df = df.with_columns(
        ((pl.col(x1) * -1).alias(f'neg_{x1}'))
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[f'neg_{x1}'],
        y=df[y],
        orientation='h',
        name=format_label(x1),
        marker=dict(color=PRIMARY_COLOR)
        )
    )
    fig.add_trace(go.Bar(
        x=df[x2],
        y=df[y],
        orientation='h',
        name=format_label(x2),
        marker=dict(color=SECONDARY_COLOR)
        )
    )
    for trace in fig.data:
        trace.update(
            texttemplate=['<b>{}%</b>'.format(abs(round(x, 2))) if x < 0 else '{:.1f}%'.format(x) for x in trace.x],
            textposition='outside',
            textfont=dict(
                size=16,
                color=PRIMARY_COLOR if trace.x.min() < 0 else SECONDARY_COLOR,
                family='Arial, sans-serif',
                weight='bold'
            ),
            hovertemplate='%{y}'
        )

    fig.update_layout(
        title=title,
        barmode='overlay',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        bargap=0.1,
        bargroupgap=0,
        template='plotly_dark',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(
                size=14,
            )
        )            
    )
    
    style_fig(fig, axis='x')

    return fig

def create_table(df):
    table = dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': format_label(col), 'id': col} for col in df.columns],
                style_header={
                    'backgroundColor': PRIMARY_COLOR,
                    'color': '#FFF',
                    'fontWeight': 'bold',
                    'borderBottom': '2px solid #FFF',
                    'textAlign': 'center',
                    'padding': '10px'
                },
                style_cell={
                    'backgroundColor': ALTERNATIVE_COLOR,
                    'color': '#FFF',
                    'border': '1px solid #ddd',
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal'
                },
                style_table={
                    'overflowX': 'auto',
                    'border': '1px solid #ccc',
                    'boxShadow': '0px 2px 8px rgba(0, 0, 0, 0.1)'
                },
                style_data_conditional=[
                    {
                        'if': {'state': 'active'},
                        'backgroundColor': PRIMARY_COLOR,
                        'border': 'none'
                    }
                ],
                style_data={
                    'border': '1px solid #ccc',
                },

                page_size=10,
                style_as_list_view=True,
            )
    return table
    
def create_footer():
    link_style = {
    'color': PRIMARY_COLOR,
    'font-weight': 'bold',
    'font-size': '16px',
    'text-decoration': 'none'
    }
    footer = html.Footer(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.A(
                            "Source Code",
                            href="https://github.com/Alfredomg7/spotify-dashboard",
                            target="_blank",
                            style=link_style
                        ),
                        className='text-center'
                    ),
                    dbc.Col(
                        html.A(
                            "Data Source",
                            href="https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset/data",
                            target="_blank",
                            style=link_style
                        ),
                        className='text-center'
                    ),
                ],
                className='justify-content-center',
            )
        ],
        className='py-3',
        style={
            'background-color': BACKGROUND_COLOR,
            'position': 'fixed',
            'bottom': '0',
            'width': '100%',
            'box-shadow': f"0px 0px 8px {PRIMARY_COLOR_RGBA}",
            'z-index': '1000'
        }
    )
    return footer
                    

            
                    