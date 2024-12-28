def sha1_hash(filename):
    import hashlib

    hash_sha1 = hashlib.sha1()
    with open(filename, 'rb') as fid:
        for chunk in iter(lambda: fid.read(4096), b""):
            hash_sha1.update(chunk)

    return hash_sha1.hexdigest()

def compute_photo_checksum(image_path):
    """
    Compute the image hash on the picture data only

    Does not include image meta data which can change

    Arguments
    ---------
    image_path : path_like
        The location of the image file

    Returns
    -------
    str
        The hash of the image data

    """
    import hashlib
    from PIL import Image
    import numpy as np
    import pyheif
    #  import imageio

    if image_path.suffix.upper() == ".HEIC":
        #  image = imageio.imread(image_path)
        heif_file = pyheif.read(image_path)

        # Convert the HEIC image to a Pillow Image
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )

        # Convert the image to a numpy array
        img_data = np.array(image)
    elif image_path.suffix.upper() in [".JPG", ".PNG", ".JPEG"]:
        # Open the image file
        with Image.open(image_path) as img:
            img_data = np.array(img)
    else:
        raise TypeError(f"Unrecognized photo type {image_path.suffix}")
    
    # Ensure the image data is in a consistent format
    img_data = img_data.tobytes()
        
    # Compute the checksum using hashlib (e.g., SHA-256)
    checksum = hashlib.sha256(img_data).hexdigest()
    
    return checksum


def compute_video_checksum(image_path):
    return sha1_hash(image_path)


def get_photo_date(image_path):
    """
    Get the date a photo was taken from the meta data

    """
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    from datetime import datetime
    import pyheif
    import piexif

    if image_path.suffix.upper() == ".HEIC":
        heif_file = pyheif.read(image_path)
        metadata = heif_file.metadata or []

        # Look for the XML metadata
        for meta in metadata:
            if meta['type'].lower() == 'exif':
                # Load the EXIF data
                exif_dict = piexif.load(meta["data"])
                
                # Get the DateTimeOriginal tag value
                date_id = piexif.ExifIFD.DateTimeOriginal
                if date_id in exif_dict['Exif']:
                    exif_date = exif_dict['Exif'][date_id]
                    if exif_date:
                        return datetime.strptime(exif_date.decode("UTF-8"), "%Y:%m:%d %H:%M:%S")

    elif image_path.suffix.upper() in [".JPG", ".PNG", ".JPEG"]:
        # Open the image file for 
        with Image.open(image_path) as img:
            # Get EXIF data
            exif_data = img.getexif()

        # Extract the date taken from EXIF data
        for tag, value in exif_data.items():
            if tag in TAGS:
                if TAGS[tag] in ['DateTime', 'DateTimeOriginal']:
                    timestamp = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    return timestamp

    else:
        raise TypeError(f"Unrecognized photo type {image_path.suffix}")

    # If Date metadata is not found
    return None


def get_video_date(video_path):
    import os
    from datetime import datetime
    from hurry.filesize import size
    from pymediainfo import MediaInfo

    # Function to read metadata from a MOV video
    media_info = MediaInfo.parse(video_path)

    for track in media_info.tracks:
        if track.track_type == "General":
            if track.comapplequicktimecreationdate is not None:
                timestamp = datetime.strptime(track.comapplequicktimecreationdate,
                                            "%Y-%m-%dT%H:%M:%S%z")
            elif track.encoded_date is not None:
                timestamp = datetime.strptime(track.encoded_date,
                                            "%Y-%m-%d %H:%M:%S UTC")
            elif track.tagged_date is not None:
                timestamp = datetime.strptime(track.tagged_date,
                                            "%Y-%m-%d %H:%M:%S UTC")
            else:
                import pudb; pudb.set_trace()
            return timestamp

    # If nothing found
    return None


# Function to read the EXIF date from an HEIC photo
def get_exif_date(image_path):
    try:
        heif_file = pyheif.read(image_path)
        metadata = heif_file.metadata or []
        
        # Look for the XML metadata
        for meta in metadata:
            if meta['type'] == 'Exif':
                xml_data = meta['data'].decode('utf-8')
                
                # Parse the XML data
                root = ET.fromstring(xml_data)
                
                # Extract the DateTimeOriginal tag value
                namespaces = {'x': 'http://ns.adobe.com/exif/1.0/'}
                date_time_original = root.find('.//x:DateTimeOriginal', namespaces)
                
                if date_time_original is not None:
                    return date_time_original.text
        return 'EXIF date not found'
    except Exception as e:
        return f'Error: {e}'

# Example usage
# print(get_exif_date('path_to_your_image.heic'))
