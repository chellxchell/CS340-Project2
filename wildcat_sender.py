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
        self.buffer = []
        self.receive_window = 0
        self.curr_packet = 0
        # add as needed
    
    # called with a bytearray when user wants to send a packet
    def new_packet(self, packet_byte_array):
        # prepend sequence number
        send_arr = bytearray(self.curr_packet.to_bytes(32,byteorder='big'))
        send_arr.extend(packet_byte_array)

        # calculate Fletcher-16 checksum
        sum1, sum2 = self.getChecksum(send_arr)
        checksum1 = bytearray(sum1.to_bytes(16,byteorder='big'))
        checksum2 = bytearray(sum2.to_bytes(16,byteorder='big'))
        send_arr.extend(checksum1.extend(checksum2))

        self.my_tunnel.magic_send(send_arr)
        pass

    # called with a bytearray when packet arrives
    def receive(self, packet_byte_array):
        # check checksum
        checksum = packet_byte_array[-2:]
        sum1, sum2 = self.getChecksum(packet_byte_array[0:-2])
        if int.from_bytes(checksum[0],byteorder='big') != sum1 or int.from_bytes(checksum[1],byteorder='big') != sum2:
            # drop packet
            pass
        else:
            seq_num = int.from_bytes(packet_byte_array[0:2],byteorder='big')
            payload = packet_byte_array[2:-2]
            bit_string = ""
            for byte in payload:
                bin_string += bin(int.from_bytes(byte,byteorder='big'))
            bit_string[len(bit_string) - self.window_size:]

        pass
    
    # running in the background
    def run(self):
        while not self.die:
            # TODO: your implementation comes here
            pass
    
    def join(self):
        self.die = True
        super().join()

    def getChecksum(self, arr):
        sum1 = 0
        sum2 = 0
        for byte in arr:
            sum1 += int.from_bytes(byte,byteorder='big')
            sum2 += sum1
        sum1 %= 255
        sum2 %= 255
        return sum1, sum2