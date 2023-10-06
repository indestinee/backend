DB_PATH="/tmp/mountd/disk1_part1/backend/backend.db" FTP_ROOT_PATH="/tmp/mountd/disk1_part1/Files" waitress-serve --host 127.0.0.1 --port 23303 --call 'src.flaskr.server:create_app'
