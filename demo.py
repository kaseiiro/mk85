import mk85c


k = '84534 45986 35465 64750 69746 75562 96281 96471 16889 77629 94879 96394 73073 45415 29900 39356 54944 10712 85757 23266 32131 18232'


demo_str = '13097 66526 02468 34895 57830 91323 69784'
print(mk85c.decrypt_letters(demo_str, k))

demo_str = '5166 1825 9887 1340 1940 2688 8582 9395 9141 7652 5105 2564 0394 2727 8949 7965' # Has a typo.
print(mk85c.decrypt_letters(demo_str, k))

demo_str = '5166 1825 9887 1340 1940 2688 8582 9395 9141 7652 5105 2564 0934 2727 8949 7965'
print(mk85c.decrypt_letters(demo_str, k))

demo_str = '7023 8033 0910 4080 7758 5613 5857 0310 7195 3198 8814 6627 9934 3228 8412 3330'
print(mk85c.decrypt_letters(demo_str, k))




demo_str = 'юЙъ$7'
demo_str = mk85c.encrypt_letters(demo_str, k, 5)
print(demo_str)
print(mk85c.decrypt_letters(demo_str, k))