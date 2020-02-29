from codecs import encode
from textwrap import wrap
from .defines import COMMIT_MSG_WIDTH

def wrap_paragraphs(text, width=COMMIT_MSG_WIDTH):
    return '\n\n'.join('\n'.join(wrap(paragraph, width)) for paragraph in text.split('\n\n'))

def rot13(text):
    return encode(text, 'rot_13')
