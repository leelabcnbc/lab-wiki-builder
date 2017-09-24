import os
import os.path
from collections import defaultdict, OrderedDict
from .utils import _useful_dir, _good_key_part, _good_entry_file_filename


def _finalize_info_dict_entry(entry_this: list):
    # let's first collect all possible (key, file_pure) pairs
    bib_keys = {x[0] for x in entry_this}
    assert len(bib_keys) == len(entry_this), "non unique keys!"
    entry_this = OrderedDict(entry_this)

    # get the bib
    bib_all = '\n\n\n'.join((x[0] for x in entry_this.values()))
    source_all = sorted({x[1:] for x in entry_this.values()})
    source_dict = OrderedDict()
    for source in source_all:
        source_dict[source] = sorted((x for x, y in entry_this.items() if y[1:] == source))
    return {
        'bib': bib_all,
        'source': source_dict,
    }


def _process_one_key(key, files, all_info_dict, dirpath, dispatch_handle=None):
    # key_intermediates is the default set of additional-categories.
    # we should merge this to each entry's own additional-categories.

    # check if there's any ipynb to process

    # for each entry, we have a ordered dict.
    # bib id is the key of the entry.
    # {bib_ID}: ({bib_entry_itself},
    #            original_key,
    #            original ipynb,
    #            {set of additional categories})
    # I could in theory compute this only once; I just
    assert dispatch_handle is not None

    _process_one_file, ext_ref = dispatch_handle['process_fn'], dispatch_handle['ext']

    bib_info_this_key = []
    for f in files:
        # check that it doesn't have any weird characters.
        if _good_entry_file_filename(f, ext_ref):
            file_full = os.path.join(dirpath, f)
            print(f'process {file_full}')
            _process_one_file(key, file_full, bib_info_this_key)
    bib_keys = {x[0] for x in bib_info_this_key}
    assert len(bib_keys) == len(bib_info_this_key), "non unique keys!"
    bib_info_this_key = OrderedDict(bib_info_this_key)
    # for x, y in bib_info_this_key.items():
    #     print(x, y[1:3])

    # then, add our items to all_info_dict.
    # send a copy to each of bib_cats.
    for bib_id, bib_entry in bib_info_this_key.items():
        assert len(bib_entry) == 4
        bib_entry_to_insert = bib_entry[:3]
        bib_cats = bib_entry[3]
        for bib_cat in bib_cats:
            all_info_dict[bib_cat].append((bib_id, bib_entry_to_insert))


def collect_bib_info(start_dir, dispatch_handle=None):
    assert dispatch_handle is not None
    all_info_dict = defaultdict(list)
    permissible_keys = []
    for dirpath, dirs, files in os.walk(start_dir):
        # ignore some useless directories.
        if os.path.samefile(dirpath, start_dir):
            # empty tuple is the root.
            key = ()
        elif _useful_dir(dirpath):
            key = tuple(os.path.relpath(dirpath, start_dir).split('/'))
            assert len(key) >= 1
        else:
            key = ('_',)  # so it would fail

        valid_key = all(_good_key_part(k) for k in key)

        if valid_key:
            permissible_keys.append(key)
            _process_one_key(key, files, all_info_dict, dirpath, dispatch_handle=dispatch_handle)

    # ok. then make each info dict's entry
    all_info_dict_new = dict()

    for x, y in all_info_dict.items():
        # this should be a dict, with fields
        # 'bib' the raw bib
        # 'source' ordered dict, key being (key, f_pure), value being sorted list of bib ids, sorted by ids.
        # _finalize_info_dict_entry should also check that there's no duplicate.
        all_info_dict_new[x] = _finalize_info_dict_entry(y)
    # you can't create some key that's purely due to additional.
    # TODO: this is probably subject to debate. but let's use this first.
    assert set(permissible_keys) >= all_info_dict_new.keys(), 'you cannot have pure additional keys'
    return all_info_dict_new
