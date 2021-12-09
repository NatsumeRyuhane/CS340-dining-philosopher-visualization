import threading
import random
import time

class Table:

    def __init__(self, capacity):
        self.fork = []
        self.philosopher = []
        self.capacity = capacity

        self.deadlock_timer_expire = 10

        # a pencil on the table prevents the shared output problem
        self.pencil = threading.Lock()

        self.statistics = []
        self.change_count = 0

        self.phil_count = 0
        self.finished_phil = 0


        for i in range(0, self.capacity):
            self.fork.append(threading.Lock())
            self.philosopher.append(None)
            self.statistics.append({})

        # an observer on the table to help detect the deadlock condition
        # also used in the eye of the universe to collapse possibilities to create a new universe
        obeserver = threading.Thread(target=self.observe, name=f"Observer")
        obeserver.start()

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

        self.draw_statistics()

    def draw_statistics(self):
        pass




class Philosopher:

    def __init__(self, table, position):
        self.__stateDictionary = {0 : "THINKING", 1 : "HUNGRY", 2 : "EATING", 99 : "FINISHED"}
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

        self.start_time = time.time()

        t = threading.Thread(target = self.think, name = f"Philosopher {self.position}")
        t.start()

    def update_state(self, state):
        self.state = state
        self.table.pencil.acquire()

        if state == 99: self.table.finished_phil += 1

        self.table.statistics[self.position][self.state] = round(1000*(time.time() - self.start_time), 2)
        self.table.change_count += 1
        print(f"[Philosopher #{self.position}] changed state to {self.__stateDictionary[self.state]}")

        self.table.pencil.release()

    def think(self):
        self.update_state(0)

        time.sleep(random.randint(0, 3))

        self.take_fork()

    def take_fork(self):
        self.update_state(1)

        self.left_fork.acquire()
        time.sleep(0)
        self.right_fork.acquire()

        self.eat()

    def eat(self):
        self.update_state(2)

        time.sleep(random.randint(0, 3))

        self.left_fork.release()
        self.right_fork.release()

        self.update_state(99)
        return 0