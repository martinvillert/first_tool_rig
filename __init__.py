import sys
def rehash():
    for key, value in zip(sys.modules.keys(), sys.modules):
        if any(["rigg_tools" in str(x) for x in (key, value)]):
            if not key == "rigg_tools":
                try:
                    del sys.modules[key]
                except AttributeError:
                    pass