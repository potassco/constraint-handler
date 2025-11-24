class FailIntegrityExn(Exception):
    pass

def constrain(expression):
    if not expression:
        raise FailIntegrityExn