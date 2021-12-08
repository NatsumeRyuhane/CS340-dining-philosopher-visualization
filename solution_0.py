import threading
import random
import time

class Table:

    def __init__(self, capacity):
        self.fork = []
        self.philosopher = []
        self.capacity = capacity

        for i in range(0, self.capacity):
            self.fork.append(threading.Lock())
            self.philosopher.append(None)

        # a pencil on the table prevents the shared output problem
        self.pencil = threading.Lock()

    def add_philosopher(self, philosopher, position):
        if position in range(0, self.capacity):
            self.philosopher[position] = philosopher
        else:
            raise ValueError

    def get_philosopher_status(self, position):
        phil = self.philosopher[position]
        if phil is not None:
            return phil.state
        else: return 0

class Philosopher:

    def __init__(self, table, position):
        self.__stateDictionary = {0 : "THINKING", 1 : "HUNGRY", 2 : "EATING"}
        self.table = table

        try:
            table.add_philosopher(self, position)
        except ValueError:
            raise ValueError("Invalid position for philosopher to eat!")

        self.position = position
        self.state = 0

        self.left = self.position % self.table.capacity
        self.right = (self.position + 1) % self.table.capacity

        self.left_fork = self.table.fork[self.position]
        self.right_fork = self.table.fork[self.right]

        t = threading.Thread(target = self.think, name = f"Philosopher {self.position}")
        t.start()

    def update_state(self, state):
        self.state = state
        self.table.pencil.acquire()
        print(f"[Philosopher #{self.position}] changed state to {self.__stateDictionary[self.state]}")
        self.table.pencil.release()

    def think(self):
        self.update_state(0)

        time.sleep(random.randint(0, 3))

        self.take_fork()

    def take_fork(self):
        self.update_state(1)

        self.left_fork.acquire()
        time.sleep(3)
        self.right_fork.acquire()

        self.eat()

    def eat(self):
        self.update_state(2)

        time.sleep(random.randint(0, 3))

        self.left_fork.release()
        self.right_fork.release()

        return 0