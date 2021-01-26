from curio.debug import schedtrace, logcrash, longblock

def _configure_debuggers(filter_=None, max_time=0.1):
    return [schedtrace(filter=filter_), logcrash, longblock(max_time=float(max_time))]
