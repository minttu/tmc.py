#!/usr/bin/env python3

from jinja2 import Environment, PackageLoader, FileSystemLoader
from jinja2.exceptions import UndefinedError
from markdown import markdown
from datetime import datetime
import yaml
import argparse
import traceback


def markdown_filter(value, *args, **kwargs):
    return markdown(value, *args, **kwargs)


def render(notifier):
    data = None
    print("Rendering")
    with open("data.yaml") as fp:
        data = yaml.safe_load(fp.read())

    data["time"] = datetime.utcnow()

    with open("index.html", "w") as fp:
        env = Environment(loader=FileSystemLoader("."))
        env.filters["markdown"] = markdown_filter
        try:
            res = env.get_template("template.html").render(data)
            fp.write(res)
        except UndefinedError:
            traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description='Generate documentation.')
    parser.add_argument('--watch', action='store_true',
                        help="Use pyinotify to watch for changes")
    args = parser.parse_args()

    if args.watch:
        import pyinotify
        import functools

        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm)
        wm.add_watch('data.yaml', pyinotify.IN_CLOSE_WRITE)
        wm.add_watch('template.html', pyinotify.IN_CLOSE_WRITE)
        on_loop_func = functools.partial(render)
        notifier.loop(daemonize=False, callback=on_loop_func)
    else:
        render(None)

if __name__ == "__main__":
    main()
