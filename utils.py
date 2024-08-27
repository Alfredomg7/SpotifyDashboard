def format_label(label):
    if label == 'duration_min':
        return 'Duration'
    return ' '.join([word.capitalize() for word in label.split('_')])
def convert_ms_to_min(ms):
    return ms / 60000

def convert_hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip('#')
    rgb_tuple = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]}, {alpha})"

def get_avg_metrics(metric_columns, all_data_df, histogram_df):
    avg_metrics = {}
    for col in metric_columns:
        if col != 'count':
            avg_metrics[col] = all_data_df[col].mean()
        else:
            avg_metrics[col] = histogram_df[col].mean()
        avg_metrics[col] = round(avg_metrics[col], 2)
    return avg_metrics