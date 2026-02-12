def filter_record(record):
    if any(v is None or v == "" for v in record.values()):
        return None
    return record
