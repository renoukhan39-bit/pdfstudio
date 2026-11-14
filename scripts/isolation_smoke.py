"""Run inside the dedicated worker container via docker compose exec."""
import errno
import os
from pathlib import Path
import socket

assert os.getuid() != 0, 'Worker must not run as root'
try:
    Path('/opt/pdfstudio/write-probe').write_text('probe')
except OSError as exc:
    assert exc.errno in (errno.EROFS, errno.EACCES), exc
else:
    raise AssertionError('Worker filesystem is writable')
for address in ('1.1.1.1', '8.8.8.8'):
    try:
        connection = socket.create_connection((address, 443), timeout=2)
    except OSError:
        continue
    connection.close()
    raise AssertionError('Worker can reach the public internet')
print('Non-root identity, read-only code filesystem and blocked public egress verified.')
