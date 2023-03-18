from threading import Thread
# from core_management.consumer import main


class Rabbit_Consumer(Thread):
    def __init__(self, seconds):
        """Note that when you override __init__, you must
           use super() to call __init__() in the base class
           so you'll get all the "chocolately-goodness" of
           threading (i.e., the magic that sets up the thread
           within the OS) or it won't work.
        """

        super().__init__()
        self.delay = seconds
        self.is_done = False

    def connect_to_ui_server(self):
        pass

    def done(self):
        self.is_done = True

    def run(self):
        # while not self.is_done:
        main()

        print('thread done')
