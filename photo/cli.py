def main_entry():
    import argparse

    description='Manage photos my way'
    parser = argparse.ArgumentParser(description=description)

    action = parser.add_subparsers(title='Available Sub-Commands',
            description='The following sub-sommands will perform different photo actions.',
            dest='action',
            )
    action.required = True

    # Parser information for the check action
    descr = 'Tag the photo or video with EXIF metadata',
    tag = action.add_parser('tag', help=descr, description=descr)

    tag.add_argument('tags', nargs='*', help='The name of the tag to add or subtract')

    # The process action will take photos from an inbox and file it in the
    # photo repository
    descr = 'Process photos from the inbox and insert them in the repository'
    proc = action.add_parser('process', help=descr, description=descr)

    # Meta action will print meta data including tags to screen
    descr = 'Display meta data of a specified photo on screen'
    meta = action.add_parser('meta', help=descr, description=descr)

    meta.add_argument('fileglob', help='The filename or glob of photos or videos to show')

    args = parser.parse_args()

    try:
        if args.action.lower() == 'tag':
            pass
        elif args.action.lower() == 'process':
            pass
        elif args.action.lower() == 'meta':
            pass
        else:
            raise ValueError('Unrecognized action, "{0}"'.format(args.action))

    except Exception as err:
        raise
