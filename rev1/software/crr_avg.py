import json
class CRR_AVG:
    """ Cascadable running/retained average class """
    buf = None      # circular buffer of samples to average
    buf_i = 0       # current buffer index
    buf_n = None    # buffer size (number of samples to average)
    cas = None      # (optional) cascade counter object
    jfile = None    # (optional) JSON file name
    avg = None      # running average

    def __init__(self, buf_n, cas = None, jfile = None):
        """ Constructor """
        self.buf_n = buf_n
        self.cas = cas
        self.jfile = jfile
        self.reset()
        if jfile != None:
            try:
                with open("%s.json" % self.jfile) as fd:
                    self.buf_i, self.buf = json.load(fd)
                #print("loaded %f values from %s" % (len(self.buf), self.jfile))
            except:
                pass
    
    def y(self, val):
        """ Add a sample to the circular buffer and return the running average """
        if len(self.buf) < self.buf_n:
            self.buf.append(val)
        else:
            self.buf[self.buf_i] = val
        self.buf_i += 1
        self.avg = sum(self.buf) / len(self.buf)
        if self.buf_i == self.buf_n:
            self.buf_i = self.buf_i % self.buf_n            
            if self.cas != None:  
                self.cas.y(self.avg)
            self.dump()            
        return self.avg
    
    def dump(self):
        """ If a filename was provided serialize to a JSON file """
        if self.jfile != None:      
            with open("%s.json" % self.jfile, 'w') as fd:
                json.dump([self.buf_i, self.buf], fd)        
        if self.cas != None: 
            self.cas.dump()

    def set(self, i, buf):
        """ Initialize with previously saved values """
        self.buf = buf
        self.buf_i = i
        self.avg = None if len(buf) == 0 else (sum(buf) / len(buf))

    def reset(self):
        """ Reset the object """
        self.set(0, [])

if __name__ == "__main__":

    import random

    """
    Calculate a 24 hour average at 1 sample per second (60*60*24 = 86400 values)
    using a reasonable number of variables (60+60+24 = 144 values).  
    """
    ravg_24h = CRR_AVG(24, jfile = "day")       # daily average bin (retained)
    ravg_60m = CRR_AVG(60, ravg_24h)            # hourly average bin
    ravg_60s = CRR_AVG(60, ravg_60m)            # minutely average bin

    for j in range(86400):
        x = random.randrange(1,100)
        ravg_60s.y(x)
    print("  24 hour average:", ravg_24h.avg)
    print("60 minute average:", ravg_60m.avg)
    print("60 second average:", ravg_60s.avg)