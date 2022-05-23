#!/usr/bin/env python3

# -*- encoding: utf-8 -*-
#
# Copyright 2022 LIP
#
# Author: Mario David <mariojmdavid@gmail.com>
#

"""json parser of a UMD or CMD release, and download packages
"""

import sys
import utils


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], '<package_name_version> (without extension .json) <0|1>')
        print('0 - downloads from the original external source, item 2 in pipeline')
        print('1 - downloads from the EGI UMD/CMD repository, item 6 in pipeline')
        sys.exit(1)

    prod_name = sys.argv[1]
    umd_download = sys.argv[2]

    ev = utils.get_conf(prod_name)
    pkg_dict = utils.create_dict_pkg(ev['json_file'])
    download_dir = ev['tmp_dir']
    if umd_download == '1':
        download_dir = ev['download_dir']
        for (pkg, url) in pkg_dict.items():
            pkg_dict[pkg] = ev['repo_uri_download'] + '/' + pkg

    print(pkg_dict)
    utils.download_pkg(pkg_dict, download_dir)
    sys.exit(0)
