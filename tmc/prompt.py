def yn_prompt(msg, default=True):
    ret = custom_prompt(msg, ["y", "n"], "y" if default else "n")
    if ret == "y":
        return True
    return False


def custom_prompt(msg, options, default):
    sure = input("{0} [{1}]: ".format(msg,
                                      "/".join([x.upper() if x == default else x.lower() for x in options])))
    if len(sure) == 0:
        return default
    for option in options:
        if sure.upper() == option.upper():
            return option
    return default
