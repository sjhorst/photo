import pytest


@pytest.fixture(scope='session')
def root_dir(tmp_path_factory):
    tmp = tmp_path_factory.mktemp('testrepo')
    return tmp


def test_add_tags():
    """
    Test adding meta data tags to a file using the image description EXIF tag

    """
    import photo
    import os
    from os.path import dirname, join

    test_root = dirname(__file__)
    data_dir = join(test_root, 'data')
    test_img = join(data_dir, 'test_gopro_photo.jpg')

    # The photo should start with no tags present
    tags = photo.get_tags(test_img)
    assert tags == []

    # A list of strings defines the tags
    tag_list = ['one', 'two', 'mult word']
    photo.update_tags(test_img, tag_list)

    # The file should now have three tags associated with it
    tags = photo.get_tags(test_img)
    assert tags == ['one', 'two', 'mult word']

    # To remove tags, you must update the list without an element
    tag_list.remove('two')
    photo.update_tags(test_img, tag_list)
    tags = photo.get_tags(test_img)
    assert tags == ['one', 'mult word']

    # Tags can support any character except commas
    tag_list.append('!@#$-_%^&*().')
    photo.update_tags(test_img, tag_list)
    tags = photo.get_tags(test_img)
    assert tags == ['one', 'mult word', '!@#$-_%^&*().']

    # Comma characters will be replaced by a period
    tag_list.append('bad, tag')
    photo.update_tags(test_img, tag_list)
    tags = photo.get_tags(test_img)
    assert tags == ['one', 'mult word', '!@#$-_%^&*().', 'bad. tag']

    # Return the file to starting position with no tags
    photo.update_tags(test_img, [])
    tags = photo.get_tags(test_img)
    assert tags == []


def test_search_tags():
    """
    Test the ability to search for a specific tag

    """
    import photo
    import os
    from os.path import dirname, join

    test_root = dirname(__file__)
    data_dir = join(test_root, 'data')
    test_img = join(data_dir, 'test_gopro_photo.jpg')

    # Place some tags into an image
    tag_list = ['home', 'travel', 'baseball']
    photo.update_tags(test_img, tag_list)
    tags = photo.get_tags(test_img)
    assert tags == ['home', 'travel', 'baseball']

    assert photo.search_tags(test_img, 'baseball') == True
    assert photo.search_tags(test_img, 'football') == False
    assert photo.search_tags(test_img, 'home') == True
    assert photo.search_tags(test_img, 'home ') == False

    # Return the file to starting position with no tags
    photo.update_tags(test_img, [])
    tags = photo.get_tags(test_img)
    assert tags == []


def test_cli_tag():
    """
    Test the CLI interface for modifying tags

    """
    from photo.cli import cli_tag
    import photo
    import os
    from os.path import dirname, join

    test_root = dirname(__file__)
    data_dir = join(test_root, 'data')
    test_img = join(data_dir, 'test_gopro_photo.jpg')

    # Create tags 
    cli_tag(test_img, '+family greg +bob')
    cur_tags = photo.get_tags(test_img)
    assert cur_tags == ['family', 'greg', 'bob']

    # Subtract tags with - character
    cli_tag(test_img, 'karen -family')
    cur_tags = photo.get_tags(test_img)
    assert cur_tags == ['greg', 'bob', 'karen']

    # Duplicate tags are skipped
    cli_tag(test_img, '+bob')
    cur_tags = photo.get_tags(test_img)
    assert cur_tags == ['greg', 'bob', 'karen']

    cli_tag(test_img, '+lan lan')
    cur_tags = photo.get_tags(test_img)
    assert cur_tags == ['greg', 'bob', 'karen', 'lan']

    # Comma characters are removed to make them equivalent to spaces
    cli_tag(test_img, '-lan,-bob')
    cli_tag(test_img, '-greg, nick , paul')
    cur_tags = photo.get_tags(test_img)
    assert cur_tags == ['karen', 'nick', 'paul']

    # Attempting to remove tags that don't exist get ignored
    cli_tag(test_img, '-nick -robert')
    cur_tags = photo.get_tags(test_img)
    assert cur_tags == ['karen', 'paul']

    # Return the file to starting position with no tags
    photo.update_tags(test_img, [])
    tags = photo.get_tags(test_img)
    assert tags == []


