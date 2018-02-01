from decimal import Decimal
from geopy.distance import great_circle  # or distance
from seuapp.models import Store

# decimal places   degrees          distance
# ---------------  -------          --------
# 0                1                111  km
# 1                0.1              11.1 km
# 2                0.01             1.11 km
# 3                0.001            111  m
# 4                0.0001           11.1 m
# 5                0.00001          1.11 m
# 6                0.000001         11.1 cm
#
# Model fields must looks like:
# # lat/long with 6 decimal places lead to precision of ~0.11 meters.
# lat = DecimalField(
#     max_digits=10, decimal_places=6,
#     validators=[
#         MinValueValidator(
#             -90, _("Latitude values must be greater than -90.")
#         ),
#         MaxValueValidator(90, _("Latitude values must be lower than 90."))
#     ]
# )
# lng = DecimalField(
#     max_digits=10, decimal_places=6,
#     validators=[
#         MinValueValidator(
#             -180, _("Longitude values must be greater than -180.")
#         ),
#         MaxValueValidator(
#             180, _("Longitude values must be lower than 180.")
#         )
#     ]
# )
PRECISION_MAP = {
    0: Decimal('1.0'),      # -/+ 111  km
    1: Decimal('0.1'),      # -/+ 11.1 km
    2: Decimal('0.01'),     # -/+ 1.11 km
    3: Decimal('0.001'),    # -/+ 111  m
    4: Decimal('0.0001'),   # -/+ 11.1 m
    5: Decimal('0.00001'),  # -/+ 1.11 m
    6: Decimal('0.000001')  # -/+ 11.1 cm
}


def find_nearest_storen(lat, lng):
    """
    Find nearest store to given latitude/longitude.
    """
    store = None
    precison = 6
    while store is None:
        results = {}  # dict is already sorted from lower to greater ;)
        # now I would love a graph database ;)
        _range = PRECISION_MAP[precison]
        stores = Store.objects.filter(
            # Here we search around a range. 9 is a modifier in _range to
            # be a bit more wide, specially in depth precisions. More stations
            # per loop means less queries.
            lat__gt=lat - (_range * 9), lat__lt=lat + (_range * 9),
            lng__gt=lng - (_range * 9), lng__lt=lng + (_range * 9)
        )

        for _store in stores:
            d = great_circle((lat, lng), (_store.lat, _store.lng))
            results[d] = _store

        if results:
            store = results.values()[0]
            break
        else:
            precison -= 1

    return store
