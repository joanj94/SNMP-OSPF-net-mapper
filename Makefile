all:
	python script.py -t 10.0.0.1 -c PASSWORD -pi -pg graf
	
basic:
	python script.py -t 10.0.0.1 -c PASSWORD

routes:
	python script.py -t 10.0.0.1 -c PASSWORD -pi

graf:
	python script.py -t 10.0.0.1 -c PASSWORD -pg graf


