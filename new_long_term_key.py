import secrets
import mk85c

k = bytearray(mk85c.KEY_LENGTH)
for i in range(mk85c.KEY_LENGTH):
   k[i] = secrets.randbelow(100)

#k += mk85c.cs(k)
print(mk85c.key_to_str(k))

