# SPDX-FileCopyrightText: Copyright (c) 2025 Software GmbH, Darmstadt, Germany and/or its subsidiaries and/or its affiliates
# SPDX-FileContributor: Dr. Gerald Ristow
# SPDX-FileContributor: René Walter
#
# SPDX-License-Identifier: Apache-2.0

from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)


class Plot:
    """Class is required so that plot updates when the timeseries changes
    """
    def __init__(self):
        self.fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Classifier for industrial timeseries data')


def run_gui(probability_series):
    """Opens up a GUI, which stays open until all nodes are labeled or the window is closed.

    Args:
        probability_series : labeled list by classfier

    Returns:
        supervised_series : final labeled list supervised by expert
    """
    print("INFO: starting gui")

    def increment_y(start_y,step_y):
        """Function to structure the objects of the gui within the y-axis

        Args:
            start_y : starting y-coordinate of latest object
            step_y : space between latest and new object

        Returns:
            return y_new : y-coordinate of new Object
        """
        return start_y + step_y

    def plot_values():
        """Plotting the graph of the actual timeseries

        Returns:
            None : returns nothing
        """
        plot.fig.clear()
        plot.ax = plot.fig.add_subplot(111)
        plot.ax.plot(probability_series[0][1])
        canvas.draw_idle()
        plot.ax.set_title('Classifier for industrial timeseries data')
        return None

    def update_labels(series):
        """After Clicking on a Button, the probabilites have to be updated for the next timeseries

        Args:
            series : probabilities

        Returns:
            None : returns nothing
        """
        prob_1.set(series[0][2][0] + " : " + str(series[0][2][1]) + "%")
        prob_2.set(series[0][3][0] + " : " + str(series[0][3][1]) + "%")
        prob_3.set(series[0][4][0] + " : " + str(series[0][4][1]) + "%")
        nodes_left.set("nodes left: " + str(len(series)) + "/" + str(max_nodes))
        return None

    def append_series(node, fragment, unit, series):
        """Append the final labeling of timeseries to supervised list.

        Args:
            node : labeled node
            fragment : fragment of labeled node
            unit : unit of labeled node
            series : series of labeled node

        Returns:
            None : returns nothing
        """
        supervised_series.append((node, fragment, unit, series))
        #print((node.get_browse_name(), fragment, unit, series))
        return None

    def next_ts(button_value):
        """After Clicking on a Button, the whole gui have to update in order to predict the next timeseries

        Args:
            button_value : value, which expert decided for labeling

        Returns:
            None : returns nothing
        """
        txtfld.delete(0, 'end')

        if button_value == "first":
            append_series(probability_series[0][0], probability_series[0][2][0], probability_series[0][2][2],
                          probability_series[0][2][3])
        elif button_value == "second":
            append_series(probability_series[0][0], probability_series[0][3][0], probability_series[0][3][2],
                          probability_series[0][3][3])
        elif button_value == "third":
            append_series(probability_series[0][0], probability_series[0][4][0], probability_series[0][4][2],
                          probability_series[0][4][3])
        else:
            # TODO Find a way to map the series,fragment etc to a label in respect to the decision of expert. For example if expert takes "Spannung", it should automaticall map "Volt" and "V".
            append_series(probability_series[0][0], button_value, "Platzhalter", "Platzhalter")

        probability_series.pop(0)
        if len(probability_series) == 0:
            root.quit()
            root.destroy()
            return None
        update_labels(probability_series)
        plot_values()
        return None

    #Initializing GUI with title, backround color etc.
    root = Tk()
    root.title('Classifier for industrial timeseries data')
    root.geometry("750x900")
    sag_color = '#011f3d'
    root['background'] = sag_color
    plot = Plot()
    supervised_series = []
    max_nodes = len(probability_series)

    #spacer
    lbl = Label(root, bg=sag_color, fg='white', font=("Helvetica", 4))
    lbl.pack(side=TOP)

    #starting point in y-coordinate for for the first Object in Gui
    start_y = 550
    #space in y-coordinate between two Objects
    step_y = 35

    place_y = start_y
    
    # All Objects of Probability #1
    lbl = Label(root, bg=sag_color, text="probability #1:", fg='white', font=("Helvetica", 16))
    lbl.place(relx=0.2, y=place_y, anchor="center")
    prob_1 = StringVar(root)
    lbl = Label(root,bg=sag_color, textvariable=prob_1, fg='white', font=("Helvetica", 16))
    lbl.place(relx=.5, y=place_y, anchor="center")
    place_y = increment_y(place_y, step_y)
    btn = Button(root, text="probability #1", fg='black', command=lambda: next_ts("first"))
    btn.place(relx=.5, y=place_y, anchor="center")
    place_y = increment_y(place_y, step_y)

    # All Objects of Probability #2
    lbl = Label(root, bg=sag_color, text="probability #2:", fg='white', font=("Helvetica", 16))
    lbl.place(relx=0.2, y=place_y, anchor="center")
    prob_2 = StringVar(root)
    lbl = Label(root,bg=sag_color, textvariable=prob_2, fg='white', font=("Helvetica", 16))
    lbl.place(relx=.5, y=place_y, anchor="center")
    place_y = increment_y(place_y, step_y)
    btn = Button(root, text="probability #2", fg='black', command= lambda: next_ts("second"))
    btn.place(relx=.5, y=place_y, anchor="center")
    place_y = increment_y(place_y, step_y)

    # All Objects of Probability #3
    lbl = Label(root, bg=sag_color, text="probability #3:", fg='white', font=("Helvetica", 16))
    lbl.place(relx=0.2, y=place_y, anchor="center")
    prob_3 = StringVar(root)
    lbl = Label(root,bg=sag_color, textvariable=prob_3, fg='white', font=("Helvetica", 16))
    lbl.place(relx=.5, y=place_y, anchor="center")
    place_y = increment_y(place_y, step_y)
    btn = Button(root, text="probability #3", fg='black', command= lambda: next_ts("third"))
    btn.place(relx=.5, y=place_y, anchor="center")
    place_y = increment_y(place_y, step_y)

    # All Objects of section: own decision
    lbl = Label(root,bg=sag_color, text="own decision", fg='white', font=("Helvetica", 16))
    lbl.place(relx=.5, y=place_y, anchor="center")
    place_y = increment_y(place_y, step_y)
    txtfld = Entry(root, text="This is Entry Widget", bd=5)
    txtfld.place(relx=.5, y=place_y, anchor="center")
    place_y = increment_y(place_y, step_y)
    btn = Button(root, text="probability #4", fg='black', command= lambda: next_ts(txtfld.get()))
    btn.place(relx=.5, y=place_y, anchor="center")

    # All Objects for section: nodes left
    nodes_left = StringVar(root)
    lbl = Label(root, bg=sag_color, textvariable = nodes_left, fg='white', font=("Helvetica", 12))
    lbl.place(relx=.9, rely=.99, anchor="center")

    # Importing SAG-Logo
    image = Image.open("sag.png")
    resize_image = image.resize((150, 150))
    img = ImageTk.PhotoImage(resize_image)
    panel = Label(root, image=img, borderwidth=0, highlightthickness=0)
    panel.place(relx=.09, rely=0.98, anchor="center")
    
    
    #initialize values
    update_labels(probability_series)
    plot.ax.plot(probability_series[0][1])
    canvas = FigureCanvasTkAgg(plot.fig, root)
    canvas.get_tk_widget().pack(side=TOP)

    root.mainloop()
    return supervised_series
