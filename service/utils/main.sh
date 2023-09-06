#!/bin/bash

python -c 'import uuid;print(uuid.uuid4())' > /unlock_code.txt
chmod 444 /unlock_code.txt

if [ $# -eq 0 ]; then
    xinetd -d
else
    exec "$@"
fi
