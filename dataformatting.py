

# data formating
def as_list(node):
    """
    Define A Node As a List
    """

    if not type(node) is list:

        node = [node]

    return node


def un_list(the_node):
    """
    Unlist A Node
    """

    if type(the_node) is list:

        return the_node[0]

    return the_node