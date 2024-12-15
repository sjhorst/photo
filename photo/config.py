"""
Global configuration interface
"""

# the canonical contents of the {photorc} configuration file
# it is a map of variable names to their default values and documentation
cfgmap = {
    # Information on the transaction register location
    "repo": {
        # The path where the register file can be found
        "path": "/Users/sjhorst/photo_test",
        # the documentation
        "doc": [
            "# The file location of transaction resister information",
        ],
    },
}


def locate_global_config():
    """
    Locate the global configuration file

    Checks the following locations, in order:
      - $XDG_CONFIG_HOME//photo/photorc
      - ~/.config/photo/photorc

    Returns
    -------
      str | None
        the location of the configuration file
    """
    # support
    import os

    # check whether the user environment is XDG compliant
    cfg_dir = os.getenv("XDG_CONFIG_HOME")
    # if not
    if not cfg_dir:
        # fall back to '~/.config'
        home_dir = os.path.expanduser(path="~")
        # if, for any reason, the expansion has failed
        if home_dir.startswith("~"):
            # bail
            return
        # form the path to the configuration directory
        cfg_dir = os.path.join(home_dir, ".config")

    # form the full path to the configuration file
    rc_file = os.path.join(cfg_dir, "photo", "photorc")
    # if it doesn't exist
    if not os.path.exists(rc_file):
        # complain
        print("WARNING: Global config file photorc does not exist!")
        # and bail
        return

    # all done
    return rc_file


def generate_global_config():
    """
    Create the global configuration file
    """
    # externals
    import os
    import yaml

    # look up the standard directory with user configurations; we prefer the XDG compliant way
    cfgdir = os.getenv("XDG_CONFIG_HOME")
    # and fall back to
    if cfgdir is None:
        # something u*ix friendly; windows support?
        cfgdir = os.path.expanduser(os.path.join("~", ".config"))
    # build the path to the photo configuration directory
    cfgdir = os.path.join(cfgdir, "photo")
    # enforce its existence
    os.makedirs(cfgdir, exist_ok=True)
    # and form the path to the configuration file
    rcfile = os.path.join(cfgdir, "photorc")

    # initialize the pile of configuration settings
    new = set(cfgmap)
    # if the configuration file exists
    if os.path.exists(rcfile):
        # open it
        with open(rcfile, mode="r") as stream:
            # parse it; make sure we get an actual dictionary even if the file is empty
            usercfg = yaml.load(stream, yaml.Loader) or {}
            # and remove any existing settings from my to-do pile
            new -= set(usercfg)

    # update the file
    with open(rcfile, mode="a") as stream:
        # go through the new settings
        for key in new:
            # write the documentation
            print("", file=stream)
            print("\n".join(cfgmap[key].pop("doc", "\n")), file=stream)
            # make the assignment
            print(f"{key}:", file=stream)
            for subkey in cfgmap[key]:
                print(f"    {subkey}: {cfgmap[key][subkey]}", file=stream)

    # all done
    return


def get_global_config():
    """
    Get the global configuration settings

    Will check in the following locations:

    1. $XDG_CONFIG_HOME/photo/photorc

    2. $HOME/.config/photo/photorc

    Returns
    -------
    dict | None
        A dictionary of values from the rc file

    """
    # support
    import yaml

    # attempt to locate the global configuration file
    rc_file = locate_global_config()
    # if it could not be found
    if not rc_file:
        # bail
        return

    # otherwise, try to open it
    with open(rc_file, "r") as fid:
        # and parse the contents
        result_dict = yaml.load(fid, Loader=yaml.Loader)

    return result_dict
