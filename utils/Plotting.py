import matplotlib.pyplot as plt
import numpy as np

class Plotter:
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.x:list = []
        self.y:list = []
        self.line, = self.ax.plot([], [], label="Scores")
        self.avg_line, = self.ax.plot([], [], linestyle='--', label="Trend")
        self.ax.legend()
        plt.title("Flappy Bird Scores")
        plt.xlabel("Iterations")
        plt.ylabel("Score")

    def add_game(self, score:int, avg:int=-1):
        """Adds Game's New Values & Update Graph"""
        if avg == -1:
            avg = score
        self.y.append(avg)
        self.x.append(len(self.y))
        self.update_plot(avg)

    def save_graph(self, location:str):
        """Saves Graph to Folder"""
        try:
            plt.savefig(f"{location}/FlappyScores.png")
            print("Graph saved!")
        except Exception:
            print(f"Can't Save Graph, Folder {location} does not exist.")

    def update_plot(self, avg:int):
        """Update Graph Visual"""
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.y)

        if len(self.x) > 1:
            avg_arr = np.full(len(self.y), avg, dtype=float)
            self.avg_line.set_xdata(self.x)
            self.avg_line.set_ydata(avg_arr)

        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def close(self):
        """Close Graph"""
        plt.ioff()
        plt.close(self.fig)
