# change the import source to see different results
from solution_0 import Table, Philosopher

n = 5

table = Table(capacity = n)

for i in range(0, n):
    new_phil = Philosopher(table = table, position = i)