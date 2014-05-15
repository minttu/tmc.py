def prompt_yn(msg, default):
    sure = input("{0} [{1}]: ".format(msg, "Y/n" if default else "y/N"))
    if len(sure) == 0:
        return default
    if sure.upper() == "Y":
        return True
    return False