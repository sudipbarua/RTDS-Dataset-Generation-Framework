import multiprocessing
import sched
import time

def method1():
    print('method 1')
    time.sleep(2)
    print('still method 1')

def method2():
    print('method 2')

def method3():
    print('method 3')
method_list = [method1, method2, method3]


def start_and_schedule_next_process(scheduler, counter, process_list):
    if counter < len(method_list):
        p = multiprocessing.Process(target=method_list[counter])
        p.start()
        process_list.append(p)
        counter += 1
        scheduler.enter(4, 1, start_and_schedule_next_process, (scheduler, counter, process_list))
    else:
        # All processes have been scheduled, do something else or exit the program
        pass

# Create a new scheduler instance
scheduler = sched.scheduler(time.time, time.sleep)

# Start scheduling the processes
counter = 0
process_list = []
scheduler.enter(4, 1, start_and_schedule_next_process, (scheduler, counter, process_list))
scheduler.run()