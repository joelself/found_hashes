import os
import argparse
import re
from enum import Enum
import json
import datetime
import time


class FoundStatus(Enum):
  not_found = 0
  found = 1
  error = 2
# response = urlopen("https://hashes.org/api.php?act=REQUEST&key=yfU5CmUVjxcLUYdTuODZVIxSoMUBo6&hash=739c5b1cd5681e668f689aa66bcc254c")
minute_start = datetime.datetime.now()
request_count = 0
parser = argparse.ArgumentParser()
parser.add_argument("path", nargs='?', default=os.getcwd())
args = parser.parse_args()
api_key = ""
with open(os.path.join(args.path, ".api_key")) as f:
  api_key = f.readline()
  api_key = api_key.strip("\r\n")
  api_key = api_key.strip("\n")
for entry in os.scandir():
  if entry.is_dir(args.path) and entry.name != "tools_dir":
    process_dir(entry)

def process_dir(dir_entry):
  processed_files = {".processed_files": True, ".found_hashes": True}
  not_found = {}
  found = {}
  with open(os.path.join(dir_entry.path, ".found_hashes")) as found_file:
    for line in found_file:
      line = line.strip("\r\n")
      line = line.strip("\n")
      found[line] = True
  with open(os.path.join(dir_entry.path, ".processed_files")) as processed_file:
    for line in processed_file:
      if line != "":
        processed_files[line] = True
  for entry in os.scandir(dir_entry.path):
    if entry.is_dir():
      process_dir(entry)
    else if not entry.name in processed_files:
      if process_file(entry, not_found):
        processed_files[entry.name] = True
      else:
        print("Failed to process file: \"{}\"".format(entry.path))

  with open(os.path.join(dir_entry.path, ".found_hashes"), "w") as found_file:
    for key in found.keys():
      found_file.write("{}\n".format(key))

  with open(os.path.join(dir_entry.path, ".not_found_hashes"), "w") as not_found_file:
    for key in not_found.keys():
      not_found_file.write("{}\n".format(key))
  with open(os.path.join(dir_entry.path, ".processed_files"), "w") as processed_file:
    for key in processed_files.keys():
      processedfile.write("{}\n".format(key))


def process_file(entry, not_found, found):
  with open(entry.path) as f:
    for line in f:
      if line != "\r\n" and line != "\n":
        parts = re.split(":", line)
        found_status = lookup_hash(parts[0])
        if found_status == FoundStatus.error:
          found_status = lookup_hash(parts[0]) # retry once
          if found_status == FoundStatus.error:
            print("Failed to look up {} in file {}".format(parts[0], entry.path))
        if found_status == FoundStatus.not_found or found_status == FoundStatus.error:
          not_found[parts[0]] = True
        else
          found[parts[0]] = True
  return True

def lookup_hash(hash_val, file_path):
  global api_key
  global minute_start
  global request_count
  now = datetime.datetime.now()
  time_diff = now - minute_start;
  if request_count >= 20 and time_diff.total_seconds() < 60.0:
    time.sleep(60.0 - time_diff.total_seconds())
  if request_count < 20 or time_diff.total_seconds() >= 60.0:
    if time_diff.total_seconds() > 60.0:
      request_count = 1
      minute_start = datetime.datetime.now()
    response = json.loads(urlopen("https://hashes.org/api.php?act=REQUEST&key={}&hash={}".format(api_key, hash_val)).read().decode("utf-8"))
    if "REQUEST" in response:
      if response["REQUEST"] == "FOUND":
        return FoundStatus.found
      else if response["REQUEST"] == "NOT FOUND":
        return FoundStatus.not_found
      else
        print("Received unexpected response: \"{}\"".format(response))
        return FoundStatus.error
      else if "ERROR" in response:
        if response["ERROR"] != "LIMIT REACHED!":
          print("Received unexpected response: \"{}\"".format(response))
        return FoundStatus.error
      else:
        print("Received unexpected response: \"{}\"".format(response))
        return FoundStatus.error



