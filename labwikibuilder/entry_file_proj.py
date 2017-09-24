"""this file handles the project library specific part"""

import os

import frontmatter
from pybtex.database import BibliographyData, Entry

from .utils import _additional_cats_closure


def _process_meta(f):
    with open(f, 'r', encoding='utf8') as data_file:
        data = frontmatter.load(data_file)

    default_result = {
        # by default, finished.
        'finished': True,
        # no keywords
        'keywords': None,
        # no additional category
        'additional-categories': None,
    }
    # then let's construct the meta info dict.
    info_this = dict()

    data_mapping_dict = {
        'people': 'author',
        'name': 'title'
    }

    for key in data.keys():
        info_this[data_mapping_dict.get(key, key)] = data[key]

    for default_key, default_value in default_result.items():
        if default_key not in info_this:
            info_this[default_key] = default_value
    assert info_this.keys() == {'title', 'author', 'year',
                                'keywords', 'additional-categories',
                                'finished'}
    assert isinstance(info_this['finished'], bool)
    # this will show up in BibBase widget.
    info_this['note'] = data.content.strip()
    return info_this


def _process_one_file(key, f, info_this_key):
    f_pure = os.path.split(f)[1]
    info_this = _process_meta(f)

    # then let's construct a bib entry.
    entry_type = 'misc' if info_this['finished'] else 'unpublished'
    del info_this['finished']
    entry_this = Entry(entry_type, [(x, str(y)) for x, y in info_this.items() if y is not None])

    bib_id, _ = os.path.splitext(f_pure)

    bib_data = BibliographyData({
        bib_id: entry_this
    })

    bib_cats = info_this['additional-categories']
    if bib_cats is None:
        bib_cats = []
    else:
        bib_cats = [tuple(cat.strip().split('/')) for cat in bib_cats.split(',')]
    bib_cats.append(key)
    bib_cats = _additional_cats_closure(bib_cats)
    # '_' + bib_id is the key we should use for GitHub browsing.
    info_this_key.append([bib_id, (bib_data.to_string('bibtex'), key, '_' + bib_id, bib_cats)])


_dispatch_handle = {
    'process_fn': _process_one_file,
    'ext': '.md'
}
