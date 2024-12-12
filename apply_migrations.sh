#!/bin/bash
set -e

alembic upgrade head
exec "$@"

# attrib +x apply_migrations.sh
# docker exec -it a869bbf472f6 alembic upgrade head