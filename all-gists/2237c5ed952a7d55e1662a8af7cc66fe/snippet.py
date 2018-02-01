#!/usr/bin/env python

"""Download conversations, customers, and attachments from a Help Scout mailbox

Written by Jonathan Kamens (jik@kamens.us).

Released into the public domain.

Email me patches if you have enhancements you'd like me to incorporate. Don't
bother emailing me bug reports or suggestions; this script does exactly what I
need it to do, and I'm not planning on spending any time doing additional
coding on it myself.

"""

import argparse
import base64
import errno
import json
import os
import requests
import sys
import time


def main():
    args = parse_args()

    args.auth = requests.auth.HTTPBasicAuth(args.api_key, 'notused')

    if args.target_directory:
        try:
            os.chdir(args.target_directory)
        except OSError as ex:
            if ex.errno == errno.ENOENT:
                sys.exit("ERROR: The directory {} does not exist".format(
                    args.target_directory))
            elif ex.errno == errno.ENOTDIR:
                sys.exit("ERROR: {} is not a directory".format(
                    args.target_directory))
            raise

    if args.list_mailboxes:
        list_mailboxes(args)
    else:
        if args.mailbox_name:
            for name, _id in get_mailboxes(args):
                if args.mailbox_name == name:
                    args.mailbox_id = str(_id)
                    break
            else:
                sys.exit('Could not find a mailbox named "{}"'.format(
                    args.mailbox_name))
        download_conversations(args)


def parse_args():
    parser = argparse.ArgumentParser(description="Download conversations, "
                                     "customers, and attachments from a "
                                     "Help Scout mailbox")
    parser.add_argument("--verbose", action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list-mailboxes", action="store_true", help="List "
                       "available mailboxes instead of downloading")
    group.add_argument("--mailbox-name", action="store",
                       help="The name of the mailbox whose content should be "
                       "downloaded")
    group.add_argument("--mailbox-id", action="store", help="The identifier "
                       "of the mailbox whose content should be downloaded")
    parser.add_argument("--api-key", action="store", required=True,
                        help="The API key to use to access Help Scout")
    parser.add_argument("--target-directory", action="store",
                        help="Directory in which to put downloaded data "
                        "(default: current directory)")

    return parser.parse_args()


def list_mailboxes(args):
    template = "{:<40s} {:>6s}"
    for name, _id in get_mailboxes(args):
        print(template.format(name, str(_id)))


def get_mailboxes(args):
    page = 1
    while True:
        mailboxes = api_q(args, "mailboxes.json?page={}", page)
        pages = mailboxes["pages"]
        for mailbox in mailboxes["items"]:
            yield (mailbox["name"], mailbox["id"])
        if page == pages:
            break
        page += 1


def download_conversations(args):
    if not os.path.isdir("conversations"):
        os.mkdir("conversations")
    page = 1
    so_far_count = 0
    start_time = time.time()
    while True:
        conversations = api_q(args, "mailboxes/{}/conversations.json?page={}",
                              args.mailbox_id, page)
        pages = conversations["pages"]

        if page == 1 and args.verbose:
            print("Starting page {} of {}".format(page, pages))

        for conversation in conversations["items"]:
            download_conversation(args, conversation["id"])

        if page == pages:
            break

        if args.verbose:
            so_far_count += len(conversations["items"])
            elapsed_time = time.time() - start_time
            estimated_total = so_far_count * pages / page
            estimated_total_time = \
                elapsed_time * estimated_total / so_far_count
            estimated_time_left = estimated_total_time - elapsed_time
            print("Finished page {} of {}, estimated {:.0f} seconds remaining".
                  format(page, pages, estimated_time_left))

        page += 1


def download_conversation(args, id):
    conversation_dir = "conversations/{}".format(id)
    conversation = api_q(args, "{}.json", conversation_dir)["item"]
    save_customer(args, conversation["customer"])
    threads = conversation.pop("threads")
    if not os.path.isdir(conversation_dir):
        os.mkdir(conversation_dir)
    json_dump(conversation, open("{}/conversation.json".format(
        conversation_dir), "w"))
    threads_dir = "{}/threads".format(conversation_dir)
    if not os.path.isdir(threads_dir):
        os.mkdir(threads_dir)
    for thread in threads:
        save_customer(args, conversation["customer"])
        thread_dir = "{}/{}".format(threads_dir, thread["id"])
        if not os.path.isdir(thread_dir):
            os.mkdir(thread_dir)
        attachments = thread.pop("attachments")
        json_dump(thread, open("{}/thread.json".format(thread_dir), "w"))
        if attachments:
            attachments_dir = "{}/attachments".format(thread_dir)
            if not os.path.isdir(attachments_dir):
                os.mkdir(attachments_dir)
            for attachment in attachments:
                attachment_dir = "{}/{}".format(
                    attachments_dir, attachment["id"])
                if not os.path.isdir(attachment_dir):
                    os.mkdir(attachment_dir)
                json_dump(attachment, open("{}/attachment.json".format(
                    attachment_dir), "w"))
                attachment_data = base64.b64decode(
                    api_q(args, "attachments/{}/data.json",
                          attachment["id"])["item"]["data"])
                file_name = "{}/{}".format(
                    attachment_dir, attachment["fileName"])
                if file_name == "attachment.json":
                    # Ugh.
                    file_name = "attachment_data.json"
                open(file_name, "w").write(attachment_data)


saved_customers = set()


def save_customer(args, customer):
    if not customer:
        return
    if customer["type"] != "customer":
        return
    if customer["id"] in saved_customers:
        return
    if not os.path.isdir("customers"):
        os.mkdir("customers")
    customer = api_q(args, "customers/{}.json", customer["id"])["item"]
    json_dump(customer, open("customers/{}.json".format(customer["id"]), "w"))
    saved_customers.add(customer["id"])


def api_q(args, req, *pargs, **kwargs):
    return requests.get("https://api.helpscout.net/v1/" +
                        req.format(*pargs, **kwargs),
                        auth=args.auth).json()


def json_dump(obj, f):
    json.dump(obj, f, sort_keys=True, indent=2)


if __name__ == "__main__":
    main()
