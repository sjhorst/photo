def main_entry():
    import argparse

    description='Manage photos my way'
    parser = argparse.ArgumentParser(description=description)

    descr = 'The following sub-sommands will perform different photo actions.'
    action = parser.add_subparsers(title='Available Sub-Commands',
            help=descr,
            description=descr,
            dest='action',
            )
    action.required = True

    # TAG action: add a tag to a photo file
    # =====================================
    descr = 'Tag the photo or video with EXIF metadata'
    tag = action.add_parser('tag', help=descr, description=descr)

    tag.add_argument('filename', help='The filename to modify')
    tag.add_argument('tags', nargs=argparse.REMAINDER, action='store', help='The name of the tag(s) to add or subtract')

    # ADD action: add a photo to the repository
    # =========================================
    # The process action will take photos from an inbox and file it in the
    # photo repository
    descr = 'Process photos from the inbox and insert them in the repository'
    proc = action.add_parser('add', help=descr, description=descr)

    proc.add_argument('path', nargs="*", help='The directory or filenames to process')

    # META action: print the meta data for a photo
    # ============================================
    # Meta action will print meta data including tags to screen
    descr = 'Display meta data of a specified photo on screen'
    meta = action.add_parser('meta', help=descr, description=descr)

    meta.add_argument('fileglob', nargs='*', help='The filename or glob of photos or videos to show')

    # VERSION action: Print the version of the software and exit
    # ==========================================================
    descr = 'Print the current version of the tool and exit'
    ver = action.add_parser('version', help=descr, description=descr)

    # END action definition
    # Move on to parsing

    args = parser.parse_args()

    try:
        if args.action.lower() == 'tag':
            cli_tag(args.filename, args.tags)

        elif args.action.lower() == 'add':
            cli_add(args.path)

        elif args.action.lower() == 'meta':
            cli_meta(args.fileglob)

        elif args.action.lower() == 'version':
            from os.path import join, dirname
            import os
            import subprocess

            with open(join(dirname(__file__), 'version'), 'r') as fid:
                print('Photo Version: {0}'.format(fid.readline()))

        else:
            raise ValueError('Unrecognized action, "{0}"'.format(args.action))

    except Exception as err:
        raise


def cli_meta(fileglob):
    """
    Display meta data to screen

    """
    from .exif import list_metadata

    if isinstance(fileglob, str):
        fileglob = [fileglob]
    if len(fileglob) == 0:
        raise ValueError('No files found')

    count = 0
    for filename in fileglob:
        import pudb; pudb.set_trace()
        status = list_metadata(filename)
        if status == 0:
            count += 1

    print('Displayed meta data for {0} images'.format(count))
    return count


def cli_tag(filename, arg_list):
    """
    Add or remove EXIF tags from a file

    + or no prefix adds tags

    - removes tags

    Example:
    photo tag IMG2133.jpg +travel +steve -sailing

    """
    import subprocess
    from .exif import get_tags, update_tags

    if len(arg_list) == 0:
        raise ValueError('No tags provided')

    cur_tags = get_tags(filename)
    tag_list = []
    arg_list = arg_list.split(' ')
    for arg in arg_list:
        tag_elem = arg.split(',')
        for tag in tag_elem:
            if tag != '':
                tag_list.append(tag)

    for tag in tag_list:
        if tag[0] == '-':
            add_str = '-'
            tag_str = tag[1:]
        elif tag[0] == '+':
            add_str = '+'
            tag_str = tag[1:]
        else:
            add_str = '+'
            tag_str = tag

        if tag_str in cur_tags and add_str == '+':
            print('Tag already exists')
            continue
        elif tag_str not in cur_tags and add_str == '-':
            print('Tag does not exist')
            continue
        elif add_str == '+':
            cur_tags.append(tag_str)
        elif add_str == '-':
            cur_tags.remove(tag_str)
        else:
            raise ValueError('Malformed tag')

    update_tags(filename, cur_tags)


def cli_add(path):
    """
    Add photos to the directory repository

    Arguments
    ---------
    path : str
        The path of the data to process. Can be a filename, directory, or glob.

    """
    from pathlib import Path
    import os
    import shutil
    from .utilities import compute_photo_checksum, compute_video_checksum
    from .utilities import get_photo_date, get_video_date
    from .config import get_global_config
    from datetime import datetime
    from zoneinfo import ZoneInfo

    tzla = ZoneInfo("America/Los_Angeles")

    cfg = get_global_config()
    repo_path = Path(cfg["repo"]["path"])

    # Set up initial statistics
    added_files = 0
    duplicate_files = 0
    skipped_files = 0
    total_files = 0
    first_date = datetime.now(tzla)
    last_date = datetime(1970, 1, 1, tzinfo=tzla)

    # Process each file
    total_files = len(path)
    for file in path:
        file_obj = Path(file)
        if file_obj.is_dir():
            path_files = os.listdir(file_obj)
            import pudb; pudb.set_trace()

        if file_obj.suffix.upper() in [".AVI", ".MOV", ".MP4"]:
            # Compute the checksum of the file
            checksum = compute_video_checksum(file_obj)
            # Get the date the photo was taken
            date = get_video_date(file_obj)
        elif file_obj.suffix.upper() in [".JPG", ".JPEG", ".PNG", ".HEIC"]:
            # Compute the checksum of the file
            checksum = compute_photo_checksum(file_obj)
            # Get the date the photo was taken
            date = get_photo_date(file_obj)
        else:
            # File not recoginized as an image. Skip it.
            print(f"{file_obj} not recognized as an image file. Skipping.")
            skipped_files += 1
            continue

        if date is None:
            date = datetime(1970,1,1, tzinfo=tzla)

        # Check for earliest or latest date
        try:
            if date < first_date:
                first_date = date
            if date > last_date:
                last_date = date
        except:
            import pudb; pudb.set_trace()

        # Create new filename
        canonical_file = Path(f"{date.strftime("%y%m%d_%H%M%S")}_{checksum[:8]}{file_obj.suffix}")
        canonical_folder = Path(f"{date.year}/{date.month:02}")

        # Rename file to the new filename
        insert_path = repo_path / canonical_folder / canonical_file

        if not insert_path.exists():
            os.makedirs(repo_path / canonical_folder, exist_ok=True)
            shutil.copy2(file_obj, insert_path)
            print(f"Added {canonical_file} (from {file_obj}) to the photo repository")
            added_files += 1
        else:
            print(f"File {canonical_file} (from {file_obj}) already exists in the repository")
            duplicate_files += 1

    print("")
    print("Summary")
    print("=======")
    print(f"Processed {total_files} files from {first_date} to {last_date}")
    print(f"{added_files} files added to the photo repository")
    print(f"{duplicate_files} files skipped as duplicates")
    print(f"{skipped_files} files skipped as unrecognized format")
    print(f"{total_files - (added_files+duplicate_files+skipped_files)} files unaccounted")
