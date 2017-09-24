import os.path
from string import ascii_lowercase, digits, ascii_uppercase
from collections import OrderedDict


def intermediate_keys(key):
    return tuple((key[:l] for l in range(len(key))))


def _additional_cats_closure(cats_original):
    cats_original_set = set(cats_original)
    cats_additional_set = set()
    for cat in cats_original_set:
        cats_additional_set.update(set(intermediate_keys(cat)))
    cats_original_set.update(cats_additional_set)
    return cats_original_set


def _useful_dir(dir_this):
    _, last_component = os.path.split(dir_this)
    return not (last_component.startswith('.') or last_component.startswith('_'))


def _get_full_path(root_dir, key):
    return os.path.join(root_dir, *key)


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


def _good_entry_file_filename(f, ext_ref):
    # lower case or digits or _
    assert isinstance(f, str)

    base, ext = os.path.splitext(f)

    if base == '':
        return False
    for c in base:
        if c not in ascii_lowercase + ascii_uppercase + digits + '_-':
            return False
    if ext != ext_ref:
        return False
    return True


def _iterate_tree_part(tree, key_full):
    folder_tree_this = tree
    for key_part in key_full:
        folder_tree_this = folder_tree_this[key_part]
    return folder_tree_this


def build_folder_tree(set_of_keys):
    # first, build root level.
    if set_of_keys == set():
        return None
    else:
        tree_this = OrderedDict()
        assert () in set_of_keys
        # then let's find all keys.
        max_depth_in_keys = max(len(key) for key in set_of_keys)
        for depth in range(max_depth_in_keys):
            # fetch all keys of this length.
            key_all = sorted(key for key in set_of_keys if len(key) == depth + 1)
            # then plug them in, according to their second to last prefix.
            key_all_prefix = sorted(key[:-1] for key in key_all)

            # then iterate over trees.
            for prefix in key_all_prefix:
                tree_this_sub = _iterate_tree_part(tree_this, prefix)
                # insert everything that starts with this key_all.
                for key_to_insert in key_all:
                    if key_to_insert[:-1] == prefix:
                        tree_this_sub[key_to_insert[-1]] = OrderedDict()
        return tree_this
