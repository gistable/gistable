# Converts a JSONL file generated with telegram-history-dump (1) to CSV
# Usage: python telegram-csv.py <path to json file> <path to output csv file>
# Example: python telegram-csv.py Bob.json Bob.csv
# 1: https://github.com/tvdstaaij/telegram-history-dump
from datetime import datetime
import unicodecsv as csv
import json, sys

def get_isodate(msg):
    date = msg.get("date", None)

    if not date:
        return "unknown"

    return datetime.fromtimestamp(date).isoformat()

def main():
    if len(sys.argv) != 3:
        sys.exit("No json and/or csv file given")

    jsonpath = sys.argv[1]
    csvpath = sys.argv[2]

    jsonfile = open(jsonpath, "r")
    csvfile = open(csvpath, "w")
    csvwriter = csv.writer(csvfile)

    csvwriter.writerow(["from", "to", "date", "text"])

    for item in jsonfile:
        msg = json.loads(item)

        csvwriter.writerow([
            msg["from"].get("print_name", "unknown"),
            msg["to"].get("print_name", "unknown"),
            get_isodate(msg),
            msg.get("text", "no text")
        ])

    jsonfile.close()
    csvfile.close()

if __name__ == "__main__":
    main()