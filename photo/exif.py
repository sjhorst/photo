def list_metadata(filename):
    """
    Print the relevant metadata to screen

    Arguments
    ---------
    filename : str
        The filename of the photo or video to show metadata 

    Returns
    -------
    int
        A code for success of the operation. 0 is successful and non 0 is
        unsuccessful.

    """
    import subprocess
    from os.path import exists

    if not exists(filename):
        raise IOError('Requested file does not exist')

    valid_ext = ['jpg', 'png', 'gif', 'mov', 'mpg', 'avi']
    file_ext = filename.split('.')[-1]
    if file_ext.lower() in valid_ext:
        subprocess.run(['exiftool', '-common', '-imagedescription', filename])
        print('')
        return 0
    else:
        return -1


def get_metadata(filename, tag):
    """
    Retrieve a specified metadata tag

    Arguments
    ---------
    filename : str
        The filename from which to extract

    tag : str
        The tag name to extract

    Returns
    -------
    str
        The content of the EXIF metadata

    """
    import subprocess
    import re
    from os.path import exists

    if not exists(filename):
        raise IOError('Requested file does not exist')

    stdout = subprocess.check_output(['exiftool', filename, '-{0}'.format(tag)])
    if stdout == bytes():
        result = None
    else:
        raw_str = result.decode('utf-8')
        values = re.search('(?<=: ).*(?=\n)$', raw_str)
        result = values.group(0)

    return result


def get_tags(filename):
    """
    Get the tags stored by the photo tool

    This is a custom use of the ImageDescription field

    Arguments
    ---------
    filename : str
        The filename of the photo to retrieve data from

    """
    import subprocess
    import re
    from os.path import exists

    if not exists(filename):
        raise IOError('Requested file does not exist')

    result = subprocess.check_output(['exiftool', filename, '-imagedescription'])
    if result != bytes():
        # Current tags exist
        raw_str = result.decode('utf-8')
        values = re.search('(?<=: ).*(?=\n)$', raw_str)
        if values.group(0) != '':
            cur_tags = values.group(0).split(',')
        else:
            cur_tags = []
    else:
        cur_tags = []

    return cur_tags


def update_tags(filename, tag_list):
    """
    Add a tag to a photo via EXIF data

    This is a custom use of the ImageDescription field

    Arguments
    ---------
    filename : str
        The filename of the photo to edit

    tag_list : list
        A list of strings for the photo tags

    """
    import subprocess
    from os.path import exists

    if not exists(filename):
        raise IOError('Requested file does not exist')

    # Make sure no comma characters are present in tags
    for idx in range(len(tag_list)):
        tag_list[idx] = tag_list[idx].replace(',', '.')

    # Convert tag_list to string
    tag_str = ','.join(tag_list)
    # Write out new tags
    subprocess.run(['exiftool', 
                    filename, 
                    '-overwrite_original',
                    '-imagedescription={0}'.format(tag_str)])


def search_tags(filename, tag_name):
    """
    Search for a tag within a file

    There are currently no wilcard characters

    Arguments
    ---------
    filename : str
        The filename to search for tags

    tag_name : str
        The tag name to search for

    Returns
    -------
    bool
        The result of the search. True if the tag is present.

    """
    tags = get_tags(filename)
    if tag_name in tags:
        return True
    else:
        return False


def get_filename(filename, fmt=''):
    """
    Get a standardized file name for the photo

    Arguments
    ---------
    filename : str
        The current filename of the photo or video

    Keyword Arguments
    -----------------
    fmt : str
        The format to use for the filename. Typically pulled from the
        preferences settings in the configuration file.

    Returns
    -------
    tuple
        A tuple of the result, first value is a string of the new filename
        while the second value is a list of the directory within the repository

    """
    import subprocess
    import re
    from datetime import datetime
    from os.path import exists
    from .utilities import sha1_hash

    if not exists(filename):
        raise IOError('Requested file does not exist')

    tag_names = ['-CreateDate',
                 '-Model',
                ]

    stdout = subprocess.check_output(['exiftool', filename]+tag_names)
    if stdout == bytes():
        name = None
        loc = None
    else:
        raw_str = stdout.decode('utf-8')
        create_date_match = re.search('(?<=Create Date)[\s:]*(.*)(?=\n)', raw_str)
        if create_date_match is not None:
            create_date = datetime.strptime(create_date_match.group(1), '%Y:%m:%d %H:%M:%S')
        else:
            raise ValueError('No creation date. Cannot create filename.')
        camera_model_match = re.search('(?<=Camera Model Name)[\s:]*(.*)(?=\n)', raw_str)
        if camera_model_match is not None:
            camera_model = camera_model_match.group(1)
        else:
            camera_model_match = re.search('(?<=Model)[\s:]*(.*)(?=\n)', raw_str)
            if camera_model_match is not None:
                camera_model = camera_model_match.group(1)
            else:
                camera_model = 'unknown'

        ext = filename.split('.')[-1]

        sha1 = sha1_hash(filename)
        name = '{0}_{1}_{2}.{3}'.format(create_date.strftime('%Y%b%d_%H:%M:%S'), 
                                    camera_model.replace(' ', '_'),
                                    sha1[:6],
                                    ext) 
        loc = [create_date.strftime('%Y'), create_date.strftime('%m')]

    return name, loc


def calculate_checksum(image_path):
    """
    Calculate the checksum on an image

    This computes the checksum only on the image data, not on the meta data.
    This allows you to add tags and otherwise alter meta data but still know
    that the underlying image is identical to another in the repo already

    Arguments
    ---------
    image_path : str
        The path to the image to be computed

    Returns
    -------
    str
        The checksum of the image being computed

    """
    import hashlib
    from PIL import Image

    # Open the image using Pillow
    img = Image.open(image_path)

    # Get the image data (content only, no metadata)
    image_data = list(img.getdata())

    # Calculate the MD5 hash of the image content
    md5_hash = hashlib.md5()
    for pixel in image_data:
        if hasattr(pixel, 'tobytes'):  # Check if pixel is a tuple
            md5_hash.update(pixel.tobytes())
        else:  # Pixel is a single value (e.g., RGB or grayscale)
            md5_hash.update(str(pixel).encode('utf-8'))

    return md5_hash.hexdigest()
