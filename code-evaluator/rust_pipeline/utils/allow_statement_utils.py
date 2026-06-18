import re

def remove_rust_allow_attributes(code: str) -> str:
    pattern = r'#!?\[\s*allow\s*\(.*?\)\s*\]\n?'
    
    # Use re.DOTALL if you expect 'allow' attributes to span multiple lines
    return re.sub(pattern, '', code, flags=re.MULTILINE | re.DOTALL)