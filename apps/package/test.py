dic1 = {
    "a":1,
    "d":4,
    "b":2,
    "c":3,
}

l = zip(dic1.keys(), dic1.values())
ll = sorted(l)
print(dict(ll))


print(dic1)