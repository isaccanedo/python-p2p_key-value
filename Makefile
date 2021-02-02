servent:
	python servent.py mtd_servent.py 51515 services 127.0.0.1:51516
s1:
	python servent.py mtd_servent.py 51516 services 127.0.0.1:51517
s2:
	python servent.py mtd_servent.py 51517 services 127.0.0.1:51518
s3:
	python servent.py mtd_servent.py 51518 services 127.0.0.1:51519
s4:
	python servent.py mtd_servent.py 51519 services 127.0.0.1:51515
s5:
	python servent.py mtd_servent.py 51520 services 127.0.0.1:51515