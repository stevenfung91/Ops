import subprocess
import datetime

IP_LIST = {
    'T2': '',
    'T3': '18.182.88.173',
    'T5': '',
    'T6': '52.68.233.242',
}

# Download Daily Report From T3
ACCOUNT_MAIN = "/home/operations/account/"
LOCAL_MAIN = "D:/OneDrive - Huobi Global Limited/LiquidityTeam/Finance/Reports"

T3_REPORTS = ['all_exchange', 'price', 'asset_raw', 'asset_combine_uid']
T6_REPORTS = ['operation']


def get_report(server, report):
    datetimestr = datetime.datetime.now().strftime('%Y-%m-%d')
    PARAMS = "%s_%s" % (report, datetimestr)
    remote_path = ACCOUNT_MAIN + PARAMS + "*"
    local_path = '"%s/%s/"' % (LOCAL_MAIN, report)

    # print(remote_path)
    # print(local_path)
    cmd = "scp strategy_dev@%s:%s %s" % (IP_LIST[server], remote_path, local_path)
    # print(cmd)

    # Check file exist
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    print("execute SCP_CMD status: ", output)


def run_all():
    # Run T3
    for report in T3_REPORTS:
        get_report('T3', report)
    # Run T6
    for report in T6_REPORTS:
        get_report('T6', report)


if __name__ == "__main__":
    run_all()

