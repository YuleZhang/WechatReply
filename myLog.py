# encoding:utf-8  
import sys  
import logging  
import time  
import datetime
   
def writeLog(message):
    logger = logging.getLogger()
    # streamhandler = logging.StreamHandler()
    filename = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    handler = logging.FileHandler("./log/" + filename + ".log")

    #添加StreamHandler在控制台也打印出来
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('LINE %(lineno)-4d : %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    logging.info(message)



    logger.addHandler(handler)
    logger.setLevel(logging.INFO )
    logger.info(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+':'+message)
    
    #  添加下面一句，在记录日志之后移除句柄
    logger.removeHandler(handler)
   
if __name__ == '__main__':  
   
    writeLog("hello")  
