def decode_google_polyline(encoded):
    """
    Decode a google polyline string into a list of coordinates.
    See http://code.google.com/apis/maps/documentation/utilities/polylinealgorithm.html
    """
    raw_numbers = [ord(c) - 63 for c in encoded[::-1]]

    current_number = 0
    sequence = []

    def append_number(num):
        result = num >> 1
        if num & 1:
            result = ~result
        sequence.append(float(result) / 1e5)

    for i, num in enumerate(raw_numbers):
        if num < 0x20 and i:
            append_number(current_number)
            current_number = 0
        current_number = (current_number << 5) + (num & 0x1f)
    append_number(current_number)

    sequence.reverse()
    points = [tuple(sequence[:2])]
    for i in range(2, len(sequence), 2):
        points.append((points[-1][0] + sequence[i],
                       points[-1][1] + sequence[i + 1]))
    return points