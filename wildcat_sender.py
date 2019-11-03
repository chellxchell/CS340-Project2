import common
import threading

class wildcat_sender(threading.Thread):
    def __init__(self, allowed_loss, window_size, my_tunnel, my_logger):
        super(wildcat_sender, self).__init__()
        self.allowed_loss = allowed_loss
        self.window_size = window_size
        self.my_tunnel = my_tunnel
        self.my_logger = my_logger
        self.die = False
        # add as needed
    
    # called with a bytearray when user wants to send a packet
    def new_packet(self, packet_byte_array):
        self.my_tunnel.magic_send(packet_byte_array)
        #any unacknowledged packets will be resent within 0.5s
        pass

    # called with a bytearray when packet arrives
    def receive(self, packet_byte_array):
        # TODO: your implementation comes here
        pass
    
    # running in the background
    def run(self):
        while not self.die:
            # TODO: your implementation comes here
            pass
    
    def join(self):
        self.die = True
        super().join()