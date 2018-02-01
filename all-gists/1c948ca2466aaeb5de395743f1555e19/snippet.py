import argparse
import json
import uuid


def gen_json(hypervisors, guests):
    virtwho = {}
    for i in range(hypervisors):
        guest_list = []
        for c in range(guests):
            guest_list.append({
                "guestId": str(uuid.uuid4()),
                "state": 1,
                "attributes": {
                    "active": 1,
                    "virtWhoType": "esx"
                }
            })
        virtwho[str(uuid.uuid4()).replace("-", ".")] = guest_list
    return virtwho

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "hypervisors", type=int,
        help="The number of hypervisors to create.")
    parser.add_argument(
        "guests", type=int,
        help="The number of guests per hypervisor to create.")
    parser.add_argument(
        "path", type=str,
        help="The file path to save the output to.")
    args = parser.parse_args()

    data = gen_json(args.hypervisors, args.guests)

    with open(args.path, 'w') as f:
        json.dump(data, f)
