# Start Client
python3 Client.py test.txt localhost

# Start Server
python3 Server.py


# Network Simulation
1. Install Kathara by following the instructions [here](https://github.com/KatharaFramework/Kathara/blob/master/README.md#installation)
2. Download the [network simulation  ](https://drive.google.com/file/d/1IoOJNYWOyikIdnOTMmDI-ZYWQvBG5h6H/view?usp=sharing)
3. Move the client and server to the shared folder in the network simulation
3. Run the network simulation with  
`sudo kathara lstart`  
4. Introduce packet loss to the file server's ethernet port with  
`tc qdisc add dev eth0 root netem loss 50%`  
5. To remove the packet loss run  
`tc qdisc del dev eth0 root`
5. On client1 or 2 send files to the server with  
`cd /shared/files/client`  
`python3 Client.py test.txt localhost`
