"""main builder function"""
import os.path
import json
from .leelab_wiki_builder import build_ref_lib


def builder(cmd_params, rc_params):
    # check cmd params
    # it should be fine. all the way.


    # check rc_params
    #
    input_root, output_root, options = _normalize_cmd_params(cmd_params)
    subdirs, website_root, source_url_root = _normalize_input_rc_params(rc_params)

    # ok, let's work through subdirs one by one.
    summary_dict_all = dict()
    for name, subdir in subdirs.items():
        print(name, subdir)
        if subdir == '.':
            website_root_this = website_root
            source_url_root_this = source_url_root
            input_root_this = input_root
            output_root_this = output_root
        else:
            website_root_this = website_root + f'/{subdir}'
            source_url_root_this = source_url_root + f'/{subdir}'
            input_root_this = input_root + f'/{subdir}'
            output_root_this = output_root + f'/{subdir}'
        summary_this = build_ref_lib_wrapper(input_root_this, output_root_this, website_root_this, source_url_root_this,
                                             name, options=options)
        summary_dict_all[name] = summary_this

    with open(os.path.join(input_root, 'summary.json'), 'w', encoding='utf-8') as f_out:
        json.dump(summary_dict_all, f_out, indent=2)


def _normalize_input_rc_params(rc_params):
    assert {'subdirs', 'source_url_root', 'website_root'} >= rc_params.keys() >= {'source_url_root', 'website_root'}
    if 'subdirs' not in rc_params:
        # working on current folder.
        rc_params['subdirs'] = {'(ROOT)': '.'}
    # TODO: check that subdirs don't have space.
    return rc_params['subdirs'], rc_params['website_root'], rc_params['source_url_root']


def _normalize_cmd_params(cmd_params):
    input_root, output_root = cmd_params.input, cmd_params.output
    if output_root is None:
        output_root = input_root
    options = {'reference_library': cmd_params.ref,
               'project_library': cmd_params.proj}
    return input_root, output_root, options


def build_ref_lib_wrapper(input_root, output_root, website_root, source_url_root,
                          name, options=None):
    # for now, let's only work on trivial case.
    assert output_root == input_root
    return build_ref_lib(input_root, website_root, source_url_root, name, options=options)
