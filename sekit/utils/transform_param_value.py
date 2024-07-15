import json


def transform_param_value(
    obj, sep="_", none_str="null", kv="-", dict_reverse=False
):
    """実験の値を文字列に変換する関数. 主にファイル名の生成のために使う

    Parameters
    ---------
    obj: object
        transformed value
    Return
    ------
    String
    """
    if obj is None:
        return none_str
    elif isinstance(obj, list):
        return sep.join(str(o) for o in obj)
    elif isinstance(obj, tuple):
        return sep.join(str(o) for o in obj)
    elif isinstance(obj, dict):
        linked_dict = list([str(a), str(b)] for a, b in obj.items())
        # 順番が変わると困るので、同じ値になるためにキーでソートしておく
        sorted_linked_dict = sorted(
            linked_dict, key=lambda d: str(d[0]), reverse=dict_reverse
        )
        return sep.join(k + kv + v for k, v in sorted_linked_dict)
    else:
        return str(obj)
