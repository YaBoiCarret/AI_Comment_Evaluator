# increment i
def add_one(i):
    # add 1
    return i + 1

def risky_divide(a, b):
    """Divide a by b. Explain why zero is handled here to avoid runtime errors."""
    if b == 0:
        # check zero
        return 0
    return a / b
