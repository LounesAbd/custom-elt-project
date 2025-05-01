import subprocess
import time

def wait_for_postgres(host, max_retries=5, delay_seconds=20):
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True)
            if "accepting connections" in result.stdout:
                print(f"Postgres is ready on {host}")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Postgres not ready yet: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})"
            )
            time.sleep(delay_seconds)
    print(f"Postgres not ready after {max_retries} attempts.")
    return False

if not wait_for_postgres(host="source_postgres"):
    print("Postgres is not ready. Exiting.")
    exit(1)

print("Starting ETL process...")

source_config = {
    'db_name': 'source_db',
    'user': 'postgres',
    'password': 'secret',
    'host': 'source_postgres'
}

destination_config = {
    'db_name': 'destination_db',
    'user': 'postgres',
    'password': 'secret',
    'host': 'destination_postgres'
}

dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['db_name'],
    '-f', 'data_dump.sql',
    '-w'
]

subprocess_env = dict(PGPASSWORD=source_config['password'])

subprocess.run(dump_command, env=subprocess_env, check=True)

load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['db_name'],
    '-a', '-f', 'data_dump.sql',
    '-w'
]

subprocess_env = dict(PGPASSWORD=destination_config['password'])

subprocess.run(load_command, env=subprocess_env, check=True)

print("ETL process completed successfully.")