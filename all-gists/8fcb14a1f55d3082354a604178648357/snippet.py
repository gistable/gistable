def daterange_overlap(range1, range2):
    """returns the overlapping DateRange of 2 DateRanges, DateRange(None, None) if no overlap"""
    lower = max([range1.lower or datetime.date.min, range2.lower or datetime.date.min])
    upper = min([range1.upper or datetime.date.max, range2.upper or datetime.date.max])
    return DateRange(None if lower == datetime.date.min else lower, None if upper == datetime.date.max else upper)


def daterange_days(date_range):
    return (date_range.upper - date_range.lower).days