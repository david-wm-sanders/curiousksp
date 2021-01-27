from curio.debug import schedtrace, logcrash, longblock

def _configure_debuggers(filter_=None, max_time=0.1):
    #TODO: handle string list of Task name filters
    print(f"{filter_=}")
    # return [schedtrace(filter={filter_}), logcrash, longblock(max_time=float(max_time))]
    return [schedtrace, logcrash, longblock(max_time=float(max_time))]
