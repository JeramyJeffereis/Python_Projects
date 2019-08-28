Jeramy Jeffereis
                        Client-Server-Jumble-Game README
RUN INSTRUCTIONS:
	Before attempting to run the program ensure that the following four files have been cloned
into the same folder: Echo-Client.py, Jumble.py, Thread-Server.py, and WordList.txt. Once this is
done, run Thread-Server.py in it's own process. While Thread-Server.py is running, you can concurrently 
run Echo-Client.py in any number of seperate processes to play the game and communicate simultaneously 
with the same server. When you wish to exit a given client process simply enter 'exit' when prompted 
to give an answer. Make sure that you exit all client processes before closing the server or else an
error will occur.
