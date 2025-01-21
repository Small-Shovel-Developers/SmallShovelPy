import socket
import threading
import json
import pandas as pd

class ClientShell:
    def __init__(self):
        self.selected_client = None
        self.active_clients = []
        self.client_ports = {}
        self.help_statement = """
Available commands:
  - show clients: List all active clients.
  - select client <client_name>: Select a specific client to interact with.
  - show pipelines: Show pipelines for the selected client.
  - run pipeline <pipeline_name>: Run a specific pipeline on the selected client.
  - ex: Exits the currently selected client. If no client is selected, exits the shell.
  - exit: Exit the shell.
"""

    def is_empty_or_whitespace(self, s):
        return not s.strip()
    
    def get_active_clients(self):
        port = 5000
        for i in range(11):
            port += i
            command = "show clients"
            resp = self.send_command(host='127.0.0.1', port=port, command=command)
            try:
                data = json.loads(resp)
                self.active_clients += data
                for client in data:
                    self.client_ports[client['name']] = client['port']
                return data
            except:
                pass
        return None

    def send_command(self, host, port, command):
        """Send a command to a specific client."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, port))
                client_socket.sendall(command.encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                return response
        except ConnectionRefusedError:
            return "Unable to connect to the client."
        except Exception as e:
            return f"Error: {e}"

    def shell(self):
        """Start an interactive shell."""
        print("Welcome to the Client Shell. Type 'help' for a list of commands.")
        while True:
            try:
                if self.selected_client:
                    prompt_location = f"-{self.selected_client}"
                else:
                    prompt_location = ""
                command = input(f"shovel-shell{prompt_location}> ").strip()
                if self.is_empty_or_whitespace(command):
                    print()

                elif command == "exit":
                    print("Exiting Client Shell.")
                    break

                elif command == "ex":
                    self.selected_client = None
                    print()

                elif command == "help":
                    print(self.help_statement)

                elif command == "show clients":
                    print("Active clients:")
                    # Placeholder: Replace with real logic to fetch client list
                    clients = self.get_active_clients()
                    if clients:
                        df = pd.DataFrame(clients)
                        print(df.to_markdown(index=False))
                    else:
                        print("No clients available")
                
                elif command.startswith("select client "):
                    client_name = command[len("select client "):].strip()
                    self.selected_client = client_name
                    print(f"Selected client: {client_name}")

                elif command == "show pipelines":
                    if not self.selected_client:
                        print("No client selected. Use 'select client <client_name>' first.")
                    else:
                        print(f"Fetching pipelines for client: {self.selected_client}")
                        port = self.client_ports[self.selected_client]
                        resp = self.send_command(host='127.0.0.1', port=port, command=command)
                        print(resp)

                elif command.startswith("run pipeline "):
                    if not self.selected_client:
                        print("No client selected. Use 'select client <client_name>' first.")
                    else:
                        pipeline_name = command[len("run pipeline "):].strip()
                        print(f"Running pipeline '{pipeline_name}' on client '{self.selected_client}'...")
                        port = self.client_ports[self.selected_client]
                        resp = self.send_command(host='127.0.0.1', port=port, command=command)
                        print(resp)

                elif command.startswith("shutdown"):
                    parts = command.split()
                    if self.selected_client:
                        port = self.client_ports[self.selected_client]
                        resp = self.send_command(host='127.0.0.1', port=port, command="shutdown")
                        print(resp)                        
                    elif len(parts) > 1:
                        if parts[1] in self.client_ports.keys():
                            port = self.client_ports[parts[1]]
                            resp = self.send_command(host='127.0.0.1', port=port, command="shutdown")
                            print(resp)
                        else:
                            print("Unable to find specified client")
                    else:
                        print("You must select a client before running shutdwon or specify a client in the command: shutdown Client2")
                else:
                    print("Unknown command. Type 'help' for a list of commands.")

            except KeyboardInterrupt:
                print("\nExiting Client Shell.")
                break

if __name__ == "__main__":
    shell = ClientShell()
    shell.shell()
