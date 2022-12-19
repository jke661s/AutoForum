import time
from EmailSender import EmailSender
from ForumAutomator import ForumAutomator

tried_time = 0


def lambda_handler(event, context):
    emailSender = EmailSender()

    try:
        automator = ForumAutomator("username", "password", credit_cap=500)
        automator.login()
        automator.get_current_credit()
        if automator.credit < automator.credit_cap:
            automator.vote_threads(10, 1)
            automator.post_upon_credit_limitation()
            time.sleep(25)
            automator.reply_upon_credit_limitation()
            automator.get_current_credit()
            emailSender.send_email("恭喜完成今日任务！",
                                   "总共发帖数量：{} \n 总共回帖数量：{} \n 总共投票数量：10 \n 目前积分：{} \n 感谢使用服务，祝您生活愉快！"
                                   .format(automator.new_thread_number, automator.new_reply_number, automator.credit))
        else:
            emailSender.send_email("积分超过{}！".format(automator.credit_cap),
                                   "目前积分为：{} \n 所以并未发帖/回帖/投票 \n 感谢使用服务，祝您生活愉快！"
                                   .format(automator.credit))
    except Exception as e:
        global tried_time
        if tried_time <= 5:
            tried_time += 1
            lambda_handler("", "")
        else:
            emailSender.send_email("出错并且尝试了五次！", "错误是：{}".format(e))
        # emailSender.send_email("出错！", "错误是：{}".format(e))

# with open("result_page.html", "w", encoding='utf-8') as fp:
#     fp.write(response.text)
