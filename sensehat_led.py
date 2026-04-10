from sense_hat import SenseHat
import time

def main():
    sense = SenseHat()

    r = (255,  0,  0)
    g = (  0,255,  0)
    bl = (  0,  0,255)
    w = (255,255,255)   
    b = (0  ,  0,  0)   

    pixels1 = [
      w,w,w,w,w,w,w,w,
      w,w,w,w,w,w,w,w,
      w,w,w,w,w,w,w,w,
      w,w,w,w,w,w,w,w,
      w,w,w,w,w,w,w,w,
      w,w,w,w,w,w,w,w,
      w,w,w,w,w,w,w,w,
      w,w,w,w,w,w,w,w
    ]
    pixels2 = [
      b,b,b,b,b,b,b,b,
      b,w,w,w,w,w,w,b,
      b,w,w,w,w,w,w,b,
      b,w,w,w,w,w,w,b,
      b,w,w,w,w,w,w,b,
      b,w,w,w,w,w,w,b,
      b,w,w,w,w,w,w,b,
      b,b,b,b,b,b,b,b
    ]
    pixels3 = [
      b,b,b,b,b,b,b,b,
      b,b,b,b,b,b,b,b,
      b,b,w,w,w,w,b,b,
      b,b,w,w,w,w,b,b,
      b,b,w,w,w,w,b,b,
      b,b,w,w,w,w,b,b,
      b,b,b,b,b,b,b,b,
      b,b,b,b,b,b,b,b
    ]
    pixels4 = [
      b,b,b,b,b,b,b,b,
      b,b,b,b,b,b,b,b,
      b,b,b,b,b,b,b,b,
      b,b,b,w,w,b,b,b,
      b,b,b,w,w,b,b,b,
      b,b,b,b,b,b,b,b,
      b,b,b,b,b,b,b,b,
      b,b,b,b,b,b,b,b
    ]    
    while(1):
	    sense.set_pixels(pixels1)
	    time.sleep(1)
	    sense.set_pixels(pixels2)
	    time.sleep(1)
	    sense.set_pixels(pixels3)
	    time.sleep(1)
	    sense.set_pixels(pixels4)
	    time.sleep(1)
	    sense.set_pixels(pixels3)
	    time.sleep(1)
	    sense.set_pixels(pixels2)
	    time.sleep(1)




if __name__ == "__main__":
    main()
