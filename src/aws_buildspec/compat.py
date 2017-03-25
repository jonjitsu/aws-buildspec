import sys


# if sys.version_info[:1] == (2,):
#     def _to_str(unicode_or_str):
#         if isinstance(unicode_or_str, unicode):
#             return unicode_or_str.encode('utf-8')
#         else:
#             return unicode_or_str
# elif sys.version_info[:1] == (3,):
#     def _to_str(bytes_or_str):
#         if isinstance(bytes_or_str, bytes):
#             return bytes_or_str.decode('utf-8')
#         else:
#             return bytes_or_str
# to_str = _to_str

def to_str(something):
    if sys.version_info[:1] == (2,):
        if isinstance(something, unicode):
            return something.encode('utf-8')
        else:
            return something
    elif sys.version_info[:1] == (3,):
        if isinstance(something, bytes):
            return something.decode('utf-8')
        else:
            return something
