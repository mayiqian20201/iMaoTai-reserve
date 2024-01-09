import datetime
import logging
import sys

import config
import login
import process
import privateCrypt

DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
                    stream=sys.stdout,
                    datefmt=DATE_FORMAT)


def run():
    TODAY = datetime.date.today().strftime("%Y%m%d")

    print(r'''
    **************************************
        欢迎使用i茅台自动预约工具
	        作者GitHub：https://github.com/3 9 7 1 7 9 4 5 9
	        vx：L 3 9 7 1 7 9 4 5 9 加好友注明来意
    **************************************
    ''')

    process.get_current_session_id()

    # 校验配置文件是否存在
    configs = login.config
    if len(configs.sections()) == 0:
        logging.error("配置文件未找到配置")
        sys.exit(1)

    aes_key = privateCrypt.get_aes_key()

    s_title = '茅台预约成功'
    s_content = ""
    for section in configs.sections():
        if (configs.get(section, 'enddate') != 9) and (TODAY > configs.get(section, 'enddate')):
            continue
        mobile = privateCrypt.decrypt_aes_ecb(section, aes_key)
        token = configs.get(section, 'token')
        userId = privateCrypt.decrypt_aes_ecb(configs.get(section, 'userid'), aes_key)
        lat = configs.get(section, 'lat')
        lng = configs.get(section, 'lng')

        process.UserId = userId
        process.TOKEN = token
        process.init_headers(user_id=userId, token=token, lng=lng, lat=lat)
        # 根据配置中，要预约的商品ID，城市 进行自动预约
        try:
            msg = process.get_result(mobile)
            s_content += (msg + "\n")
        except BaseException as e:
            print(e)
            logging.error(e)

    # 推送消息
    if '申购失败' in s_content:
        title="申购失败通知:"
    elif '申购中' in s_content:
        title="申购未结束:"
    else:
        title = "申购成功通知:"
    process.send_msg(title, s_content)


if __name__ == '__main__':
    run()
