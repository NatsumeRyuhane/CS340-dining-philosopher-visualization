import threading
import random
import time
import json

class Table:

    def __init__(self, capacity):
        self.fork = []
        self.philosopher = []
        self.capacity = capacity

        self.deadlock_timer_expire = 10
        self.statistics = []
        self.change_count = 0

        self.phil_count = 0
        self.finished_phil = 0
        
        # in this solution, each philosopher will take a number from a counter on the table when hungry
        # a philosopher will only be allowed to eat if it holds a lower value than its neighbors
        self.counter_lock = threading.Lock()
        self.counter = 0
        self.wait_cond = []
        self.cond_lock = threading.Lock()

        for i in range(0, self.capacity):
            self.statistics.append({})
            self.fork.append(threading.Lock())
            self.wait_cond.append(threading.Condition())
            self.philosopher.append(None)

        self.pencil = threading.Lock()

        observer = threading.Thread(target=self.observe, name=f"Observer")
        observer.start()

    def add_philosopher(self, philosopher, position):
        if position in range(0, self.capacity):
            self.pencil.acquire()
            self.phil_count += 1
            self.pencil.release()
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

    def observe(self):
        last_change_count = 0
        time_last_update = time.time()

        while True:
            self.pencil.acquire()
            if (last_change_count == self.change_count): pass
            else:
                last_change_count = self.change_count
                time_last_update = time.time()
            self.pencil.release()

            if (time.time() - time_last_update < self.deadlock_timer_expire):
                time.sleep(1)
            elif (self.phil_count != 0 and self.phil_count == self.finished_phil):
                print("Finished")
                break
            else:
                print("Deadlock detected!")
                break

        with open("result.txt", "w+") as savefile:
            savefile.write(str(self.statistics))


        with open("result.txt", "w+") as savefile:
            savefile.write(json.dumps(self.statistics, indent = 4))

        #draw(self.statistics)

class Philosopher:

    def __init__(self, table, position):
        self.__stateDictionary = {0 : "THINKING", 1 : "HUNGRY", 2 : "EATING", 3 : "WAITING", 99 : "FINISHED"}
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

        self.start_time = time.time()
        t = threading.Thread(target = self.think, name = f"Philosopher {self.position}")
        t.start()

    def update_state(self, state):
        self.state = state
        if (state == 3):
            if (self.hunger_left <= self.hunger):
                msg = f"[Philosopher #{self.position}] is waiting philosopher #{self.left} because they have lower hunger ({self.hunger_left}/{self.hunger})"
            elif (self.hunger_right <= self.hunger):
                msg = f"[Philosopher #{self.position}] is waiting philosopher #{self.right} because they have lower hunger ({self.hunger_right}/{self.hunger})"
        else:
            msg = f"[Philosopher #{self.position}] changed state to {self.__stateDictionary[self.state]}"

        self.table.pencil.acquire()
        if state == 99: self.table.finished_phil += 1
        self.table.statistics[self.position][self.state] = round(1000*(time.time() - self.start_time), 2)
        self.table.change_count += 1
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
            
            if ((self.hunger_left < self.hunger) or (self.hunger_right < self.hunger)):
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
        self.hunger = -1
        self.update_state(2)

        time.sleep(random.randint(0, 3))

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
        self.update_state(99)
        return 0