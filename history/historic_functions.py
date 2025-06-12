# SPDX-FileCopyrightText: Copyright (c) 2025 Software GmbH, Darmstadt, Germany and/or its subsidiaries and/or its affiliates
# SPDX-FileContributor: Dr. Gerald Ristow
# SPDX-FileContributor: René Walter
#
# SPDX-License-Identifier: Apache-2.0

def show_dynamic_nodes(leaves):
    print("INFO: all dynamic leaves with path:")
    for leaf in leaves:
        print(create_leaf_path(leaf))


def create_leaf_path(leaf):
    # path = str(leaf.nodeid)[15:-1]
    path = str(leaf.get_browse_name())
    path = path[16:-1]
    while True:
        if leaf.get_parent() is None:
            break
        leaf_name = str(leaf.get_parent().get_browse_name())
        leaf_name = leaf_name[16:-1]
        path = leaf_name + "/" + path
        leaf = leaf.get_parent()
    return path