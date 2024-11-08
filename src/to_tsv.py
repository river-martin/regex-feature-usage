import json
import sys


def json_to_tsv(file_path):
    with open(file_path, "r") as file:
        for line in file.readlines():
            try:
                data = json.loads(line)
                print(
                    "\t".join(
                        str(value)
                        for value in data.values()
                        if "\n" not in str(value) and "\t" not in str(value)
                    )
                )
            except UnicodeEncodeError:
                print("Error: UnicodeEncodeError")
                continue


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python to_tsv.py <path_to_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    json_to_tsv(json_file_path)
