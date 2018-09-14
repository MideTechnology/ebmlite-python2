'''
Created on Aug 14, 2017

@author: dstokes
'''
import unittest
import core
import os, sys
import numpy as np
from datetime import datetime, timedelta

from decoding import *
from encoding import *
from mock     import *
from numpy    import inf
from util     import *

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass
class testDecoding(unittest.TestCase):
    
    def setUp(self):
        
        class mockStream(object):
            
            def __init__(self):
                self.string = ''
            
            def read(self, n=None):
                if n is None:
                    n = len(self.string)
                retVal = self.string[:n]
                self.string = self.string[n:]
                return retVal
        
        self.mockStream = mockStream()
        
    
    def testDecodeIntLen(self):
        # Test getting the number of bytes in an element's size from the first
        # byte of the size
        
        for i in range(1, 255):
            self.assertEqual(decodeIntLength(i), \
                             (np.ceil(8 - np.log2(i)), i - 2**np.floor(np.log2(i)) ))
            
            
    
    def testIDLen(self):
        # Test getting the number of bytes in an ID from the first byte of the ID
        
        for i in range(16, 255):
            self.assertEqual((np.ceil(8-np.log2(i)), i), decodeIDLength(i))


    
    def testReadElID(self):
        # Test reading the ID of an element
        
        idBytes = ['\x80', \
                   '\x40\x41', \
                   '\x20\x41\x42', \
                   '\x10\x41\x42\x43']
        eIDs = [128, 16449, 2113858, 272712259]
                           
        for id, i, eID in zip(idBytes, range(1, len(idBytes) + 1), eIDs):
            self.mockStream.string = id
            readElIDOut = readElementID(self.mockStream)
            self.assertEqual(readElIDOut, (eID, i))


    
    def testReadElSize(self):
        # Test reading the size of an element
        
        idBytes = ['\x85', \
                   '\x45\x41', \
                   '\x25\x41\x42', \
                   '\x15\x41\x42\x43', \
                   '\x08\x41\x42\x43\x44', \
                   '\x04\x41\x42\x43\x44\x45', \
                   '\x02\x41\x42\x43\x44\x45\x46', \
                   '\x01\x41\x42\x43\x44\x45\x46\x47']
        elSizes = [0x5, \
                   0x541, \
                   0x54142, \
                   0x5414243, \
                   0x41424344, \
                   0x4142434445, \
                   0x414243444546, \
                   0x41424344454647]
        
        for id, i, elSz in zip(idBytes, range(1, len(idBytes) + 1), elSizes):
            self.mockStream.string = id
            self.assertEqual(readElementSize(self.mockStream), (elSz, i))
       

    
    def testReadUInt(self):
        # Test reading unsigned integers
        
        idBytes = ['\x85', \
                   '\x45\x41', \
                   '\x25\x41\x42', \
                   '\x15\x41\x42\x43']
        ints = [0x85, 0x4541, 0x254142, 0x15414243]
        
        for id, i, numOut in zip(idBytes, range(1, len(idBytes) + 1), ints):
            self.mockStream.string = id
            a = readUInt(self.mockStream, i)
            self.assertEquals(a, numOut)
       

    
    def testReadInt(self):
        # Test reading signed integers
        
        # Positive ints
        idBytes = ['\x75', \
                   '\x45\x41', \
                   '\x25\x41\x42', \
                   '\x15\x41\x42\x43']
        ints = [0x75, 0x4541, 0x254142, 0x15414243]
        
        for id, i, numOut in zip(idBytes, range(1, len(idBytes) + 1), ints):
            self.mockStream.string = id
            a = readInt(self.mockStream, i)
            self.assertEquals(a, numOut)
            
        # Negative ints
        idBytes = ['\xf5', \
                   '\xc5\x41', \
                   '\xb5\x41\x42', \
                   '\xa5\x41\x42\x43']
        ints = [-1*(0xff ^ 0xf5) - 1, \
                -1*(0xffff ^ 0xc541) - 1, \
                -1*(0xffffff ^ 0xb54142) - 1, \
                -1*(0xffffffff ^ 0xa5414243) - 1]
        
        for id, i, numOut in zip(idBytes, range(1, len(idBytes) + 1), ints):
            self.mockStream.string = id
            a = readInt(self.mockStream, i)
            self.assertEquals(a, numOut)
            
        
            
    def testReadFloat(self):
        # Test reading floating point numbers
        
        # 0 length
        self.mockStream.string = ''
        self.assertEqual(readFloat(self.mockStream, 0), 0.0)
        
        # 4-bit length
        self.mockStream.string = '\x00\x00\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 4), 0.0)
        
        self.mockStream.string = '\x3f\x80\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 4), 1.0)
        
        self.mockStream.string = '\xc0\x00\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 4), -2.0)
        
        self.mockStream.string = '\x3e\xaa\xaa\xab'
        self.assertEqual(np.float32(readFloat(self.mockStream, 4)), np.float32(1.0/3.0))
    
        # 8-bit length
        self.mockStream.string = '\x00\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 8), 0.0)
        
        self.mockStream.string = '\x3f\xf0\x00\x00\x00\x00\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 8), 1.0)
        
        self.mockStream.string = '\xc0\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 8), -2.0)
        
        self.mockStream.string = '\x3f\xd5\x55\x55\x55\x55\x55\x55'
        self.assertEqual(readFloat(self.mockStream, 8), 1.0/3.0)
    
    
    
    def testReadString(self):
        # Test reading strings
        
        self.mockStream.string = ''
        self.assertEqual(readString(self.mockStream, 0), '')
        
        self.mockStream.string = 'test'
        self.assertEqual(readString(self.mockStream, len(self.mockStream.string)), \
                         'test')
            
    
    
    def testReadUnicode(self):
        # Test reading unicode strings
        
        self.mockStream.string = u''
        self.assertEqual(readUnicode(self.mockStream, 0), u'')
        
        self.mockStream.string = 'TEST'
        self.assertEqual(readUnicode(self.mockStream, len(self.mockStream.string)), \
                         u'TEST')
    
    
    
    def testReadDate(self):
        # Test reading dates from bytes
        
        self.mockStream.string = '\x00\x00\x00\x00ABCD'
        a = readDate(self.mockStream)
        self.assertEqual(a, datetime.datetime(2001, 1, 1, tzinfo=None) + \
                            timedelta(microseconds=0x41424344//1000))
        
    
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()