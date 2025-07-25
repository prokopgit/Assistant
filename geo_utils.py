import exifread

def extract_geo_from_photo(path: str):
    try:
        with open(path, 'rb') as f:
            tags = exifread.process_file(f)

        def get_decimal(coord, ref):
            d, m, s = [float(x.num) / float(x.den) for x in coord.values]
            result = d + m / 60 + s / 3600
            return -result if ref in ['S', 'W'] else result

        lat = tags.get('GPS GPSLatitude')
        lat_ref = tags.get('GPS GPSLatitudeRef')
        lon = tags.get('GPS GPSLongitude')
        lon_ref = tags.get('GPS GPSLongitudeRef')

        if lat and lon and lat_ref and lon_ref:
            latitude = get_decimal(lat, lat_ref.values[0])
            longitude = get_decimal(lon, lon_ref.values[0])
            return (latitude, longitude)

    except Exception as e:
        print(f"❌ EXIF error: {e}")
    return None