# coding=utf-8

def add_keys_to_dict(dictionary,keys):
  if len(keys) == 0:
    return
  if not dictionary.has_key(keys[0]):
    dictionary[keys[0]] = {}
  add_keys_to_dict(dictionary[keys[0]],keys[1:])

