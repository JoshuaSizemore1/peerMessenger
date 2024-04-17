import socket
import threading
import tkinter as tk

header = 64
stopServer = False


#Server part of code
clients =[]
server = None
clientNum = 0
nextClient = "client" + str(clientNum + 1)
commands = ["/join", "/help", "/clients", "/create"]
serverRunning = False
clientNumChange = False
rooms = []

#Server global methods
def stopServer():
    global serverRunning
    global clientNum

    clients.clear()
    clientNum = 0
    serverRunning = False


def startServerThread():
    global serverRunning

    serverRunning = True
    serverThread = threading.Thread(target= startServer)
    serverThread.start()



def startServer():
    global server
    global serverRunning
    global clientNumChange

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverIp ="127.0.0.1"
    port = 8000
    server.bind((serverIp, port))
    server.listen(1)

    clientTetheringThread = threading.Thread(target= clientTethering)
    clientTetheringThread.start()
    
    print("Online")


    while serverRunning:

        #print(clientNum)
        #print(clients)

        if clientNumChange == True:
            currentUserText.config(state= "normal")
            currentUserText.delete("1.0", tk.END)
            for i in range(len(clients)):
                currentUserText.insert(tk.END, "\n" + str(clients[i].id))
            currentUserText.config(state= "disabled")
            clientNumChange = False



    print("Killed")
    server.close()



def clientTethering():
    global server
    global clientNum
    global nextClient
    global clientNumChange

    try:
        while serverRunning:
            clientNum = clientNum + 1
            nextClient = "client" + str(clientNum)
            clientSocket, addr = server.accept()

            clients.append(exec("%s = None" % (nextClient)))
            for i in range(len(clients)):
                if clients[i] == None:
                    clients[i] = Client("Undef", clientNum, clientSocket, addr,)
            clientNumChange = True


            thread = threading.Thread(target= clients[clientNum - 1].handleClient)
            thread.start()
    except Exception as e:
        pass


#Sends a message to the specified client
def sendConsoleMess(client, msg):
  message = msg.encode("utf-8")
  msgLength = len(message)
  sendLength = str(msgLength).encode("utf-8")
  sendLength += b' ' * (header - len(sendLength))
  client.send(sendLength)
  client.send(message)


#Gets the message from the server(console) text entry (messageEntry) and sends it to every client using the sendConsoleMess method
def consoleMess(event):
    for i in range(len(clients)):
        sendConsoleMess(clients[i].clientSocket, ("Console: "+ messageEntry.get()))
    messageEntry.delete(0, tk.END)


class Client():
    def __init__ (self, username, id, clientSocket, addr,):
        self.username = username
        self.id = id
        self.clientSocket = clientSocket
        self.addr = addr,
        self.request = ""
        self.requestUpdate = False
        self.requestLength = 0
        self.session = True
        self.currentRoom = 0

    def clientRequest(self):
        try:
            while self.session == True:
                self.requestLength  = self.clientSocket.recv(header).decode("utf-8")
                self.requestLength = int(self.requestLength)
                self.request = self.clientSocket.recv(self.requestLength).decode("utf-8")
                self.requestUpdate = True
        except Exception as e:
            for i in range(len(clients)):
                if clients[i].id == self.id:
                    del clients[i]

    
    def handleClient(self):
        global clientNum
        global clientNumChange

        response = "Connected"
        sendConsoleMess(self.clientSocket, response)

        self.requestLength  = self.clientSocket.recv(header).decode("utf-8")
        self.requestLength = int(self.requestLength)
        self.username = self.clientSocket.recv(self.requestLength).decode("utf-8")
        if self.username == "Guest":
            self.username = self.username + str(self.id)
        print( self.username + " joined the server.")

        requestThread = threading.Thread(target= self.clientRequest)
        requestThread.start()

        while self.session == True:
    
            if self.requestUpdate == True:

                if(self.request[0:1] == "/"):
                    if(self.request[1:] == commands[0]):
                        if len(rooms) > 1:
                            for i in range(len(rooms)):
                                if self.request[6: ] == clients[i]:
                                    sendConsoleMess(self.clientSocket, "Connecting ...")
                                    
                    if(self.request[1:] == "help"):
                        sendConsoleMess(self.clientSocket, "")
                    if(self.request[1:] == "clients"):
                        if len(clients) > 1:
                            sendConsoleMess(self.clientSocket, " ".join(clients.username))
                        else:
                            sendConsoleMess(self.clientSocket, "You're all Alone :(")

                elif(self.request == "close"):
                    self.session = False
                else:
                    print(self.username + ": " + self.request)
                self.requestUpdate = False


        print(self.username + " left the server.")
        self.clientSocket.close()
        for i in range(len(clients)):
            if clients[i].id == self.id:
                del clients[i]
        clientNum = clientNum - 1
        clientNumChange = True



"""
NEXT THING TO DO: 
finish server messaging
"""


#Tkinter part of code
win = tk.Tk()
win.geometry("700x350")
win.title("Message Server")

messageEntry = tk.Entry(win)
startButton = tk.Button(win, text= "Start Server", command= startServerThread)
endButton = tk.Button(win, text= "Shut Off Server", command= stopServer)


currentUserText = tk.Text(win, bg= None, bd= 0, font= "Helvetica 11")



def close():
    global serverRunning
    for i in range(len(clients)):
        clients[i].session = False
    serverRunning = False
    win.destroy()

win.protocol("WM_DELETE_WINDOW", close)
win.bind('<Return>', consoleMess)


messageEntry.pack(anchor= "s")
endButton.pack(anchor= "center")
startButton.pack(anchor= "center")
currentUserText.pack(anchor= "center")
win.mainloop()