import json
import sys

from websocket import create_connection

# read command line argument as one string

input = sys.argv[1]

# if no input is given use test data

if input == "":
    # small base64 png
    png_image = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAEaUlEQVR4nLzW/zfVdxwHcHTrmlLSnaiDIpeSLyfh0pBhmdVGjKiVpTOFMTKmTPlSZ8zUGdnpmJrGwjVfOkpdZSvdSunWktS2LEe+JLpMotq1PZ9/xD5+eLw/5/P5XOf9+rxfr/frLZIEv6ulpeVeHAvFazrhjRc3YUreELx9bxfMHLoLq2duhgMXf4aDHb7waOoH8NrCVP5KLw+miZphq8+X0K/pBNTR+p//RLEBFRjOyJbC719dhIaX/4DDQc+g4rQtzNoWyevXO+EelyioLvXj7MrmctZj92CnrpjxNbbAk9VXYKiliSARWGf2YlhuHgHX9zbCpE+soFXtAxgU/RE8uGgvvJ84D+bKuRLN01VQJd4C1ypnwrI2T+hjyvv6W+9AZztPISLQ/iqiH8P+EnO4omocKjU/QvlKrkdgRg6j8dOGq+9sgudPcSWKRe7wsQ2//ik9J/jbh1xFvV1X4XhbPsx2mBQkggGLEAxGWkugWf807Jhmdv+9sA6qfB/CDQYp8MyMdOh85RaMOBIDV716zvfd5sAflq3m08TzML9uGdxxVkeQCDY918WguJALZZmvoTy3EO7xSoKupTv4tHYNNE124bXtt9DfeQF1ZM1ne38G35/IgBI33o/qLoOxhS5CRCASvzTC0Cdl1me5VEJNPLP72FAtlBrw6ebMKWjYy/s1OgVwo4LfOq78Eox255ol1LFWPBWH4YNBJQywNxYiAu2KwC8wVPzKnS+vsQYesGNeu8UzZwLKuS8t1f0GnouLhMMW7VBXxl+Nx7BWig+9A2s9vPj+3njYuYJvKkMEWQPtgYxBDI+3J8Lky6ZQpgiG+0aYG2qnrbxOYN16G5hxRqHhMNo2AXoVcAfzMmf0CjUzRxL2E50KhXe9pYJEMGMLs2LCqRrmiDmv8nlFnLUxd1adp/P50gtv+GSWAkaJmF3JcQfhiZAsWOnPWI3m90G73T2wsdoVHjZsESSCpFjmfs1UCWxP5+ym4jjrFKevoZeqCzpHsJJl+azzdf+0wRYTC9gVwJoftdSHc/XfgqmjXMuoykVQU3RDkAjELczcyHB2orSixfDRQ2aCfw5PEiH77KH0yBK+UyKDamPOqW4V96jmEfa+BfIRqN++HgZNNkBP9QXY94ahEBGIHHpYb8d3s/cOqTSw8NYsaBPIvT4wuBxONKyEVmu5w9T4ukGNkhWzQc4d6dnbPCkt9v+dH8SKNXHTzgZWf3pAkAhul17DMLCcO9+6+kDY9F0Y3GnNjhZmwlzOCmO36L/PDtyq/yc828Eu7XqV5x+PsWzGd511e3ySFaOQOED5aLggERh7PsHg2MZ8UFexu43K2bNC6tNgfSs7wbmCjdD+L+a19BAzPaaKM93usQ1esucJLruJndlsdjL/z8c8YVzXPBUiAu39Y8z3bEeeFQZ9uAbHJrthQ+Hn8M1udquTPS/h7NPcOyVlj6Dde9wv5xzlmUoiHYaWv/C02vUv6z9MxbN6lnW6EBH8FwAA//8BaHZMV0wTLwAAAABJRU5ErkJggg=="
    # add png header
    png_image = "data:image/png;base64," + png_image

    input = { "image": png_image }
    
    # convert to json string
    input = json.dumps(input)

# create websocket connection

ws = create_connection("ws://localhost:8000/ws")

# send input to server

ws.send(input)

result = None

while True:
    # receive result from server
    result = ws.recv()

    # if result is empty break loop
    if result == "":
        break

    # print result

    print("result", result)


# print result

ws.close()
