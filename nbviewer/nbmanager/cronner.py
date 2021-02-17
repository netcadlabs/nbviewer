import datetime
import os
import sys
import time


def main(tenant_id: str, code: str):
    zaman = str(datetime.datetime.now())
    print('started {}'.format(zaman))

    file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '{}.txt'.format(code))

    with open(file, 'a') as outFile:
        outFile.write('{} {} {} started\n'.format(zaman, tenant_id, code))
        time.sleep(2)
        outFile.write('{} {} {} ended\n'.format(zaman, tenant_id, code))


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print('not enough argv')