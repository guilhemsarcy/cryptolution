"""Settings for data collection from Kraken."""

COLLECTION_SETTINGS = {
    'query_period_in_minutes': '1440',
    'max_number_of_items': 400,
    'storage_path': 's3://cryptolution/data.csv'  # here you have to specify your own storage path
}

mapping_status = {
    'fresh': 'success',
    'half_fresh': 'warning',
    'rotten': 'danger'
}
