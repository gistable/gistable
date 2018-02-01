def delete_first(self):
    deleted = self.head
    if self.head:
        self.head = self.head.next
        deleted.next = None
    return deleted