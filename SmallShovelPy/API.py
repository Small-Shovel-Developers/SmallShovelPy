import requests
import json
import datetime
import time
import tqdm

class API:
    def __init__(self, token):
        self.token = token

    def send_data(self, key_path, table, transmit_data):

        base_url = "https://small-shovel-demo-demo.onrender.com"
        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ik5ORUNTZXJ2aWNlQWdlbnQiLCJwZXJtaXNzaW9uc19jbGFzcyI6IkNBMlMiLCJjb21wYW55IjoiTk5FQyJ9.sYUz3czqQrcZPrt2-zegtpmu1k5oQFi-OfdICNWgNug"
        session = requests.session()
        session.headers.update({'Authorization': self.token})

        data = {
            "key_path": key_path,
            "new_key": table,
            "value": transmit_data
        }
        resp = session.post(base_url+"/api/client-data/add", data=json.dumps(data))
        if resp.status_code == 200:
            current_time = datetime.datetime.utcnow()
            print(f"{current_time} - {table}: {resp.json()}")
            return True
        else:
            current_time = datetime.datetime.utcnow()
            print(f"{current_time} - {table}: {resp}")
            return False
        
    def split_list(input_list, chunk_size):
        return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]
        
    def extend_data(self, key_path, table, transmit_data):

        base_url = "https://small-shovel-demo-demo.onrender.com"
        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ik5ORUNTZXJ2aWNlQWdlbnQiLCJwZXJtaXNzaW9uc19jbGFzcyI6IkNBMlMiLCJjb21wYW55IjoiTk5FQyJ9.sYUz3czqQrcZPrt2-zegtpmu1k5oQFi-OfdICNWgNug"
        session = requests.session()
        session.headers.update({'Authorization': self.token})

        data = {
            "key_path": f'{key_path}.{table}',
            "value": transmit_data
        }
        resp = session.post(base_url+"/api/client-data/extend", data=json.dumps(data))
        if resp.status_code == 200:
            return True
        else:
            current_time = datetime.datetime.utcnow()
            print(f"{current_time} - chunk transmission failure: {resp}")
            return False

    def send_table(self, df, key_path, table):
        
        df_json_f = df.to_json(orient='records', default_handler=str)
        df_json = json.loads(df_json_f)

        if len(df_json) < 50_000:
            self.send_data(key_path, table, df_json)
            time.sleep(1)
        else:
            self.send_data(key_path, table, [])
            time.sleep(1)

            chunks = self.split_list(df_json, 20_000)
            failed_rows = []

            for chunk in tqdm(chunks, desc=f"Uploading {table} data", unit="chunks"):
                status = self.extend_data(key_path, table, chunk)
                if not status:
                    failed_rows += chunk

                time.sleep(1)
            
            print(f"{table} had {len(failed_rows)} failed rows")

# Transmitting Data
# current_time = datetime.datetime.utcnow()
# print(f"{current_time} - Transmitting Data...")

# processed_tables = {

# }

# collection = ""

# send_data("", collection, "Initialization")

# for table in processed_tables:

#     df = processed_tables[table]
