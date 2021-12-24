"""HyperText Formatter"""

def format(string: str, **kwargs) -> str:
    """A string formatter
    
    example:
        
        > n = '$[val]'
        > val = "Hello, World!"
        > print(format(n, val=val))
        Hello, World!
    
    """
    for key,val in kwargs.copy().items():
        string.replace(f"$[{key}]", val)
    return string
