#!/usr/local/env python

import argparse
import email
import extract
import getpass
import imaplib
import os
import sys
import uuid

from py2neo import Graph, Node, Relationship

class GmailExtractor:

    def __init__(self, imap_server, neo4j_server):
        self.__graph = neo4j_server
        self.__imap = imap_server
        self.__persons_known = {}

    def __get_folder_mail(self, folder):
        status, msgs = self.__imap.select(folder)
        if status != "OK":
            sys.exit(status)
        result, data = self.__imap.uid('search', None, "ALL")
        for msg_id in data[0].split():
            result, data = self.__imap.uid('fetch', msg_id, "RFC822")
            msg = email.message_from_string(data[0][1])
            self.__add_message_to_db(msg)

    def __add_message_to_db(self, msg):
        msg_obj, attachments = extract.extract_msg(msg)
        msg_node = Node.cast(msg_obj)
        msg_node.labels.add("Email")
        for addr_type in ["to", "cc", "from"]:
            if addr_type in msg_obj:
                for address in msg_obj[addr_type].split(", "):
                    name, email_addr = email.utils.parseaddr(address)
                    if email_addr not in self.__persons_known:
                        self.__persons_known[email_addr] = Node("Person", name=name, email=email_addr)
                    to_relationship = Relationship(msg_node, addr_type.upper(), self.__persons_known[email_addr])
                    graph.create(to_relationship)

    def __list(self):
        folders = self.__imap.list()
        return [folder[folder.find("/")+4:-1] for folder in folders[1]]

    def get_folder_list(self, args):
        dirs = self.__list()
        for folder in dirs:
            print folder

    def get_all_mail(self, args):
        self.__get_folder_mail('[Gmail]/All Mail')
        self.__get_folder_mail('[Gmail]/Trash')

    def get_inbox(self, args):
        self.__get_folder_mail('INBOX')

def setup_help(gmc):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    inbox_folder = subparsers.add_parser('inbox')
    inbox_folder.set_defaults(func=gmc.get_inbox)

    all_folder = subparsers.add_parser('all')
    all_folder.set_defaults(func=gmc.get_all_mail)

    list_folder = subparsers.add_parser('list')
    list_folder.set_defaults(func=gmc.get_folder_list)

    return parser

if __name__ == "__main__":
    graph = Graph(os.environ['NEO4J_ADDRESS'] + '/db/data")
    user = os.environ["GMAIL_USER"] if "GMAIL_USER" in os.environ else raw_input("GMail User Name: ")
    password = os.environ["GMAIL_PASS"] if "GMAIL_PASS" in os.environ else getpass.getpass("GMail Password: ")

    gm = imaplib.IMAP4_SSL('imap.gmail.com')
    try:
        print gm.login(user.strip(), password.strip())
    except Exception as E:
        sys.exit(E)

    gmc = GmailExtractor(gm, graph)
    parser = setup_help(gmc)
    args = parser.parse_args()
    args.func(args)


