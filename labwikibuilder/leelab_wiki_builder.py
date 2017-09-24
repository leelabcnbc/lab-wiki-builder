from .entry_file_ref import _dispatch_handle as _dispatch_handle_ref
from .input import collect_bib_info
from .output import _output_info_one_key, get_summary_from_info_dict


def build_ref_lib(lib_root, website_root,
                  source_url_root, name, options=None):
    assert options is not None

    if options == {'reference_library': True, 'project_library': False}:
        # get the process file handle
        dispatch_handle = _dispatch_handle_ref
    elif options == {'reference_library': False, 'project_library': True}:
        dispatch_handle = _dispatch_handle_ref
    else:
        raise ValueError('invalid option {}'.format(options))

    info_dict = collect_bib_info(lib_root, dispatch_handle=dispatch_handle)
    for key, info_this_key in info_dict.items():
        _output_info_one_key(lib_root, key, info_this_key, website_root,
                             source_url_root, name)
    summary_dict = get_summary_from_info_dict(info_dict)
    return summary_dict
