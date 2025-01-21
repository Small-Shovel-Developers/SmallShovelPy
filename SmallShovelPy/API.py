import requests
import json
import datetime
import time
from tqdm import tqdm

class API:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://small-shovel-demo-demo.onrender.com"

    def send_data(self, key_path, table, transmit_data):

        session = requests.session()
        session.headers.update({'Authorization': self.token})

        data = {
            "key_path": key_path,
            "new_key": table,
            "value": transmit_data
        }
        resp = session.post(self.base_url+"/api/client-data/add", data=json.dumps(data))
        if resp.status_code == 200:
            current_time = datetime.datetime.now()
            print(f"{current_time} - {table}: {resp.json()}")
            return True
        else:
            current_time = datetime.datetime.now()
            print(f"{current_time} - {table}: {resp}")
            return False
        
    def split_list(input_list, chunk_size):
        print("Splitting list")
        return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]
        
    def extend_data(self, key_path, table, transmit_data):

        session = requests.session()
        session.headers.update({'Authorization': self.token})

        data = {
            "key_path": f'{key_path}.{table}',
            "value": transmit_data
        }
        resp = session.post(self.base_url+"/api/client-data/extend", data=json.dumps(data))
        if resp.status_code == 200:
            return True
        else:
            current_time = datetime.datetime.now()
            print(f"{current_time} - chunk transmission failure: {resp}")
            return False

    def send_table(self, df, key_path, table):
        
        df_json_f = df.to_json(orient='records', default_handler=str)
        df_json = json.loads(df_json_f)

        if len(df_json) < 50_000:
            return self.send_data(key_path, table, df_json)
        else:
            print(f"{datetime.datetime.now()}: Table is too large, initializing in API and chunking data...")
            self.send_data(key_path, table, [])
            time.sleep(1)

            print(f"{datetime.datetime.now()}: Chunking data for transmission...")
            chunk_size = 20_000
            chunks = [df_json[i:i + chunk_size] for i in range(0, len(df_json), chunk_size)]
            print(f"{datetime.datetime.now()}: Chunks to transmit: {len(chunks)}")

            failed_rows = []
            status_message = ""
            n = 0

            print(f"{datetime.datetime.now()}: Beginning transmission of chunks...")
            for chunk in tqdm(chunks, desc=f"Uploading {table} data", unit="chunks"):
                n+=1

                status = self.extend_data(key_path, table, chunk)
                status_message += f"- Chunk {n} Transmit Success: {status}\n"

                if not status:
                    failed_rows += chunk

                time.sleep(1)
            
            print(f"{table} had {len(failed_rows)} failed rows")
            return status

    def append_table(self, df, key_path, table):

        # TODO: Add checking that the table to extend exists.
        
        df_json_f = df.to_json(orient='records', default_handler=str)
        df_json = json.loads(df_json_f)

        if len(df_json) < 50_000:
            return self.extend_data(key_path, table, df_json)
        else:
            print(f"{datetime.datetime.now()}: Chunking data for transmission...")
            chunk_size = 20_000
            chunks = [df_json[i:i + chunk_size] for i in range(0, len(df_json), chunk_size)]

            failed_rows = []
            status_message = ""
            n = 0

            print(f"{datetime.datetime.now()}: Beginning transmission of chunks...")
            for chunk in tqdm(chunks, desc=f"Uploading {table} data", unit="chunks"):
                n+=1

                status = self.extend_data(key_path, table, chunk)
                status_message += f"- Chunk {n} Transmit Success: {status}\n"
                if not status:
                    failed_rows += chunk

                time.sleep(1)
            
            print(f"{table} had {len(failed_rows)} failed rows")
            return status

# Transmitting Data
# current_time = datetime.datetime.utcnow()
# print(f"{current_time} - Transmitting Data...")

# processed_tables = {

# }

# collection = ""

# send_data("", collection, "Initialization")

# for table in processed_tables:

#     df = processed_tables[table]
