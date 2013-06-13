#
# sip calc_yield
#
# calculate yield for sip nodes
#


# at the moment, the sequence numbers wrap at 256,
# therefore the following equations show what we have to
# do

# c = sequence count (packets received) [0,inf)
# d = maxseq - minseq + 1 [-254,256] 
# m = missed packets [0,inf)
# n = wrap arounds [0,inf)

# c + m = d + n * 256 
# => (c + m - d)/256=n
# => n = ceil((c-d)/256) if m<256
# m = d + n * 256 - c
# yield = c / (c + m)
#       = c / (d + n * 256)

def calc_yield(seqcnt, minseq, maxseq, wrap=256):
    """ derive yield from count of received packets, earliest sequence
    number and latest sequence number that wrap around.
    """
    
    d = maxseq - minseq + 1
    n = math.ceil((seqcnt - d) / 256.)
    
    return (seqcnt * 100.) / (d + n * 256)
