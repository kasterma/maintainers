"""Decide who is responsible for which part of the directory tree"""

import yaml
import fnmatch
import argparse
import logging
import logging.config

with open('logging.yml') as f:
    D = yaml.load(f)
    logging.config.dictConfig(D)

log = logging.getLogger("maintainers")

parser = argparse.ArgumentParser(description="Apply MAINTAINERS file to find relevant data for file")
parser.add_argument("-f", "--file", "--filename", dest="filename", help="The MAINAINERS file.", default="MAINTAINERS")
parser.add_argument("--path", dest="path", help="The path to get information on", required=True)


def get_glob_list(dat):
    """Given a full maintainer description return a list of (glob, idx) pairs"""
    gi_list = []
    for k,v in dat.items():
        f = v['F']
        if isinstance(f, list):
            gi_list.extend([(g, k) for g in f])
        else:
            gi_list.append((f, k))
    return gi_list


def check_path(path, gi_list):
    """Check which area(s) (as specified by dat) path falls into"""
    ares = [(g,k) for (g,k) in gi_list if fnmatch.fnmatch(path, g)]
    log.debug("Path {0} has matches {1}".format(path, str(ares)))
    return ares


class NoMatch(Exception):
    """Exception to indicate there was no matching file glob for this file"""
    pass


def path_to_key(path, gi_list):
    """Given a path return the key this belongs to.

    Note: if doesn't belong to any key throws NoMatch.
    Note: if matches on multiple patterns, the longest (as in number of characters) wins.
    """
    matches = check_path(path, gi_list)
    if matches:
        return max(matches, key=lambda x: len(x[0]))[1]
    else:
        raise NoMatch("Couldn't file a match for path: {0}.".format(path))


def get_relevant_dat(path, dat):
    """Get the data about the file."""
    gi_list = get_glob_list(dat)
    key = path_to_key(path, gi_list)
    d = dat[key].copy()
    d['key'] = key
    d['path'] = path
    return d


if __name__ == "__main__":
    args = parser.parse_args()
    log.debug("Ags: {0}".format(args))
    with open(args.filename) as f:
        dat = yaml.load(f)
    log.info(dat)
    print(get_relevant_dat(args.path, dat))
