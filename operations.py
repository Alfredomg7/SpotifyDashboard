import polars as pl

def calculate_difference(bin_df, metric, overall_avg):
    bin_avg = bin_df[0, metric]
    if bin_avg == 0:
        difference = -100
    else:
        difference = ((bin_avg - overall_avg) / overall_avg) * 100
    return round(difference, 2)

def count_by_category(df, category, alias='count'):
    total_count = df.height
    count_by_category_df = (
        df.lazy()
        .group_by(category)
        .agg([(pl.count("track_id") / total_count * 100).alias(alias)])
        .sort(alias)
        .collect()
    )
    return count_by_category_df