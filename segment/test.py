import segment2
import segment3
import segment4
import math
import time


def lcs(a, b):
    lena = len(a)
    lenb = len(b)
    c = [[0] * (lenb + 1)] * (lena + 1)
    for i in range(lena):
        for j in range(lenb):
            if a[i] == b[j]:
                c[i+1][j+1] = c[i][j]+1
            else:
                c[i+1][j+1] = max(c[i+1][j], c[i][j+1])
    return c[lena][lenb]


def test1():
    fout = open("test.html", "w", buffering=1)
    count = 0
    with open("spider3.txt", "r") as test_data:
        while True:
            line = test_data.readline()
            if line == "":
                break
            ans = line.split()
            data = ''.join(ans)

            count += 1
            print('Running on test %d' % count)

            start = time.time()
            try:
                score1 = lcs(ans, segment2.segment_split(data, 1.2))
            except Exception:
                score1 = 0
            end = time.time()
            time1 = end - start

            start = time.time()
            try:
                score2 = lcs(ans, segment2.segment_split(data, 1.1))
            except Exception:
                score2 = 0
            end = time.time()
            time2 = end - start

            start = time.time()
            try:
                score3 = lcs(ans, segment3.segment_split(data))
            except Exception:
                score3 = 0
            end = time.time()
            time3 = end - start

            fout.write("%d %.3f %d %.3f %d %.3f %d\n" %
                       (score1, time1, score2, time2, score3, time3, len(ans)))


def test2():
    count = 0
    with open("spider3.txt", "r") as test_data:
        while True:
            line = test_data.readline()
            if line == "":
                break
            ans = line.split()
            data = ''.join(ans)

            count += 1
            # print('Running on test %d' % count)

            start = time.time()
            try:
                score = lcs(ans, segment4.segment(data))
            except Exception:
                score = 0
            end = time.time()
            cost = end - start
            print(score, "%.3f" % cost, sep='\t')


if __name__ == '__main__':
    test2()