class GPolyDecoder(object):
    def decode(self, encodedString):
        index = 0
        length = len(encodedString)
        lat = 0
        lng = 0
        poly_lines = []

        while index < length:
            b = 0
            shift = 0
            result = 0
            while True:
                char = encodedString[index]
                index += 1
                b = ord(char) - 63
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break

            dlat = 0
            if (result & 1) != 0:
                dlat = ~(result >> 1)
            else:
                dlat = (result >> 1)
            lat += dlat
            shift = 0
            result = 0
            while True:
                char = encodedString[index]
                index += 1
                b = ord(char) - 63
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break

            dlng = 0
            if (result & 1) != 0:
                dlng = ~(result >> 1)
            else:
                dlng = (result >> 1)

            lng += dlng
            poly_lines.append(((long(lat) / 1E5), (long(lng) / 1E5)))

        return poly_lines