from smartcard.scard import *
from smartcard.util import toHexString
import pickle
import sys

UID = []

class NFC_Reader():
	def __init__(self, uid = ""):
		self.uid = uid
		self.hresult, self.hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
		self.hresult, self.readers = SCardListReaders(self.hcontext, [])
		assert len(self.readers) > 0
		self.reader = self.readers[0]
		print("NFC : " +  str(self.reader))
		
		self.hresult, self.hcard, self.dwActiveProtocol = SCardConnect(
				self.hcontext,
				self.reader,
				SCARD_SHARE_SHARED,
				SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
		self.data_blocks = []

	def get_card_status(self):
		if self.hcard == 0:
			print('\nKartu tidak terdeteksi..\n')
			quit()
            
		hresult, reader, state, protocol, atr = SCardStatus(self.hcard)
		print("Status")
		if hresult != SCARD_S_SUCCESS:
			raise error, 'failed to get status: ' + SCardGetErrorMessage(hresult)
		value, value_hex = self.send_command([0xFF,0xCA,0x00,0x00,0x00])
		UID = value_hex[:-5]
		print('Reader: '), reader
		print('State: '), state
		print('Protocol: '), protocol
		print('UID: '), UID
		converted = toHexString(atr, format=0)
		print("------------------------\n")
		if(len(UID)>12):
			print("Kartu jenis ultralight tidak supoort duplikasi")
			quit()
		return converted

	def run(self):
		reader.get_card_status()
		ceking = ""
		value, value_hex = self.send_command([0xFF,0xCA,0x00,0x00,0x00])
		print(value_hex)
		value, value_hex = self.send_command([0xFF,0x00,0x00,0x00,0x08,0xD4,0x08,0x63,0x02,0x00,0x63,0x03,0x00])
		print(value_hex)
		value, value_hex = self.send_command([0xFF,0x00,0x00,0x00,0x06,0xD4,0x42,0x50,0x00,0x57,0xCD])
		print(value_hex)
		value, value_hex = self.send_command([0xFF,0x00,0x00,0x00,0x05,0xD4,0x08,0x63,0x3D,0x07])
		print(value_hex)
		value, value_hex = self.send_command([0xFF,0x00,0x00,0x00,0x03,0xD4,0x42,0x40])
		ceking = value_hex
		print(value_hex)
		value, value_hex = self.send_command([0xFF,0x00,0x00,0x00,0x05,0xD4,0x08,0x63,0x3D,0x00])
		print(value_hex)
		if(ceking == "D5 43 00 0A 90 00"):
			reader.run_write()
		else:
			print("Jenis kartu tidak writetable")	
	
	def run_next(self):
		value, value_hex = self.send_command([0xFF,0x00,0x00,0x00,0x03,0xD4,0x42,0x43])
		print(value_hex)
		value, value_hex = self.send_command([0xFF,0x00,0x00,0x00,0x08,0xD4,0x08,0x63,0x02,0x80,0x63,0x03,0x80])
		print(value_hex)
		value, value_hex = self.send_command([0xFF,0x00,0x00,0x00,0x05,0xD4,0x40,0x01,0x30,0x00])
		print(value_hex)
        
	def run_read(self):
		reader.get_card_status()
		value, value_hex = self.send_command([0xFF, 0x88, 0x00, 0x00, 0x60, 0x00]) #Auth block 0x00 [0xFF, 0x88, 0x00, block_number, 0x60, key]
		print(value_hex)
		if(value_hex == "90 00"):
			value, value_hex = self.send_command([0xFF,0xB0,0x00,0x00,0x10]) #Read 16 block 0x00 [0xFF,0xB0,0x00,block_number,0x10]
			with open('data.dump', 'wb') as fp:
    				pickle.dump(value[:-2], fp)
			print(value_hex)
			print("\n")
			print("Pembacaan kartu berhasil ! \nSelanjutnya letakan kartu ke dua untuk duplikasi \nKemudian akses python nf.py duplikat")
			print("\n")
		else:
			print("Proses pembacaan kartu gagal")	
        
	def run_write(self):
		try:
			with open ('data.dump', 'rb') as fp:
					dumptmp = pickle.load(fp)
		except:
			print("Terjadi masalah membaca file kartu")
			quit()

		value, value_hex = self.send_command([0xFF,0x00,0x00,0x00,0x03,0xD4,0x42,0x43])
		print(value_hex)
		value, value_hex = self.send_command([0xFF,0x00,0x00,0x00,0x08,0xD4,0x08,0x63,0x02,0x80,0x63,0x03,0x80])
		print(value_hex)
		command_write = [0xFF,0x00,0x00,0x00,0x15,0xD4,0x40,0x01,0xA0,0x00]
		command_write.extend(dumptmp)
		value, value_hex = self.send_command(command_write)
		print(value_hex)
  		print("\n")
		print("Duplikasi kartu berhasil")
		print("\n")
	        
	def send_command(self, command):
		print("<< "+toHexString(command))
		for iteration in range(1):
			try:
				self.hresult, self.response = SCardTransmit(self.hcard,self.dwActiveProtocol,command)
				value = toHexString(self.response, format=0)
			except SystemError:
				print ("Kartu tidak terdeteksi")
			#time.sleep(1)
		##print("\n")
		return self.response, value


if __name__ == '__main__':
    
    if(len(sys.argv)<2):
        print("\n-------* RFID CLONE *\n")
        print("Letakan kartu pertama, kemudian akses python nf.py baca")
        print("\n------------------------------\n")
        quit()
    else:
        cmd = sys.argv[1]
        
    if(cmd == "baca"):
        reader = NFC_Reader()
        reader.run_read()
        quit()
        
    if(cmd == "duplikat"):
        reader = NFC_Reader()
        reader.run()
        quit()




