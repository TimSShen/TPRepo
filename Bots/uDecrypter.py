import os
def uDecrypter(codedNum, pk):
    '''Decrypts unicode decimal converted six digit number string with a private key. Expects that a six digit number is first
    converted to unicode decimals (two digit pairs) that are then concatenated together. The final number is then multiplied by a private key.
    This function retrieves the private key and divides the final number again, then uses a unicode dictionary for number digits to reverse the unicode digit pairs.'''
    uDict = {48:0, 49:1, 50:2, 51:3, 52:4, 53:5, 54:6, 55:7,56:8, 57:9}
    key = pk
    count = 1
    str_pair = ''
    dString = ''

    #Reverse private key encryption
    decrypt = str(int(int(codedNum)/int(key)))
    
    for char in decrypt:
        str_pair = str_pair + char
        if count%2 == 0:
            dString = dString + str(uDict[int(str_pair)])
            str_pair = '' 
        # print(dString)
        count+=1

    print (f'Decrypt success: {dString}')
    return dString

# uDecrypter(1366952162178808,os.environ.get('PKEY'))