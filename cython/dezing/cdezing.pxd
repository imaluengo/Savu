
cdef extern from "./options.h":
   ctypedef struct Options:
      unsigned char versionflag
      unsigned char f_call_num
      size_t cropwd
      unsigned int nlines
      float outlier_mu
      unsigned char returnflag
      unsigned int npad

cdef extern from "./timestamp.h":
   void timestamp_open(const char * const logname)
   void timestamp_close()
   void timestamp_init()
   void timestamp(const char * const stampmsg)

cdef extern from "./dezing_functions.h":
   void runDezing(Options * ctrlp, unsigned int  thisbatch,unsigned char * inbuf, unsigned char * outbuf )

