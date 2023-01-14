# I made this so that I don't have to use print functions
# only reason is that it makes it easier to navigate my code using ctrl+f
# it also is useful for disabling logs

__activeFn = {
    "error": True,
    "log": True
}
def on(*fns):
    for fn in fns:
        __activeFn[fn] = True
def off(*fns):
    for fn in fns:
        __activeFn[fn] = False

def error(*msg):
    if __activeFn["error"]: print("Cathain Error: {0}".format(' '.join([str(i) for i in msg])))

def log(*msg):
    if __activeFn["log"]: print(' '.join([str(i) for i in msg]))