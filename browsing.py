# SPDX-FileCopyrightText: Copyright (c) 2025 Software GmbH, Darmstadt, Germany and/or its subsidiaries and/or its affiliates
# SPDX-FileContributor: Dr. Gerald Ristow
# SPDX-FileContributor: René Walter
#
# SPDX-License-Identifier: Apache-2.0

from opcua import Client, ua
import time
import threading
import copy
import json
from GUI import run_gui

use_gui = True
# sleep_timer defines the time that is waited between two measurements of a leaf. If the value of the leaves changes, it is a dynamic leaf
sleep_timer = 5
max_threads = 500
#window_len and collect_interval defining the plots, when using the gui, normally 180 secs
window_len = 60
collect_interval = 1
#url = "opc.tcp://SAG-GHY1ZY2:53530/OPCUA/SimulationServer"
url = "opc.tcp://SAG-1J1SSL3:53530/OPCUA/SimulationServer"

# cumulocity
template_name = "KI4ETA-Tree"
referencedServerId = "178830"
referencedServerName = "ETA-Klimaraum-SPS"
referencedRootNodeId = "i=85"

leaves = []
dynamic_leaves = []
client = Client(url)
client.connect()
root = client.get_root_node()


def browse_recursive(node):
    """Recursively searches the opcua-browser tree for leaves that have a numeric value (int,float).
    Appends that kinds of leaves in list.

    Args:
        node : Node where the search starts
    """
    for childId in node.get_children():
        ch = client.get_node(childId)
        if ch.get_node_class() == ua.NodeClass.Object:
            browse_recursive(ch)
        elif ch.get_node_class() == ua.NodeClass.Variable:
            try:
                if(ch.nodeid.NodeIdType == ua.NodeIdType.FourByte or ch.nodeid.NodeIdType == ua.NodeIdType.TwoByte)\
                        and (isinstance(ch.get_value(), float) or isinstance(ch.get_value(), int)):
                    leaves.append(ch)
            except Exception as e:
                pass


def dynamic_check(leaf, li, sleep):
    """Checking whether a node changes its value over time.

    Args:
        leaf : node to check dynamic values
        li : list only containing dynamic nodes
        sleep : waiting time for dynamic value
    """
    try:
        first_value = leaf.get_value()
        for i in range(sleep * 4):
            tmp_value = leaf.get_value()
            if first_value != tmp_value:
                li.append(leaf)
                break
            time.sleep(0.25)
    except Exception as e:
        return


# checks every extracted leaf for dynamic values
# if the value does not change, the node gets rejected
def remove_static_values(leaves, sleep):
    """Opens up a thread for For each node to filter the nodes with dynamic values

    Args:
        leaves : list of all leaves with numeric value
        sleep : paramater to reduce overload

    Returns:
        new_li : list only containing leaves with dynamic values.
    """
    print(f'INFO: removing static leaves from list with len: {len(leaves)}')
    if int(sleep * (len(leaves) / max_threads)) > 5:
        print(f'INFO: estimated waiting time: {str(int(sleep * (len(leaves) / max_threads)))} seconds')
    new_li = []
    threads = []
    for i in range(len(leaves)):
        t = threading.Thread(
            target=dynamic_check,
            args=[leaves[i], new_li, sleep])
        t.start()
        threads.append(t)
        if ((i + 1) % max_threads) == 0:
            time.sleep(sleep)
            #print("INFO: checked leaves: " + str(len(threads)))
    for thread in threads:
        thread.join()
    print(f'INFO: final amount of leaves with dynamic value: {str(len(new_li))}')
    return new_li


def collect_data(leaf, window_len, collect_interval, timeseries):
    """The node is subscribed to collect data over a period of time

    Args:
        leaf : dynamic node
        window_len : selected length of a timeseries
        collect_interval : Waiting time between two new data points
        timeseries : list of timeseries
    """
    window = []
    for i in range(window_len):
        value = leaf.get_value()
        window.append(value)
        time.sleep(collect_interval)
    timeseries.append((leaf, window))
    return


def create_timeseries(leaves, window_len, collect_interval):
    """Opens up a thread for For each node to build up a timeseries respectively.

    Args:
        leaves : list of dynamic-nodes
        window_len : selected length of a timeseries
        collect_interval : Waiting time between two new data points

    Returns:
        timeseries : list of timeseries
    """
    print("INFO: creating timeseries")
    print(f"INFO: estimated waiting time: {str((window_len * collect_interval))} seconds")
    timeseries = []
    threads = []
    for i in range(len(leaves)):
        t = threading.Thread(
            target=collect_data,
            args=[leaves[i], window_len, collect_interval, timeseries])
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()
    return timeseries


def label_leaves_classifier(timeseries):
    """The classifier is called here and classifies the created timeseries.
    Because of the softmax function, a probability is calculated for each class with which the time series belongs to the class. 
    The three highest probabilities are included in the list

    Args:
        timeseries : list of timeseries

    Returns:
        label_list : labeled list of classifier
    """
    print("INFO: predicting unit of timeseries")
    label_list = []
    i = 0
    for ts in timeseries:
        # TODO load classifier here to predict the label of each timeseries. Next cell is a placeholder
        label_list.append((ts[0], ts[1], ("Spannung" + str(i), 87+i, "V", "L1-N"), ("Temperatur" + str(i), 11+i, "C", "Grad"), ("Strom" + str(i), 2+i, "A", "I1-N")))
        i = i + 1
    #label = clf.predict(timeseries[0])
    return label_list


def label_leaves_static(dynamic_nodes):
    """If the classifier is not needed and the opcua-browser tree is well documented,
    this call can be used to label the data. 
    The function can be individually adapted according to your own wishes depending on the application

    Args:
        dynamic_nodes : list of nodes with dynamic-values

    Returns:
        label_list : list of statically described labels
    """
    label_list = []
    for node in dynamic_nodes:
        #node, fragment, unit, series
        label_list.append((node, "Spannung L1-N", "V", "L1-N"))
    return label_list


def get_labeled_leaves(leaves, window_len, collect_interval):
    """Call to process labeling-steps sequentially.

    Args:
        leaves : list of nodes with dynamic-values
        window_len : selected length of a timeseries
        collect_interval : Waiting time between two new data points

    Returns:
        predicted_leaf_list : list labeled by classifier
    """
    timeseries = create_timeseries(leaves, window_len, collect_interval)
    predicted_leaf_list = label_leaves_classifier(timeseries)
    return predicted_leaf_list


def get_c8y_path(leaf):
    """Path is required so that Cumulocity can find the specific node in the tree

    Args:
        leaf : dynamic-node

    Returns:
        path : path of dynamic node in the tree
    """
    path = [str(leaf.get_browse_name())[14:-1]]
    while True:
        leaf_name = str(leaf.get_parent().get_browse_name())
        path.append(leaf_name[14:-1])
        leaf = leaf.get_parent()
        if leaf.get_parent().get_parent() is None:
            break
    path.reverse()
    return path


def create_opcua_template(leaf_list,  referencedServerId, referencedServerName, referencedRootNodeId, template_name):
    """A template is generated containing the labeled dynamic nodes. The template can be integrated into Cumulocity

    Args:
        leaf_list : labeled leave-list
        referencedServerId : id of Server
        referencedServerName : name of opcua-browser-server
        referencedRootNodeId : entry point in the tree
        template_name : name of template in Cumulocity

    Returns:
        template : cumulocity-template
    """
    print("INFO: generate template for cumulocity")
    f = open('rest/template.json')
    origin = json.load(f)
    template = copy.deepcopy(origin)
    template['name'] = template_name
    template['referencedServerId'] = referencedServerId
    template['referencedServerName'] = referencedServerName
    template["referencedRootNodeId"] = referencedRootNodeId
    measurement_template = copy.deepcopy(template['mappings'][0])
    template['mappings'].clear()
    for leaf in leaf_list:
        node_name = str(leaf[0].get_browse_name())[16:-1]
        tmp_template = copy.deepcopy(measurement_template)
        tmp_template['browsePath'] = get_c8y_path(leaf[0])
        tmp_template['name'] = node_name
        tmp_template['measurementCreation']['unit'] = leaf[2]
        tmp_template['measurementCreation']['type'] = leaf[1]
        tmp_template['measurementCreation']['fragmentName'] = "c8y_" + node_name.lower()
        tmp_template['measurementCreation']['series'] = leaf[3]
        template['mappings'].append(tmp_template)
    f.close()
    return template


def save_template(template):
    """Saves generated template in file-system.

    Args:
        template : cumulocity-template
    """
    file = 'output/new_template.json'
    print(f'INFO: saving cumulocity template in: {file}')
    with open(file, 'w') as f:
        json.dump(template, f)


if __name__ == "__main__":
    print("INFO: browsing through opcua-browser tree for leafs")
    browse_recursive(root)
    dynamic_leaves = remove_static_values(leaves, sleep_timer)
    if use_gui:
        probability_leaf_list = get_labeled_leaves(dynamic_leaves, window_len, collect_interval)
        labeled_leaf_list = run_gui(probability_leaf_list)
    else:
        labeled_leaf_list = label_leaves_static(dynamic_leaves)
    c8y_template = create_opcua_template(labeled_leaf_list, referencedServerId, referencedServerName, referencedRootNodeId, template_name)
    save_template(c8y_template)
    # TODO build REST-Call to automatically import template in cumulocity
    client.disconnect()
    print('INFO: finished')


