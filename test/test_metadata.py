import pytest


def test_metadata_list(capsys):
    """
    Ensure different types of photos all ave the necessary metadata

    """
    import photo
    import os
    from os.path import dirname, join

    test_root = dirname(__file__)
    data_dir = join(test_root, 'data')
    samples = os.listdir(data_dir)

    for img in samples:
        photo.list_metadata(join(data_dir, img))
        stdout, stderr = capsys.readouterr()
        if img == 'test_not_photo.txt':
            assert stdout == ''
        else:
            assert stdout != ''
        assert stderr == ''


def test_cli_meta():
    """
    Test the meta cli interface

    """
    from photo.cli import cli_meta
    from os.path import dirname, join
    import os
    import glob

    test_root = dirname(__file__)
    data_dir = join(test_root, 'data')
    samples = os.listdir(data_dir)

    # Test a single image
    count = cli_meta([join(data_dir, samples[0])])
    assert count == 1

    # Attempting to run on a file that doesn't exist returns an error
    with pytest.raises(IOError):
        cli_meta(['fake_photo.jpg'])

    # Attempting a filename that does exist but not in the correct directory
    # should also error out
    with pytest.raises(IOError):
        cli_meta([samples[0]])

    # Glob searches should also work for the entire directory
    fileglob = glob.glob(join(data_dir, '*'))
    count = cli_meta(fileglob)
    assert count == 6

    # Glob searches should also work for specifics
    fileglob = glob.glob(join(data_dir, '*.jpg'))
    count = cli_meta(fileglob)
    assert count == 5
