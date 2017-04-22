import os
import sys
import http.client

host = "http://localhost:5000"
requests = [
    {"method": "GET", "route": ""},
    {"method": "GET", "route": "/search/ban%20rahul"},
    {"method": "GET", "route": "/watch/-0ziqk9cZRM"},
    {"method": "GET", "route": "/channel/UCc052CoYw9cF27quifoL_mg"},
    {"method": "GET", "route": "/login"},
    {"method": "GET", "route": "/signup"},
    {"method": "GET", "route": "/recently-watched"},
    # {"method": "GET", "route": "/logout/"},
    {"method": "GET", "route": "/frhfri"}
]


def main():
    max_route_len = max([(len(x["route"]) + 1) for x in requests])
    header_line = " {0: <7} | {1: <{width}} | Response".format(
        "Method", "URL", width=max_route_len
    )
    border_line = pattern_line("-", "+", [9, max_route_len + 2, 25])
    separater_line = pattern_line(" ", "|", [9, max_route_len + 2, 25])
    print(border_line)
    print(header_line)
    print(border_line)
    sys.stdout.flush()
    for x in requests:
        print(separater_line)
        test_route(x, max_route_len)
        x["route"] = x["route"] + "/"
        test_route(x, max_route_len)
        sys.stdout.flush()
    print(separater_line)
    print(border_line)


def test_route(r, max_route_len):
    cmd_prefix = 'curl -s -o /dev/null -I -w \"%{http_code}" -X'
    cmd = cmd_prefix + r["method"] + ' ' + host + r["route"]
    print(
        " {0: <7} | {1: <{width}} | ".format(
            r["method"],
            r["route"],
            width=max_route_len
        ), end=""
    )
    sys.stdout.flush()
    res = os.popen(cmd).read()
    print(res, ":", http.client.responses[int(res)])
    sys.stdout.flush()



def pattern_line(s1, s2, counts):
    s = ""
    for x in counts:
        s = s + s1 * x + s2
    return s[:-1]


if __name__ == "__main__":
    main()
