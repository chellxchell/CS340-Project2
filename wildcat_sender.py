import common
import threading
import time

class wildcat_sender(threading.Thread):
    def __init__(self, allowed_loss, window_size, my_tunnel, my_logger):
        super(wildcat_sender, self).__init__()
        self.allowed_loss = allowed_loss
        self.window_size = window_size
        self.my_tunnel = my_tunnel
        self.my_logger = my_logger
        self.die = False
        
        self.window = [0] * self.window_size
        self.window_start = 0
        self.curr_packet = 0
        self.resend = {}
    
    # called with a bytearray when user wants to send a packet
    def new_packet(self, packet_byte_array):
        # prepend sequence number
        send_arr = bytearray(self.curr_packet.to_bytes(2,byteorder='big'))
        send_arr.extend(packet_byte_array)

        # calculate and append Fletcher-16 checksum
        sum1,sum2 = self.getChecksum(send_arr)
        checksum = bytearray(sum1.to_bytes(1,byteorder='big'))
        checksum.extend(bytearray(sum2.to_bytes(1,byteorder='big')))
        send_arr.extend(checksum)

        # queue to resend in 0.5 seconds
        self.resend[self.curr_packet] = send_arr.copy()
        self.curr_packet += 1
        
        self.my_tunnel.magic_send(send_arr)

    # called with a bytearray when packet arrives
    def receive(self, packet_byte_array):
        # print(f'received: {packet_byte_array}')

        # check checksum
        checksum = packet_byte_array[-2:]
        sum1, sum2 = self.getChecksum(packet_byte_array[0:-2])
        if checksum[0] != sum1 or checksum[1] != sum2:
            # failed checksum, drop packet
            # print(f"Packet corrupted, packet dropped")
            pass
        else:
            # parse packet

            # adjust window start
            rec_window_start = int.from_bytes(packet_byte_array[0:2],byteorder='big')
            if(rec_window_start < self.window_start):
                # duplicate ack, drop packet
                # print("Duplicate ack, nothing to do")
                return
            while(self.window_start < rec_window_start):
                if(self.window_start in self.resend):
                    del self.resend[self.window_start]
                self.window.pop(0)
                self.window.append(0)
                self.window_start += 1
                
            # parse bit array
            payload = packet_byte_array[2:-2]
            bit_string = ""
            for byte in payload:
                bit_string += bin(byte)[2:]
            bit_string = bit_string[:self.window_size]
            
            # update window
            for i,bit in enumerate(bit_string):
                self.window[i] |= int(bit)
                if self.window[i] == 1 and self.window_start + i in self.resend:
                    del self.resend[self.window_start + i]
    
    # running in the background
    def run(self):
        while not self.die:
            for key in self.resend:
                # print(f'resent {self.resend[key]}')
                self.my_tunnel.magic_send(self.resend[key].copy())
            # print(self.window)
            time.sleep(0.5)
    
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