__all__ = ["trace"]


def monkey_patch_getitem(obj, label, trace_list):
    if hasattr(obj, "__getitem__") and not isinstance(obj, str):
        prev_get_item = obj.__getitem__

        def new_get_item(k):
            new_label = f"{label}.{k}"
            trace_list.append(new_label)
            ret_val = prev_get_item(k)
            return monkey_patch_getitem(ret_val, new_label, trace_list)

        prev_set_item = obj.__setitem__

        def new_set_item(k, v):
            return prev_set_item(k, v)

        try:
            setattr(obj, "__getitem__", new_get_item)
        except AttributeError:
            class WrapObj(object):
                def __getitem__(self, item):
                    return new_get_item(item)

                if hasattr(obj, "__setitem__"):
                    def __setitem__(self, key, value):
                        return new_set_item(key, value)

                def __init__(self):
                    for key in filter(lambda x: x not in ["__getitem__", "__setitem__"], dir(obj)):
                        try:
                            setattr(self, key, getattr(obj, key))
                        except TypeError:
                            pass

            obj = WrapObj()
        return obj
    else:
        return obj


def trace(obj):
    trace_list = []
    obj = monkey_patch_getitem(obj, "", trace_list)
    return obj, trace_list


if __name__ == '__main__':
    def test_main():
        obj = [{"a": {"b": "c"}}]
        obj, trace_list = trace(obj)
        obj[0]["a"]["b"] = "d"
        print(trace_list)


    test_main()
