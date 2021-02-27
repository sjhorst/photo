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

    result = subprocess.check_output(['exiftool', filename, '-imagedescription'])
    if result != bytes():
        # Current tags exist
        raw_str = result.decode('utf-8')
        values = re.search('(?<=: ).*(?=\n)$', raw_str)
        cur_tags = values.group(0).split(',')
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

    # Delete existing tags
    subprocess.run(['exiftool', filename, '-imagedescription='])
    # Convert tag_list to string
    tag_str = ','.join(tag_list)
    # Write out new tags
    subprocess.run(['exiftool', filename, '-imagedescription={0}'.format(tag_str)])
