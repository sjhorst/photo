def sha1_hash(filename):
    import hashlib

    hash_sha1 = hashlib.sha1()
    with open(filename, 'rb') as fid:
        for chunk in iter(lambda: fid.read(4096), b""):
            hash_sha1.update(chunk)

    return hash_sha1.hexdigest()

def compute_image_checksum(image_path):
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
    else:
        # Open the image file
        with Image.open(image_path) as img:
            img_data = np.array(img)
    
    # Ensure the image data is in a consistent format
    img_data = img_data.tobytes()
        
    # Compute the checksum using hashlib (e.g., SHA-256)
    checksum = hashlib.sha256(img_data).hexdigest()
    
    return checksum

def get_photo_date(image_path):
    """
    Get the date a photo was taken from the meta data

    """
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    from datetime import datetime

    # Open the image file
    with Image.open(image_path) as img:
        # Get EXIF data
        exif_data = img._getexif()

        if not exif_data:
            return None

        # Extract the date taken from EXIF data
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'DateTimeOriginal':
                timestamp = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                return timestamp

        # If DateTimeOriginal tag is not found
        return None

