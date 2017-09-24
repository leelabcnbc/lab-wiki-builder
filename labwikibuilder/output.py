import os.path
from collections import OrderedDict
from .utils import _get_full_path
import markdown
from urllib.parse import quote_plus
from json import dumps


def _get_top_source_in_md(key, source_url_root, title_to_use=None):
    if not source_url_root.endswith('/'):
        source_url_root += '/'
    # this should be a pair, of key, notebook name.
    if title_to_use is None:
        title_to_use = _get_title(key)
    return '[' + title_to_use + ']' + '(' + source_url_root + '/'.join(key) + ')'


def _get_source_in_md(source, source_url_root):
    if not source_url_root.endswith('/'):
        source_url_root += '/'
    # this should be a pair, of key, notebook name.
    key, nbname = source
    return '[' + f'{nbname}' + ']' + '(' + source_url_root + '/'.join(key + (nbname,)) + ')'


def _get_title(key):
    return '/'.join(key) if key != () else '(ROOT)'


def _tree_pretty_print(folder_tree, website_root, key_front):
    # first print root.
    bag_of_lines = []
    # this ':-1' also works when key_front is (), and it will return ().
    bag_of_lines.append('Back to {}\n'.format(_get_top_source_in_md(key_front[:-1], website_root)))
    # then for each thing in folder tree, do a recursion.
    _tree_pretty_print_inner(
        folder_tree, website_root, key_front, indent=0, bag_of_lines=bag_of_lines
    )

    return '\n'.join(bag_of_lines) + '\n'


def _tree_pretty_print_inner(folder_tree, website_root, key_front, indent, bag_of_lines):
    for key, value in folder_tree.items():
        bag_of_lines.append(
            ' ' * indent + '* ' + _get_top_source_in_md(key_front + (key,), website_root, title_to_use=key)
        )
        if value != {}:
            # then recursion.
            _tree_pretty_print_inner(
                value, website_root, key_front + (key,), indent=indent + 4, bag_of_lines=bag_of_lines
            )


def _output_info_one_key(root_dir, key, info_this_key,
                         website_root, source_url_root, name, folder_tree=None):
    full_path_this_key = _get_full_path(root_dir, key)

    # then create this dir if needed
    os.makedirs(full_path_this_key, exist_ok=True)

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

    # here, I need to add a tree.
    md_all.append('## subtree starting from this level\n')
    md_all.append(
        _tree_pretty_print(folder_tree, website_root, key)
    )
    md_all.append('## entries under this level\n')
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
