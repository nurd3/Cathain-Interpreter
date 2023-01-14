import re
import debug
import prefs

print("Welcome to the Cathain Interpreter!")
print("... means a timeline reached the jump limit (default: 1000)")
print("!!! means a timeline encountered an illegal action,\n    such as trying to jump to a non-existent label")
print("--- denotes the end of a timeline\n")


# gives us a string of the binary value of a given number
# this also will enforce a size:
    # strings that are too small will have the appropriate amount of 0s before them
    # strings that are too big will be cut off
def bitstr(n, size):
    a = (" " * size) + f'{n:0b}'         # get the binary add spaces (spaces are placeholders)
    a = a[::-1]                          # reverse the string
    a = a[:size]                         # cut off any overflow
    a = a.replace(" ", "0") [::-1]       # replace any remaining spaces with 0s
    return a

def to_str(hex):
    last_char = ""
    ret = ""
    for i in hex:
        if last_char == "":
            last_char += i
        else:
            x = last_char + i
            try:
                y = int(x, base=16)
                ret += chr(y)
            except: pass
            last_char = ""
    try: int(last_char, base=16)
    except: last_char = ""
    return [ret, last_char]

def timeline(tkns, num, label):
    L = bitstr(num, len(tkns))
    i = 0
    ret = []
    x = "ff"
    jmps = 0
    try:
        jmp_limit = prefs.jump_limit
    except:
        jmp_limit = 1000
    while i < len(tkns):
        t = tkns[i]
        debug.log(L[i], t)
        if jmps > jmp_limit:
            ret.append("...")
            break
        # goto
        if t[0] == "GOTO":
            if L[i] == "1":
                if t[1] in label:
                    p = label[t[1]]
                    if L[p] == "1": i = p
                    else: i = -1
                    jmps += 1
                else: i = -1
        
        elif t[0] == "SWAP":
            if L[i] == "1": x = x.replace(t[1], t[2])
            ret.append(x)
        
        # end timelines that do something illegal
        if i < 0:
            ret.append("!!!")
            break
        i += 1
    debug.log("=== {0}".format(ret))
    return ret

def run_ctn(script):
    script = re.sub("#~.*?~#", '', script)
    script = re.sub("( |\n)+", "\n", script)
    script = script.split("\n")
    label = {}
    x = 0
    y = []
    global err
    err = 0
    while x < len(script):
        i = script[x]
        if i.startswith("!"):
            if i in label:
                debug.error("label declared twice: '{0}'".format(i))
                err += 1
            label[i[1:]] = x
            y.append(["LABEL"])
        elif i.startswith("@"):
            y.append(["GOTO", i[1:]])
        else:
            try:
                g = [re.sub("([0-9]|[a-f])", "", script[x].lower()), re.sub("([0-9]|[a-f])", "", script[x + 1].lower())]
                if g != ["", ""]:
                    err += 1
                    if g[0] != "": debug.error("unexpected '{0}'".format(g[0]))
                    if g[1] != "": debug.error("unexpected '{0}{1}'".format(g[1]))
                y.append(["SWAP", script[x], script[x + 1]])
                x += 1
            except: pass
        x += 1
    if err > 0:
        return {"err": err}
    debug.log(label)
    n = 0
    ret = []
    while n < 2 ** len(y):
        ret.append(timeline(y, n, label))
        n += 1

    return {
        "timelines": ret,
        "count": len(y)
    }

debug.off("log")
try:
    if prefs.debug_log:
        debug.on("log")
except: pass
def run():
    with open("main.ctn", "r") as f:
        n = 0
        c = run_ctn(f.read())
        if "err" in c: 
            plural = ""
            if c["err"] != 1: plural = "s"
            print("PROGRAM FAILED: {0} ERROR{1}".format(c["err"], plural))
            return
        l = c["count"]
        for i in c["timelines"]:
            N = f'  {n:0b}'[::-1]
            N = N[:l].replace(" ", "0")[::-1]
            print("timeline", n, "({0})".format(N))
            nn = 0
            g = len(str(len(c["timelines"][n])))
            for ii in c["timelines"][n]:
                NN = str(nn)
                print(
                    "  " + (" " * (g - len(NN))) + NN + " ", 
                    ii.upper()
                )
                nn += 1
            print("     ---")
            try: 
                x = to_str(c["timelines"][n][-1])
                if prefs.show_result: print(
                    (" " * (g - len(NN))) + "       hex:", "0x" + c["timelines"][n][-1].upper(),
                    (" " * (g - len(NN))) + "\n    string:", repr(x[0])
                )
            except: pass
            n += 1
    return
run()
