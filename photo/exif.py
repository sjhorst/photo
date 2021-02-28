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
        raise IOError('Requested filename does not exist')

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
