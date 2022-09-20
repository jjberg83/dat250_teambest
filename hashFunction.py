# https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/


import rsa
 
def encrypt(myStr):
	# generate public and private keys with
	# rsa.newkeys method,this method accepts
	# key length as its parameter
	# key length should be atleast 16
	publicKey, privateKey = rsa.newkeys(512)
 
	 
	# rsa.encrypt method is used to encrypt
	# string with public key string should be
	# encode to byte string before encryption
	# with encode method
	encMessage = rsa.encrypt(myStr.encode(),
	                         publicKey)
	 
	 
	 
	
	return encMessage, privateKey

def decrypt(encMessage, privateKey):
	# the encrypted message can be decrypted
	# with ras.decrypt method and private key
	# decrypt method returns encoded byte string,
	# use decode method to convert it to string
	# public key cannot be used for decryption
	decMessage = rsa.decrypt(encMessage, privateKey).decode()
	return decMessage

print("la oss kryptere og dekryptere 'hello geeks'")
firstEncrypt, privateKey = encrypt("hello geeks")
print("hello geeks kryptert blir ", firstEncrypt)
firstDecrypt = decrypt(firstEncrypt, privateKey)
print("dekryptetet vi dette igjen får vi ", firstDecrypt) 
