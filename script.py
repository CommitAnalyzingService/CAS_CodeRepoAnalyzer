from analyzer.analyzer import *
from ingester.ingester import *

#import Queue

thread2 = Ingester(sys.argv)
thread2.start()
thread2.join()

thread1 = Analyzer(sys.argv)
thread1.start()
thread1.join()

print("Fin!")