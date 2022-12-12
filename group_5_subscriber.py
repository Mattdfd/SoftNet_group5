import random
import tkinter

import numpy as np
import datetime
import json
import tkinter as tk 
import tkinter.ttk as ttk
import matplotlib
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

class Subscriber():

    def __init__(self,broker,port):        
        self.topics = [("OSCILLATIONS", 0),("AMPLITUDE", 1)]
        self.broker = broker
        self.port = port
        self.topicLists = {}
        self.current_topic = "OSCILLATIONS"
        self.maxDataPoints = 60       
        self.client = mqtt.Client()

    def append_val(self, topic, msg):       

        x_value = msg["Timestamp"]
        y_value = msg["y-value"]

        # Check if topic data exists in dictionary
        topic_data_points = self.topicLists.get(topic)
        if not topic_data_points: # create new lists if they don't exist
            topic_data_points = {
                "x_values": [],
                "y_values": []
            }
        if  y_value == 7:
            topic_data_points["x_values"].append("error")
            topic_data_points["y_values"].append(random.randint(-3,3))

            tkinter.messagebox.showerror("showerror", "Value out of Bounds")
        else: # update existing lists
            topic_data_points["x_values"].append(x_value)
            topic_data_points["y_values"].append(y_value)      

        # check if topic data has to many data points in it
        if len(topic_data_points["x_values"]) - 1 >= self.maxDataPoints:
            topic_data_points["x_values"].pop(0)
            topic_data_points["y_values"].pop(0)

        self.topicLists.update({topic: topic_data_points})

  
    def x_values(self):
        return self.get_values("x_values")
 
    def y_values(self):
        return self.get_values("y_values")

    def get_values(self, value_key): 
        # See if topic exists in dictionary
        topic_data_points = self.topicLists.get(self.current_topic)        
        if not topic_data_points:
            return []

        values = topic_data_points.get(value_key)        
        # see if the value key exists in sub-dictionary
        if not values:
            return []
        else:
            return values    

    def on_message(self, client, userdata, message):        
        msg = json.loads(message.payload.decode("utf-8"))
        self.append_val(message.topic,msg)
        # print("Received message '" + " '{}' , Timestamp '{}' ".format(str(msg["y-value"]),str(msg["Timestamp"]) ))

    def run(self):
        try:
            self.client = mqtt.Client()
            self.client.connect(self.broker, self.port)
            self.client.subscribe(self.topics)
            self.client.on_message = self.on_message
            self.client.loop_start()
        except:
            print("Connection Failed")
            exit()

class App(tk.Tk):
    def __init__(self):
        # create Subscriber object
        self.subscriber = Subscriber("mqtt.eclipseprojects.io", 1883)      

        # TKinter
        tk.Tk.__init__(self)
        self.title("Oscillation and Amplitude Graph")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.geometry("1000x1000")        

        frame = tk.Frame(self).pack()
        tk.Label(frame, text="Subscriber").pack(padx=10,pady=10)    

        # Figure and Graph Setup        
        self.init_graph()
        # UI Setup
        self.init_UI(frame)
        
               
        # start subscriber
        self.subscriber.run()

    def init_graph(self):
        figure = Figure((5,5), dpi=100)
        self.graph = figure.add_subplot(111)

        canvas = FigureCanvasTkAgg(figure,self)
        canvas.draw()
        canvas.get_tk_widget().place(
            relx=0.28,
            rely=0.5,
            anchor=tk.W,
            relheight=0.8,
            relwidth=0.7,            
        )

        self.ani = FuncAnimation(figure, self.animate, interval=1000)

    def init_UI(self, frame):
        self.currentTopic = tk.StringVar()
        self.currentTopic.set(self.subscriber.current_topic)

        tk.Label(frame, text="Topic:").place(
            relx=0.08,
            rely=0.1,
            anchor=tk.NW
        )

        ttk.Combobox(frame, textvariable=self.currentTopic, values=["AMPLITUDE", "OSCILLATIONS"]).place(
            relx=0.08,
            rely=0.12,
            anchor=tk.NW
        )

        tk.Button(frame, text="Change Topic", command=self.changeTopic).place(
            relx = 0.08,
            rely= 0.15,
            anchor=tk.NW
        )

    def animate(self, i):        
        # get Data
        x_data = list(self.subscriber.x_values())       

        dataLen = len(x_data)        

        if dataLen == 0:            
            return

        # clear plot
        self.graph.cla()

        # plot data
        self.graph.plot(self.subscriber.x_values(), self.subscriber.y_values())        

        x_labels = []              

        # Generate XLabels so they are more than line, eaiser to read
        if dataLen == 1: # if there is one element just create one label
            x_labels.append(str(x_data[0]).replace('-', '\n')) 
        else: # create labels
            x_labels = []
            labelCount = 5       
            lastLabelIndex = dataLen - 1
            labelPositions = []

            # calculate the index's that will contain labels
            for i in range(0, dataLen, max(int(lastLabelIndex/(labelCount - 1)), 1)):            
                labelPositions.append(i)
        
            # set last label position to be the last datapoint in the array
            labelPositions[len(labelPositions) - 1] = lastLabelIndex
            
            # Create labels for x axis if does not match a label position enter a empty string
            for i in range(0, dataLen):

                if i == labelPositions[0]:            
                    x_labels.append(str(x_data[i]).replace('-', '\n')) 
                    if len(labelPositions) > 0: # don't pop if last label
                         labelPositions.pop(0)                
                else:
                    x_labels.append("")              

        self.graph.set_xticks(self.graph.get_xticks())
        self.graph.set_xticklabels(x_labels)   

    def changeTopic(self): 
        self.subscriber.current_topic = self.currentTopic.get()     

    def on_closing(self):
        self.quit()
        self.destroy()



if __name__ == "__main__":
    app = App()
    app.mainloop()




            