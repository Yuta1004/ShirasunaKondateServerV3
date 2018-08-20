def is_float(str_value):
    try:
        float(str_value)
        return True
    except ValueError:
        pass

    return False
