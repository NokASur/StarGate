Simple Client-Server application with chatting/lobby functions

To use on your machine:

    1) Clone the repo "git clone https://github.com/NokASur/StarGate"
    2) Move to the StarGate folder "cd StarGate"
    3) From the StarGate folder run "touch database.env"
    4) Specify these environmental variables for your DB inside database.env:
           POSTGRES_USER=...
           POSTGRES_PASSWORD=...
           POSTGRES_HOST=...
           POSTGRES_PORT=...
           POSTGRES_DB=...
    5) Run docker compose up --build for a server to start
    6) Run any required amount of client instances with "python Client/main.py"
    7) ???
    8) PROFIT!