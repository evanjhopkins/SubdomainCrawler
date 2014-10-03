#Evan Hopkins 9/20/13

import sys
import subprocess
import os
import time

verbose = False
subnets = ['10.10.1', '10.10.6', '10.13.8', '148.100.100', '148.100.49']

def cla(input):
	global subnets
	id = input[:2]
	if id == "-d":
		subnets = [input[2:]]
	if id == "-v": 	
		verbose = True
		print '*Verbose mode on'
	if id == '-h':
		print '   HELP:'
		print '     -dxx.xx.xx -> Specify a single subnet to test'
		print "     -v -> Doesn't delete any of the temp files from working directory"
		print "     -h -> Help mode"
		sys.exit()
		
def main():
	for args in sys.argv:
		cla(args)
	create = open('found.txt', 'w+')
	create = open('not_found.txt', 'w+')
	create.close()
	for curr in subnets:
		getData(curr)
		time.sleep(5)
	pingCheck()
	if not verbose: clean()
	print 'Completed!'
	
def getData(subnet):
	#building command statements
	command_nots = 'for f in {1..255}; do host ' + subnet + '.$f; done | grep "not found" > notsTMP' 
	command_found = 'for f in {1..255}; do host ' + subnet + '.$f; done | grep "pointer" > foundTMP'
	
	#runs commands in terminal
	print 'Working on '+subnet+' subnet...'
	os.system(command_nots)
	os.system(command_found)
	
	print 'Writing to csv...'
	parseFounds(subnet)
	parseNots(subnet)
	
def parseFounds(subnet):
	writer = open('found.txt', 'a')
	read = open('foundTMP')
	for lyne in read :
		beginCut = getIndex(lyne, 'i')-1
		endCut = getIndex(lyne, 't')+3
		ip = lyne[:beginCut]
		ip = fixIP(ip, subnet)#reveses ip so it's in correct order
		adr = lyne[endCut:]
		writer.write(ip+', '+adr)
	read.close()
	writer.close()
		
def parseNots(subnet):
	writer = open('not_found.txt', 'a')
	read = open('notsTMP')
	for lyne in read :
		beginCut = getIndex(lyne, 't')+2
		endCut = getIndex(lyne, 'i')-1
		ip = lyne[beginCut:endCut]
		ip = fixIP(ip, subnet)
		writer.write(ip+'\n')
	writer.close()
	read.close()
		
def pingCheck():
	prcnt = 0
	ln = []
	cnt = 0
	print 'Pinging failed IPs (can take a while)...'
	writer = open('pingableTMP', 'w+')
	read = open('not_found.txt')
	final = open('pingables.txt', 'w+')
	for lyne in read:
		command = 'ping -c1 -w1 '+ lyne[:-1] +' | grep received >> pingableTMP'
		os.system(command)
		if (cnt%53)==0:
			print str(cnt) + " IP's done so far"
		cnt = cnt + 1
	cnt = 0;		
	read.close()
	for lyne in writer:
		responded = lyne[23]
		ln.append(responded)
	read = open('not_found.txt')
	for lyne in read:
		if ln[cnt] == '1':
			final.write(lyne[:-1] + '\n')
		cnt = cnt + 1
	writer.close()
	final.close()
	cnt = 0;

def getIndex(lyne, char):
	cnt=0
	for c in lyne:
		if (c==char):
			return cnt
		cnt = cnt+1
	print 'DEBUG-> getIndex method could not find * '+char+' *'
			
def fixIP(ip, subnet):
	period = getIndex(ip, '.')
	section = ip[:period]
	return subnet+'.'+section
	
	
def clean():
	print 'Cleaning up files...'
	os.system('rm foundTMP')
	os.system('rm notsTMP')
	os.system('rm pingableTMP')
	os.system('mv found.txt found.csv')
	os.system('mv pingables.txt not_found.csv')
	os.system('rm not_found.txt')

	
if __name__=='__main__':
	main()
