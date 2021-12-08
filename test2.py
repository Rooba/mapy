# a = [(z, i,) for z in [(a := 2), (2, 4,), (1, 2,), (3, 4,)] for i in ([1,2,3,4,5,6])]
a, b = 0, 0
for z, y in [
    (d := (a := 2 ** i - 1), ((b := a + (2 * i) & b) % 250)) for i in range(1, 20)
]:
    while z > (c := b // 4):
        z = (b := z ** 2 - 1) >> 0xFF & (y := a ^ b)
        print(z, c, b, y, a)
