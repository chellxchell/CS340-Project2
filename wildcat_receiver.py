import common
import threading
import time

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
        self.logged = set()

    def receive(self, packet_byte_array):
        # check checksum
        checksum = packet_byte_array[-2:]
        sum1, sum2 = self.getChecksum(packet_byte_array[:-2])
        if checksum[0] != sum1 or checksum[1] != sum2:
            # checksum failed, drop packet
            # print(f"Packet corrupted, packet dropped")
            return
        else:
            # parse packet
            seq_num = int.from_bytes(packet_byte_array[0:2],byteorder='big')
            if(seq_num not in self.logged):
                self.logged.add(seq_num)
                self.my_logger.commit(packet_byte_array[2:-2])
            if seq_num >= self.window_size + self.window_start:
                # out of window range, drop packet
                # print("Out of window range, packet dropped")
                return
            
            if(seq_num >= self.window_start):
                self.window[seq_num - self.window_start] = 1
                # shift window
                for packet in self.window:
                    if packet == 1:
                        self.window_start += 1
                        self.window.pop(0)
                        self.window.append(0)
                    else:
                        break
            
            # format bitmap
            byte_arr = []
            run_bit = ""
            for i,packet in enumerate(self.window):
                run_bit += str(packet)
                if len(run_bit) == 8 or len(self.window):
                    byte_arr.append(int(run_bit,2))
                    run_bit = ""

            ack = bytearray(self.window_start.to_bytes(2,byteorder='big'))
            ack.extend(bytearray(byte_arr))

            # create checksum and send
            sum1,sum2 = self.getChecksum(ack)
            checksum = bytearray(sum1.to_bytes(1,byteorder='big'))
            checksum.extend(bytearray(sum2.to_bytes(1,byteorder='big')))

            ack.extend(checksum)
            self.my_tunnel.magic_send(ack)

    def run(self):
        while not self.die:
            # time.sleep(0.5)
            pass
            
    def join(self):
        self.die = True
        super().join()

    
    def getChecksum(self, arr):
        sum1 = 0
        sum2 = 0
        for byte in arr:
            sum1 += byte
            sum2 += sum1
        sum1 %= 255
        sum2 %= 255
        return sum1,sum2