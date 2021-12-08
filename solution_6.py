import threading
import random
import time

class Table:

    def __init__(self, capacity):
        self.fork = []
        self.philosopher = []
        self.capacity = capacity
        
        self.counter_lock = threading.Lock()
        self.counter = 0
        self.wait_cond = []
        self.cond_lock = threading.Lock()
        
        self.waiting_threshold = int(capacity*0.4)

        for i in range(0, self.capacity):
            self.fork.append(threading.Lock())
            self.wait_cond.append(threading.Condition())
            self.philosopher.append(None)

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
        
    def get_philosopher_hunger(self, position):
        phil = self.philosopher[position]
        if phil is not None:
            return phil.hunger
        else: return 2**31
        
    def get_hunger_counter(self):
        self.counter_lock.acquire()
        ret = self.counter
        self.counter += 1
        self.counter_lock.release()
        return ret
        

class Philosopher:

    def __init__(self, table, position):
        self.__stateDictionary = {0 : "THINKING", 1 : "HUNGRY", 2 : "EATING", 3 : "WAITING"}
        self.table = table
        self.hunger = 2**31

        try:
            table.add_philosopher(self, position)
        except ValueError:
            raise ValueError("Invalid position for philosopher to eat!")

        self.position = position
        self.state = 0
        
        self.left = (self.position - 1) % self.table.capacity
        self.right = (self.position + 1) % self.table.capacity

        self.left_fork = self.table.fork[self.position]
        self.right_fork = self.table.fork[self.right]

        t = threading.Thread(target = self.think, name = f"Philosopher {self.position}")
        t.start()

    def update_state(self, state):
        self.state = state
        if (state == 3):
            if (self.hunger_left <= self.hunger):
                msg = f"[Philosopher #{self.position}] is waiting philosopher #{self.left} because they have way lower hunger ({self.hunger_left}/{self.hunger})"
            elif (self.hunger_right <= self.hunger):
                msg = f"[Philosopher #{self.position}] is waiting philosopher #{self.right} because they have way lower hunger ({self.hunger_right}/{self.hunger})"
        else:
            msg = f"[Philosopher #{self.position}] changed state to {self.__stateDictionary[self.state]}"

        self.table.pencil.acquire()
        print(msg)
        self.table.pencil.release()

    def think(self):
        self.update_state(0)

        time.sleep(random.randint(0, 3))

        self.compare_hunger()
        
    def compare_hunger(self):
        self.update_state(1)
        self.hunger = self.table.get_hunger_counter()
        
        self.table.wait_cond[self.position].acquire()
   
        while (True):
            self.hunger_left = self.table.get_philosopher_hunger(self.left)
            self.hunger_right = self.table.get_philosopher_hunger(self.right)
            
            if ((self.hunger_left + self.table.waiting_threshold < self.hunger ) or (self.hunger_right + self.table.waiting_threshold < self.hunger)):
                self.update_state(3)
                self.table.wait_cond[self.position].wait()
            else: break
            
        self.take_fork()

    def take_fork(self):

        self.left_fork.acquire()
        time.sleep(3)
        self.right_fork.acquire()

        self.eat()

    def eat(self):
        self.hunger = -(self.table.waiting_threshold + 1)
        self.update_state(2)

        time.sleep(random.randint(0, 1))

        self.left_fork.release()
        self.right_fork.release()
        self.finalize()

        
    
    def finalize(self):
        self.hunger = 2**31
        
        self.table.wait_cond[self.left].acquire()
        self.table.wait_cond[self.left].notifyAll()
        self.table.wait_cond[self.left].release()
        
        self.table.wait_cond[self.right].acquire()
        self.table.wait_cond[self.right].notifyAll()
        self.table.wait_cond[self.right].release()
        
        self.table.wait_cond[self.position].release()
        return 0