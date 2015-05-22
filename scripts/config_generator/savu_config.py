'''
Created on 21 May 2015

@author: ssg37927
'''

import os

from savu.data.process_data import ProcessList


class Content(object):

    def __init__(self, filename):
        self.process_list = ProcessList()
        if os.path.exists(filename):
            print "Opening file %s" % (filename)
            self.process_list.populate_process_list(filename)

    def display(self):
        print self.process_list.process_list

def help(content, arg):
    print "  commands available are:"
    print "    help : this help"
    print "    open : opens or creates a new configuration file"
    print "    disp : display the processes in the list"
    return content

def open(content, arg):
    return Content(arg)

def disp(content, arg):
    content.display()
    return content

commands = {'open': open,
            'help': help,
            'disp': disp}

if __name__ == '__main__':
    print "Starting Savu Config tool"

    # set up things
    input_string = "startup"
    content = Content("")

    while True:
        input_string = raw_input(">>> ").strip()
        print "command is '%s'" % (input_string)

        command = input_string.split()[0]
        arg = ' '.join(input_string.split()[1:])

        if 'exit' in command:
            break

        # try to run the command
        if command in commands.keys():
            content = commands[command](content, arg)
        else:
            print "I'm sorry, thats not a command I recognise, try help"

    print "Thanks for using the application"