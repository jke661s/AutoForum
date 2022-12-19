import time
import requests
from lxml import etree
import re


class ForumAutomator:
    def __init__(self,
                 username,
                 password,
                 root_url="https://resbbs.surpassdata.com/",
                 login_url="https://resbbs.surpassdata.com/member.php",
                 forum_url="https://resbbs.surpassdata.com/forum.php",
                 credit_cap=500):
        self.username = username
        self.password = password
        self.root_url = root_url
        self.login_url = login_url
        self.forum_url = forum_url
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/106.0.0.0 Safari/537.36 "
        }
        self.credit = 0
        self.new_thread_number = 0
        self.new_reply_number = 0
        self.credit_cap = credit_cap

    # Login function
    def login(self):
        # Get cookie, loginhash, formhash and referer
        get_params = {
            "mod": "logging",
            "action": "login"
        }
        response = self.session.get(url=self.login_url, params=get_params, headers=self.headers)
        tree = etree.HTML(response.text)
        login_form = tree.xpath('//div[@id="wp"]//form[@name="login"]')[0]
        login_hash = login_form.xpath('./@id')[0].split("_")[1]
        form_hash = login_form.xpath('.//input[@type="hidden" and @name="formhash"]/@value')[0]
        referer = login_form.xpath('.//input[@type="hidden" and @name="referer"]/@value')[0]

        # Post request to log in
        post_params = {
            "mod": "logging",
            "action": "login",
            "loginsubmit": "yes",
            "loginhash": login_hash,
            "inajax": "1"
        }
        post_data = {
            "formhash": form_hash,
            "referer": referer,
            "loginfield": "username",
            "username": self.username,
            "password": self.password,
            "questionid": "0",
            "answer": ""
        }
        self.session.post(url=self.login_url, params=post_params, headers=self.headers, data=post_data)

    # Post one new voting topic: Return the session response after the post.
    def post_new_thread(self):
        # Get and save the current credit for further usage. As well as the values required for posting the thread.
        get_new_thread_params = {
            "mod": "post",
            "action": "newthread",
            "fid": "37",
            "special": "1"
        }
        response = self.session.get(url=self.forum_url, params=get_new_thread_params, headers=self.headers)
        tree = etree.HTML(response.text)
        # Credit
        self.credit = self.get_credit_int(tree.xpath('//a[@id="extcreditmenu"]/text()')[0])
        # formhash
        form_hash = tree.xpath('//input[@id="formhash"]/@value')[0]
        # posttime
        post_time = tree.xpath('//input[@id="posttime"]/@value')[0]
        # wysiwyg
        wysiwyg = tree.xpath('//input[@id="e_mode"]/@value')[0]
        # special
        special = tree.xpath('//form[@id="postform"]//input[@name="special"]/@value')[0]

        # Post a new thread
        post_new_thread_params = {
            "mod": "post",
            "action": "newthread",
            "fid": "37",
            "extra": "",
            "topicsubmit": "yes"
        }
        post_new_thread_data = {
            "formhash": form_hash,
            "posttime": post_time,
            "wysiwyg": wysiwyg,
            "special": special,
            "subject": "是兄弟就来比积分吧！我积分{}".format(self.credit),
            "polls": "yes",
            "fid": "37",
            "tpolloption": "1",
            "polloption[]": ["比我多", "比我少", "不想说"],
            "polloptions": "",
            "maxchoices": "1",
            "expiration": "",
            "message": "",
            "replycredit_extcredits": "0",
            "replycredit_times": "1",
            "replycredit_membertimes": "1",
            "replycredit_random": "100",
            "allownoticeauthor": "1",
            "usesig": "1",
            "save": ""
        }
        response = self.session.post(url=self.forum_url,
                                     params=post_new_thread_params,
                                     headers=self.headers,
                                     data=post_new_thread_data)
        print("Posted one thread:", response.url)
        return response

    # Post new topics until the credit doesn't grow anymore.
    def post_upon_credit_limitation(self):
        while self.credit < self.credit_cap:
            response = self.post_new_thread()
            self.new_thread_number += 1
            tree = etree.HTML(response.text)

            if self.credit == self.get_credit_int(tree.xpath('//a[@id="extcreditmenu"]/text()')[0]):
                return
            else:
                self.credit = self.get_credit_int(tree.xpath('//a[@id="extcreditmenu"]/text()')[0])
                time.sleep(25)

    # Post a new reply on the first thread in the list.
    def post_new_reply(self):
        # Get forum page and get the current credit
        get_thread_list_params = {
            "mod": "forumdisplay",
            "fid": "37"
        }
        response = self.session.get(url=self.forum_url, params=get_thread_list_params, headers=self.headers)
        tree = etree.HTML(response.text)
        # Credit
        self.credit = self.get_credit_int(tree.xpath('//a[@id="extcreditmenu"]/text()')[0])

        # Go to the first thread
        first_thread_url = self.root_url + tree.xpath('//table[@id="threadlisttableid"]/tbody[contains(@id, '
                                                      '"normalthread")][1]//th/a[2]/@href')[0]
        response = self.session.get(url=first_thread_url, headers=self.headers)

        # Reply
        tree = etree.HTML(response.text)
        form = tree.xpath('//form[@id="fastpostform"]')[0]
        form_action_url = self.root_url + form.xpath('./@action')[0]
        # posttime
        posttime = form.xpath('//input[@id="posttime"]/@value')[0]
        # formhash
        formhash = form.xpath('//input[@name="formhash"]/@value')[0]
        # usesig
        usesig = form.xpath('//input[@name="usesig"]/@value')[0]
        # subject
        subject = form.xpath('//input[@name="subject"]/@value')[0]
        post_reply_data = {
            "message": "我看不懂，但我大受震撼",
            "posttime": posttime,
            "formhash": formhash,
            "usesig": usesig,
            "subject": subject
        }
        self.session.post(url=form_action_url, headers=self.headers, data=post_reply_data)
        print("Posted one reply at", form_action_url)

    # Post new reply until the credit doesn't grow anymore.
    def reply_upon_credit_limitation(self):
        while self.credit < self.credit_cap:
            self.post_new_reply()
            self.new_reply_number += 1
            # Get forum page and get the current credit
            get_thread_list_params = {
                "mod": "forumdisplay",
                "fid": "37"
            }
            response = self.session.get(url=self.forum_url, params=get_thread_list_params, headers=self.headers)
            tree = etree.HTML(response.text)
            # Credit
            if self.credit == self.get_credit_int(tree.xpath('//a[@id="extcreditmenu"]/text()')[0]):
                return
            else:
                self.credit = self.get_credit_int(tree.xpath('//a[@id="extcreditmenu"]/text()')[0])
                time.sleep(25)

    # Get certain amount of threads for voting from starting page.
    def vote_threads(self, target_amount, starting_page):
        voted_amount = 0
        while True:
            get_thread_list_params = {
                "mod": "forumdisplay",
                "fid": "37",
                "page": starting_page
            }
            response = self.session.get(url=self.forum_url, params=get_thread_list_params, headers=self.headers)
            tree = etree.HTML(response.text)
            thread_url_list = tree.xpath(
                '//table[@id="threadlisttableid"]/tbody[contains(@id, "normalthread")]//th/a[2]/@href')
            for thread_url in thread_url_list:
                if voted_amount == target_amount:
                    print("Got enough threads amount.", target_amount, " Leaving...")
                    self.get_current_credit()
                    return

                full_url = self.root_url + thread_url
                response = self.session.get(url=full_url, headers=self.headers)
                tree = etree.HTML(response.text)
                submit_button_list = tree.xpath('//button[@id="pollsubmit"]')
                if len(submit_button_list) != 0:
                    print(full_url, "  is unvoted, voting now...")
                    self.vote_thread(response.text)
                    voted_amount += 1
                else:
                    print(full_url, "  is voted")
            print("Voted {} on page {}, {} more votes required.".format(voted_amount, starting_page, target_amount - voted_amount))
            self.vote_threads(target_amount - voted_amount, starting_page + 1)
            break

    # Vote on the first poll.
    def vote_thread(self, page_text):
        tree = etree.HTML(page_text)
        form = tree.xpath('//form[@id="poll"]')[0]
        request_url = self.root_url + form.xpath('./@action')[0]

        # Get form hash and poll answer
        formhash = form.xpath('.//input[@name="formhash"]/@value')[0]
        pollanswer = form.xpath('.//input[@id="option_1"]/@value')
        post_poll_data = {
            "formhash": formhash,
            "pollanswers[]": pollanswer
        }
        self.session.post(url=request_url, data=post_poll_data, headers=self.headers)

    # Save the current credit locally.
    def get_current_credit(self):
        get_thread_list_params = {
            "mod": "forumdisplay",
            "fid": "37"
        }
        response = self.session.get(url=self.forum_url, params=get_thread_list_params, headers=self.headers)
        tree = etree.HTML(response.text)
        # Credit
        self.credit = self.get_credit_int(tree.xpath('//a[@id="extcreditmenu"]/text()')[0])

    # Extract the credit int from the string
    def get_credit_int(self, credit_string):
        return int(re.search(r'\d+', credit_string).group())
