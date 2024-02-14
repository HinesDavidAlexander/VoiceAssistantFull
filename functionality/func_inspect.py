import inspect

def call_with_signature(func, args):
    """Calls a function with the provided arguments, checking that the arguments are correct.

    Args:
        func (callable): function to be called
        args (any): arguments to be passed to the function

    Raises:
        ValueError: incorrect number/type of arguments provided

    Returns:
        any: func called with the provided args
    """
    
    to_bind = False
    
    signature = inspect.signature(func)
    params = signature.parameters
    for param in params.values():
        if param.annotation == str or param.name == "query":
            to_bind = True
            break
    
    if not to_bind:
        return func()
    bound_args = None
    try:
        bound_args = signature.bind(*args)
    except TypeError as e:
        raise ValueError(f"Incorrect number/type of arguments provided: {e}")
    except Exception as e:
        raise ValueError(f"Incorrect inputs for function call.: {e}")
    
    if not bound_args:
        raise ValueError("Incorrect number of arguments provided")
    bound_args.apply_defaults()
    
    return func(*bound_args.args, **bound_args.kwargs)

def has_args(callable):
    """
    Checks if a callable takes any arguments.

    Args:
        callable: The callable to check.

    Returns:
        True if the callable takes any arguments, False otherwise.
    """

    # Use inspect.signature to get the function signature
    signature = inspect.signature(callable)

    # Check if the signature has any parameters
    return bool(signature.parameters)