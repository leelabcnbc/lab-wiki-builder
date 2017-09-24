"""this file handles the reference library specific part"""

from sys import version_info
import re
import os
import json
import pybtex.database

assert version_info >= (3, 6), "Python 3.6 or later to run this program!"
from .utils import _additional_cats_closure

# use '?' for non-greedy.
# $ for end of line (but not including the \n), and ^ for start of line (but not including the preceding \n).
_bib_match_pattern = "^~~~$\n^@.+?^~~~"
_re_matcher = re.compile(_bib_match_pattern, re.MULTILINE | re.DOTALL)


def _process_one_file(key, f, info_this_key):
    f_pure = os.path.split(f)[1]
    with open(f, 'r', encoding='utf8') as data_file:
        data = json.load(data_file)
        # print(data)
        cells_this_file = data['cells']
        # print('for {}, {} cells'.format(nb_to_process, len(cells_this_file)))
        for c in cells_this_file:
            cell_content_this = ''.join(c['source'])
            # print(cell_content_this)
            # then use regular expression.
            all_bibs_this = _re_matcher.findall(cell_content_this)
            for x in all_bibs_this:
                bib_raw = x[4:-3]
                bib_database = pybtex.database.parse_string(bib_raw, 'bibtex')

                # for entry in bib_database.entries.values():
                #     print(entry.key)
                # TODO: explicitly display what got duplicated.
                assert len(bib_database.entries) == 1, 'you must have single bib entry each time!'
                entry_this = bib_database.entries[bib_database.entries.keys()[0]]
                # then let's get ID.
                bib_id = entry_this.key
                bib_cats = entry_this.fields.get('additional-categories', '').strip()
                if bib_cats == '':
                    bib_cats = []
                else:
                    bib_cats = [tuple(cat.strip().split('/')) for cat in bib_cats.split(',')]
                bib_cats.append(key)
                bib_cats = _additional_cats_closure(bib_cats)
                info_this_key.append([bib_id, (bib_raw, key, f_pure, bib_cats)])



_dispatch_handle = {
    'process_fn': _process_one_file,
    'ext': '.ipynb'
}