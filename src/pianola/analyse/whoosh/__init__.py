import os
import re

from pianola.lib.schema.whoosh import WhooshSchema

import whoosh.index as index


def analyse(indices_dir: str) -> WhooshSchema:
    res = WhooshSchema("whoosh", [])
    for f in os.listdir(indices_dir):
        if m := re.match(r"_(.*)_(\d+)\.toc", f):
            indexname = m[1]
            res.indices += [index.open_dir(indices_dir, indexname=indexname)]

    return res
