"""A python file that contains the Participant object and Poller class, used in randopoll.py.

Within the Participant object class we have an init method that initializes
participant variables. Also within this class is a string method that returns
a string of the participant variables. After this class lies the Poller class
which is used to open, access and modify participant.csv file. There's an enter and 
exit method that opens and writes in the csv. An init method that initializes
variables used by the class. Iter, next, and find_participant methods that
are in charge of iterating through participants and the logic that go behind that.
After those are the categorical incrementing methods, such as polled and attempted.
"""
import random
# Participant object that will hold information regarding the participant collumns


class Player:
    # Participant variables
    def __init__(self, name: str, polled: int, correct: int, attempted: int, excused: int):
        self.name = name
        self.polled = polled
        self.correct = correct
        self.attempted = attempted
        self.excused = excused

    # __str__ method that returns a participants information in string format
    def __str__(self):
        return (self.name + "," + str(self.polled) + "," + str(self.correct) + "," + str(self.attempted) + "," + str(self.excused))


# Poller class that opens, accesses, and modifies csv file (and all the logic behind that)

class Poller:
    # __init__ initializes poller variables that help organize participant objects
    def __init__(self, file: str):
        self.file = file
        self.participants_list = []
        self.current_participant_index = (len(self.participants_list) - 1)
        self.terminate = False

    # __enter__ method opens the csv file, reads it, and digests the info such that the participant objects are
    # not only created, but put in a list in which can be accessable throughout the program. There are also a
    # ValueError that will be raised if the csv file isn't formatted correctly (too many collumns or too few)
    def __enter__(self):
        with open(self.file, 'r') as f:
            for row in f:
                split_row = row.split(',')
                if (len(split_row) > 5) or (len(split_row) < 5):
                    raise ValueError('File is formatted incorrectly.')
                self.participants_list.append(Participant(split_row[0], int(
                    split_row[1]), int(split_row[2]), int(split_row[3]), int(split_row[4])))
        return self

    # find_participants is the method that handles the logic in finding which participant has the lowest
    # number of polls. This method also finds a random participant in which to choose upon if the lowest
    # participants are tied.
    def find_participant(self):
        lowest_index = 0
        lowest_polled = self.participants_list[lowest_index].polled
        low_list = []
        # Loop will identify the minimum
        for i in range(len(self.participants_list)):
            if self.participants_list[i].polled < lowest_polled:
                lowest_polled = self.participants_list[i].polled
                lowest_index = i
        # This loop will add participants who have the minimum polled to another list
        for i in range(len(self.participants_list)):
            if self.participants_list[i].polled == lowest_polled:
                low_list.append(i)
        lowest_index = random.randrange(len(low_list))
        return low_list[lowest_index]

    # __exit__ method is run whenever the __next__ method raises StopIteration. This method
    # writes the participant info into the csv file.
    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.file, 'w') as f:
            for participant in self.participants_list:
                f.write(str(participant) + '\n')

    def __iter__(self):
        return self

    # __next__ method is in charge of identifying the next participant to call on by
    # calling onto the find_participant method which returns said participant index.
    # This method is also raises ValueError when it detects the participant_list is empty,
    # and also raises StopIteration when stop() is called.
    def __next__(self):
        if len(self.participants_list) == 0:
            raise ValueError('File is empty.')
        if self.terminate == True:
            raise StopIteration
        self.current_participant_index = self.find_participant()
        return self.participants_list[self.current_participant_index].name

    # The following are methods that increment their respective participant variables.
    def polled(self):
        self.participants_list[self.current_participant_index].polled += 1

    def correct(self):
        self.polled()
        self.participants_list[self.current_participant_index].correct += 1

    def attempted(self):
        self.polled()
        self.participants_list[self.current_participant_index].attempted += 1

    def excused(self):
        self.polled()
        self.participants_list[self.current_participant_index].excused += 1

    def missing(self):
        self.polled()

    # stop() sets self.terminate to true which tells the __next__ function to StopIteration.
    def stop(self):
        self.terminate = True

    # total returns the total number of times the participants have been polled.
    def total(self):
        total = 0
        for participant in self.participants_list:
            total += participant.polled
        return total
