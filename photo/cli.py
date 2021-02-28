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

    # Parser information for the check action
    descr = 'Tag the photo or video with EXIF metadata'
    tag = action.add_parser('tag', help=descr, description=descr)

    tag.add_argument('filename', help='The filename to modify')
    tag.add_argument('tags', nargs=argparse.REMAINDER, action='store', help='The name of the tag(s) to add or subtract')

    # The process action will take photos from an inbox and file it in the
    # photo repository
    descr = 'Process photos from the inbox and insert them in the repository'
    proc = action.add_parser('process', help=descr, description=descr)

    # Meta action will print meta data including tags to screen
    descr = 'Display meta data of a specified photo on screen'
    meta = action.add_parser('meta', help=descr, description=descr)

    meta.add_argument('fileglob', nargs='*', help='The filename or glob of photos or videos to show')

    descr = 'Print the current version of the tool and exit'
    ver = action.add_parser('version', help=descr, description=descr)

    args = parser.parse_args()

    try:
        if args.action.lower() == 'tag':
            cli_tag(args.filename, args.tags)

        elif args.action.lower() == 'process':
            pass

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
