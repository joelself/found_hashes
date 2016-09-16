import argparse
import os

def process_dir(directory, out_file):
		for entry in os.scandir(directory):
			if not entry.is_dir():
				with open(os.path.join(entry.path)) as f:
					print("Processing file: {}".format(entry.path))
					count = 0
					for line in f:
						line = line.strip("\r\n")
						line = line.strip("\n")
						out_file.write("{}:{}\n".format(entry.name, line))
						count += 1
					print("\tWrote {} lines".format(count))

parser = argparse.ArgumentParser()
parser.add_argument("path")
args = parser.parse_args()
with open(os.path.join(args.path, ".all_found"), "w") as all_found:
	process_dir(os.path.join(args.path, "MD5"), all_found)
	process_dir(os.path.join(args.path, "SHA1"), all_found)

