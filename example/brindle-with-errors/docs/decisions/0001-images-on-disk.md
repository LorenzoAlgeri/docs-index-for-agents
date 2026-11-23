# 0001: Store recipe images on disk

Status: accepted.

Images stay out of the database. Reason: a tenant file with images grows ten
times faster, and backups of the file become the slow part of the night.
Consequence: a restore needs both the database file and the image folder.
