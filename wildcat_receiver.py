import common
import threading

class wildcat_receiver(threading.Thread):
    def __init__(self, allowed_loss, window_size, my_tunnel, my_logger):
        super(wildcat_receiver, self).__init__()
        self.allowed_loss = allowed_loss
        self.window_size = window_size
        self.my_tunnel = my_tunnel
        self.my_logger = my_logger
        self.die = False
        
        self.window = [0] * self.window_size
        self.window_start = 0
        self.last_received = 0

    def receive(self, packet_byte_array):
        # check checksum
        checksum = packet_byte_array[-2:]
        sum1, sum2 = self.getChecksum(packet_byte_array[0:-2])
        if int.from_bytes(checksum[0],byteorder='big') != sum1 or int.from_bytes(checksum[1],byteorder='big') != sum2:
            # drop packet
            pass
        else:
            # parse packet
            self.my_logger.commit(packet_byte_array)
            seq_num = int.from_bytes(packet_byte_array[0:2],byteorder='big')
            self.window[seq_num - self.window_start] = 1

            # shift window
            for packet in self.window:
                if packet == 1:
                    self.window_start += 1
                    self.window.pop(0).append(0)
                else:
                    break
            
            # format bitmap
            byte_arr = []
            run_bit = ""
            for packet,i in enumerate(self.window):
                run_bit += packet
                if len(run_bit) == 8 or len(self.window):
                    byte_arr.append(int(run_bit,2))

            ack = bytearray(self.window_start).extend(bytearray(byte_arr))

            # create checksum and send
            sum1, sum2 = self.getChecksum(ack)
            checksum1 = bytearray(sum1.to_bytes(16,byteorder='big'))
            checksum2 = bytearray(sum2.to_bytes(16,byteorder='big'))
            ack.extend(checksum1.extend(checksum2))

            self.my_tunnel.magic_send(ack)
        pass

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