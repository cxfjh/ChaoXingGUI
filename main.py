import os
import re
import ctypes
import argparse
import configparser
from api.answer import Tiku
from threading import Thread
from api.logger import logger
from api.base import Chaoxing, Account
from api.exceptions import LoginError, FormatError, JSONDecodeError, MaxRollBackError
from urllib3 import disable_warnings, exceptions


# 弹出信息框
def MessageBox(title, text):
    ctypes.windll.user32.MessageBoxW(None, text, title, 0x0 | 0x40)


# 禁用不安全的请求警告
disable_warnings(exceptions.InsecureRequestWarning)

filePath = "./log/disposition.txt"
textPath = "./log/course.txt"
errorPath = './log/error.txt'

if os.path.exists(errorPath): os.remove(errorPath)


# 从文件中提取账号信息。
def extractInfoFromFile():
    try: 
        if not os.path.exists(filePath): return
        with open(filePath, 'r', encoding='utf-8') as file: content = file.read()
        account = re.search(r'账号：(\d+)', content)
        password = re.search(r'密码：(.+)', content)
        userId = re.search(r'ID：(\d+)', content)
        return [account.group(1), password.group(1), userId.group(1)]
    except Exception as e:
        logger.error(f"提取账号信息失败: {e}")
        return None


# 从文件中提取账号信息。
info = extractInfoFromFile()


# 追加文本
def appendText(text):
    if not os.path.exists(textPath): return
    with open(textPath, 'a', encoding='utf-8') as file: file.write(f'{text}, ') 


# 获取文本
def getText():
    try: 
        if not os.path.exists(textPath):
            with open(textPath, 'x') as file: pass 
            return []
        with open(textPath, 'r', encoding='utf-8') as file: content = file.read().split(',')
        content = {int(item.strip()) for item in content if item.strip()}
        return list(content)
    except Exception as e: logger.error(f"获取文本失败: {e}"); return []


# 初始化配置，通过命令行参数或配置文件获取配置信息。
def initConfig():
    parser = argparse.ArgumentParser(description="Samueli924/chaoxing")
    parser.add_argument("-c", "--config", type=str, default=None, help="使用配置文件运行程序")
    parser.add_argument("-u", "--username", type=str, default=None, help="手机号账号")
    parser.add_argument("-p", "--password", type=str, default=None, help="登录密码")
    parser.add_argument("-l", "--list", type=str, default=None, help="要学习的课程ID列表")
    parser.add_argument("-s", "--speed", type=float, default=1.0, help="视频播放倍速(默认1，最大2)")
    args = parser.parse_args()
    if args.config:
        config = configparser.ConfigParser()
        config.read(args.config, encoding="utf8")
        return (
            config.get("common", "username"),
            config.get("common", "password"),
            (str(config.get("common", "courseList")).split(",") if config.get("common", "courseList") else None),
            int(config.get("common", "speed")),
            config["tiku"],
        )
    return (args.username, args.password, args.list.split(",") if args.list else None, int(args.speed) if args.speed else 1, None)


# 管理回滚次数，防止无限回滚。
class RollBackManager:
    def __init__(self) -> None:
        self.rollbackTimes = 0
        self.rollbackId = ""

    # 增加回滚次数，如果超过3次则抛出异常。
    def addTimes(self, id: str) -> None:
        if id == self.rollbackId and self.rollbackTimes == 3: raise MaxRollBackError("回滚次数已达3次，请手动检查学习通任务点完成情况")
        elif id != self.rollbackId: self.rollbackId = id; self.rollbackTimes = 1
        else: self.rollbackTimes += 1


# 登录账号并初始化Chaoxing对象。
def loginAccount(username, password):
    account = Account(username, password)
    tiku = Tiku()
    chaoxing = Chaoxing(account=account, tiku=tiku)
    loginState = chaoxing.login()
    if not loginState["status"]: 
        with open(errorPath, 'w', encoding='utf-8') as file: file.write(loginState["msg"])
        raise LoginError(loginState["msg"])
    return chaoxing


# 获取用户要学习的课程列表。
def getCourseTask(chaoxing, courseList, allCourses):
    courseTask = []
    if not courseList:
        print("*" * 10 + "课程列表" + "*" * 10)
        for course in allCourses: print(f"ID: {course['courseId']} 课程名: {course['title']}")
        print("*" * 28)
        try: courseList = input("请输入要学习的课程ID ") if not info else info[2]
        except Exception as e: raise FormatError("输入格式错误") from e
    for course in allCourses:
        if course["courseId"] in courseList: courseTask.append(course)
    if not courseTask: courseTask = allCourses
    return courseTask


# 学习指定课程。
def studyCourse(chaoxing, course, rbManager, speed):
    logger.info(f"开始学习课程: {course['title']}")
    pointList = chaoxing.get_course_point(course["courseId"], course["clazzId"], course["cpi"])
    pointIndex = 0  # 任务点索引

    # 循环播放视频，直到所有任务点都完成。
    while pointIndex < len(pointList["points"]):
        point = pointList["points"][pointIndex]
        logger.info(f'当前章节: {point["title"]}')
        jobs, jobInfo = chaoxing.get_job_list(course["clazzId"], course["courseId"], course["cpi"], point["id"])
        
        try: bookID = jobInfo["knowledgeid"] # 获取视频ID
        except KeyError: Thread(target=MessageBox, args=("提示", f'{point["title"]} 该章节没有视频，已跳过')).start()
        
        # 章节未开启，回滚到上一个任务点。
        if jobInfo.get("notOpen", False) :
            pointIndex -= 1
            if not chaoxing.tiku or chaoxing.tiku.DISABLE or not chaoxing.tiku.SUBMIT:logger.error(f"章节未开启，请手动完成并提交再重试，或者开启题库并启用提交");break
            rbManager.addTimes(point["id"])
            continue

        if not jobs: pointIndex += 1; continue # 章节任务点数量为0，跳过。

        # 循环播放任务点。
        for job in jobs:
            if job["type"] == "video":          
                TextBookID = getText()
                if TextBookID.count(bookID) > 0: break
                appendText(bookID)

                logger.trace(f"识别到视频任务, 任务章节: {course['title']} 任务ID: {job['jobid']}")
                isAudio = False
                try: chaoxing.study_video(course, job, jobInfo, _speed=speed, _type="Video")
                except JSONDecodeError: logger.warning("当前任务非视频任务，正在尝试音频任务解码");isAudio = True
                if isAudio:
                    try: chaoxing.study_video(course, job, jobInfo, _speed=speed, _type="Audio")
                    except JSONDecodeError:logger.warning(f"出现异常任务 -> 任务章节: {course['title']} 任务ID: {job['jobid']}, 已跳过")

            # 如果是文档任务，则下载文档。
            elif job["type"] == "document":
                TextBookID = getText()
                if TextBookID.count(bookID) > 0: break
                appendText(bookID)

                logger.trace(f"识别到文档任务, 任务章节: {course['title']} 任务ID: {job['jobid']}")
                chaoxing.study_document(course, job)
            
            # 如果是章节检测任务，则完成检测。
            elif job["type"] == "workid":
                TextBookID = getText()
                if TextBookID.count(bookID) > 0: break
                appendText(bookID)

                logger.trace(f"识别到章节检测任务, 任务章节: {course['title']}")
                chaoxing.study_work(course, job, jobInfo)

            # 如果是阅读任务，则阅读文章。
            elif job["type"] == "read":
                TextBookID = getText()
                if TextBookID.count(bookID) > 0: break
                appendText(bookID)

                logger.trace(f"识别到阅读任务, 任务章节: {course['title']}")
                chaoxing.study_read(course, job, jobInfo)
        pointIndex += 1


# 启动学习任务。
def start():
    try:
        rbManager = RollBackManager()
        username, password, courseList, speed, tiku_config = initConfig()
        speed = 2.0
        if not username or not password:
            username = input("请输入手机号账号: ") if not info else info[0]
            password = input("请输入登录密码: ") if not info else info[1]
        chaoxing = loginAccount(username, password)
        tiku = Tiku()
        tiku.config_set(tiku_config)
        tiku = tiku.get_tiku_from_config()
        tiku.init_tiku()
        chaoxing.tiku = tiku
        allCourses = chaoxing.get_course_list()
        courseTask = getCourseTask(chaoxing, courseList, allCourses)
        logger.info(f"课程列表过滤完毕，当前课程任务数量: {len(courseTask)}")
        for course in courseTask: studyCourse(chaoxing, course, rbManager, speed)
        logger.info("所有课程学习任务已完成")
    except BaseException as e:
        import traceback
        logger.error(f"错误: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        raise e

# 启动线程
if __name__ == "__main__":
    Thread(target=start).start()
