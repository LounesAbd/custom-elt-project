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
            print(f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(delay_seconds)
    print(f"Postgres not ready after {max_retries} attempts.")
    return False

def check_table_exists(db_config, table_name):
    check_command = [
        'psql',
        '-h', db_config['host'],
        '-U', db_config['user'],
        '-d', db_config['db_name'],
        '-c', f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}');"
    ]
    subprocess_env = dict(PGPASSWORD=db_config['password'])
    check_process = subprocess.run(check_command, env=subprocess_env, check=True, capture_output=True, text=True)
    check_output = check_process.stdout.strip()

    # Parse the output to check if the table exists
    if 't' in check_output:
        return True  # Table exists
    else:
        return False  # Table does not exist


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

# Step 1: Dump data from source database
print("Starting pg_dump (data dump from source)...")
dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['db_name'],
    '-f', 'data_dump.sql',
    '-w'
]

subprocess_env = dict(PGPASSWORD=source_config['password'])

try:
    subprocess.run(dump_command, env=subprocess_env, check=True)
    print("Data dump completed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error during pg_dump: {e}")
    exit(1)

# Step 2: Load data into destination database
print("Starting psql (loading data into destination)...")
load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['db_name'],
    '-a', '-f', 'data_dump.sql',
    '-w'
]

try:
    subprocess.run(load_command, env=subprocess_env, check=True)
    print("Data load completed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error during psql load: {e}")
    exit(1)

# Step 3: Wait until destination table (films) is available
print("Waiting for films table to be available in destination database...")
while not check_table_exists(destination_config, "films"):
    print("films table not found. Sleeping for 10 seconds...")
    time.sleep(10)

print("films table found. Proceeding with dbt...")


'''
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
'''