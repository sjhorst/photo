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


def test_filename_creation():
    """
    Test using the metadata to create a standardized filename

    """
    import photo
    from os.path import dirname, join
    import os

    test_root = dirname(__file__)
    data_dir = join(test_root, 'data')
    samples = os.listdir(data_dir)

    for img in samples:
        name, loc = photo.get_filename(join(data_dir, img))
        
        if img == 'test_canon_photo.jpg':
            assert name == '2018Feb17_01:41:09_Canon_EOS_REBEL_T2i_6e55db.jpg'
            assert loc == ['2018', '02']
        elif img == 'test_gopro_photo.jpg':
            assert name == '2020Oct18_00:00:00_unknown_866525.jpg'
            assert loc == ['2020', '10']
        elif img == 'test_iphone_photo.jpg':
            assert name == '2015Oct17_14:06:28_iPhone_5s_1e0440.jpg'
            assert loc == ['2015', '10']
        elif img == 'test_iphone_video.mov':
            assert name == '2016Aug10_17:17:36_iPhone_5s_cdbaf7.mov'
            assert loc == ['2016', '08']
        elif img == 'test_unknown_photo.jpg':
            assert name == '2020Oct18_00:00:00_DSC-H20_0b2b0a.jpg'
            assert loc == ['2020', '10']
        elif img == 'test_scanned_photo.jpg':
            assert name is None
            assert loc is None
