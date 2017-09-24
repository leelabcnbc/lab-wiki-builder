import json
import os
import os.path
import re
from collections import defaultdict, OrderedDict
from sys import version_info
import markdown
from urllib.parse import quote_plus
from string import ascii_lowercase, digits, ascii_uppercase
import pybtex.database

assert version_info >= (3, 6), "Python 3.6 or later to run this program!"

# use '?' for non-greedy.
# $ for end of line (but not including the \n), and ^ for start of line (but not including the preceding \n).
_bib_match_pattern = "^~~~$\n^@.+?^~~~"
_re_matcher = re.compile(_bib_match_pattern, re.MULTILINE | re.DOTALL)


def intermediate_keys(key):
    return tuple((key[:l] for l in range(len(key))))


def _useful_dir(dir_this):
    _, last_component = os.path.split(dir_this)
    return not (last_component.startswith('.') or last_component.startswith('_'))


def _additional_cats_closure(cats_original):
    cats_original_set = set(cats_original)
    cats_additional_set = set()
    for cat in cats_original_set:
        cats_additional_set.update(set(intermediate_keys(cat)))
    cats_original_set.update(cats_additional_set)
    return cats_original_set


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


def _good_nb_filename(f):
    # lower case or digits or _
    assert isinstance(f, str)

    base, ext = os.path.splitext(f)

    if base == '':
        return False
    for c in base:
        if c not in ascii_lowercase + ascii_uppercase + digits + '_-':
            return False
    if ext != '.ipynb':
        return False
    return True


def _process_one_key(key, files, all_info_dict, dirpath):
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
    bib_info_this_key = []
    for f in files:
        # check that it doesn't have any weird characters.
        if _good_nb_filename(f):
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


def _good_key_part(key_part):
    # lower case or digits or _
    assert isinstance(key_part, str)
    if key_part == '':
        return False
    for c in key_part:
        if c not in ascii_lowercase + digits + '_':
            return False
    if key_part.startswith('_'):
        return False
    return True


def collect_bib_info(start_dir):
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
            _process_one_key(key, files, all_info_dict, dirpath)

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


def _get_full_path(root_dir, key):
    return os.path.join(root_dir, *key)


def _get_top_source_in_md(key, source_url_root):
    if not source_url_root.endswith('/'):
        source_url_root += '/'
    # this should be a pair, of key, notebook name.
    return '[' + _get_title(key) + ']' + '(' + source_url_root + '/'.join(key) + ')'


def _get_source_in_md(source, source_url_root):
    if not source_url_root.endswith('/'):
        source_url_root += '/'
    # this should be a pair, of key, notebook name.
    key, nbname = source
    return '[' + f'{nbname}' + ']' + '(' + source_url_root + '/'.join(key + (nbname,)) + ')'


def _get_title(key):
    return '/'.join(key) if key != () else '(ROOT)'


def _output_info_one_key(root_dir, key, info_this_key,
                         website_root, source_url_root, name):
    full_path_this_key = _get_full_path(root_dir, key)
    bib_full_path = os.path.join(full_path_this_key, 'bib.bib')
    assert not os.path.exists(bib_full_path), f'{bib_full_path} exists'
    html_full_path = os.path.join(full_path_this_key, 'index.html')
    assert not os.path.exists(html_full_path), f'{html_full_path} exists'

    # first, output bib
    with open(bib_full_path, mode='w', encoding='utf-8') as f_bib:
        f_bib.write(info_this_key['bib'])

    # then write md (intermediate)

    source_top_level = sorted(set(s[0] for s in info_this_key['source'].keys()))
    html_title = _get_title(key)
    md_template_per_source = """    * {source}: {ids}"""
    md_all = []
    md_all.append(
        f"# {name}: {html_title}"
    )
    md_all.append(
        "If notebook doesn't look right, try adding `?flush_cache=true`, as discussed [here](http://nbviewer.jupyter.org/faq#i-want-to-removeupdate-a-notebook-from-notebook-viewer)\n")
    for s_top_level in source_top_level:
        md_all.append("""* {top_source}""".format(top_source=_get_top_source_in_md(s_top_level, website_root)))
        for source, ids in info_this_key['source'].items():
            if not source[0] == s_top_level:
                continue
            source_this = md_template_per_source.format(source=_get_source_in_md(source, source_url_root),
                                                        ids=', '.join(ids))
            md_all.append(source_this)

    # then add the javascript part for bibbase
    bib_relative_path = '/'.join(key + ('bib.bib',))

    bib_path = quote_plus(f'{website_root}/{bib_relative_path}')

    md_all.append('\n')  # this will get us out of the list.
    md_all.append(
        f"""<script src="https://bibbase.org/show?bib={bib_path}&jsonp=1"></script>""")

    md_all = '\n'.join(md_all)

    html_body = markdown.markdown(md_all, extensions=['markdown.extensions.extra'])

    # the header part is following <http://getbootstrap.com/css/>
    html_all = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset=utf-8>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_title}</title>
</head>
<body>
<div class="container-fluid">
{html_body}
</div>
</body>
</html>
"""
    with open(html_full_path, 'w', encoding='utf-8') as f_html:
        f_html.write(html_all)


def get_summary_from_info_dict(info_dict_this):
    summary_dict = OrderedDict()
    # getting the root is fine.
    if () in info_dict_this:
        info_this = info_dict_this[()]
        for source, ids in info_this['source'].items():
            key, nbname = source
            # since I don't merge '/'.join and nbname together during join, top level notebooks
            # always start with /.
            summary_key = '/'.join(key) + f'/{nbname}'
            summary_dict[summary_key] = sorted(ids)
    return summary_dict


def build_ref_lib(lib_root, website_root,
                  source_url_root, name):
    info_dict = collect_bib_info(lib_root)
    for key, info_this_key in info_dict.items():
        _output_info_one_key(lib_root, key, info_this_key, website_root,
                             source_url_root, name)
    summary_dict = get_summary_from_info_dict(info_dict)
    return summary_dict
