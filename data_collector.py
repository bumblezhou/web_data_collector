import time
import os
import io
import requests
import shutil
from enum import Enum
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC

import cv2
import numpy as np

global driver
driver = webdriver.Firefox()
# driver = webdriver.Chrome()
driver.get("https://zfcg.scsczt.cn/gp-auth-center/login?origin=oauth")


# 登录
def login():
    time.sleep(4)
    driver.set_window_size(1355, 800) 

    # 三次登录不了, 就重新开始
    print("第一次尝试登录...")
    mock_to_login()

    # 第二次
    try:
        error_msg = driver.find_element(By.XPATH, "//*[@class='erro']")
        if error_msg:
            print("第二次尝试登录...")
            mock_to_login()
    except Exception as e:
        pass

    # 第三次
    try:
        error_msg = driver.find_element(By.XPATH, "//*[@class='erro']")
        if error_msg:
            print("第三次尝试登录...")
            mock_to_login()
    except Exception as e:
        pass

    time.sleep(5)

    # 确定按钮
    try:
        confirm_button = driver.find_element(By.XPATH, "(//button[contains(., '确定')])[last()]")
        if confirm_button:
            print("点击 确定按钮")
            confirm_button.click()
    except Exception as e:
        print("没有 确定按钮, 继续执行")
        return False
    time.sleep(1)
    
    # 电子交易按钮
    try:
        dianzijiaoyi_button = driver.find_element(By.XPATH, "//*[@id='app']/div/div[1]/div[2]/div/div/div[1]/div[1]/div[2]/ul/div/span/li[5]/a")
        if dianzijiaoyi_button:
            print("点击 电子交易按钮")
            dianzijiaoyi_button.click()
    except Exception as e:
        print("没有 电子交易按钮, 继续执行")
        return False
    time.sleep(6)

    # 档案管理按钮
    try:
        danganguanli_button = driver.find_element(By.XPATH, "//li[@title='档案管理']/div")
        if danganguanli_button:
            print("点击 档案管理按钮")
            danganguanli_button.click()
    except Exception as e:
        print("没有 档案管理按钮, 继续执行")
        return False
    time.sleep(1)
    
    # 电子文件归集
    try:
        dianziwenjianguiji_button = driver.find_element(By.XPATH, "//a[contains(., '电子文件归集')]")
        if dianziwenjianguiji_button:
            print("点击 电子文件归集")
            dianziwenjianguiji_button.click()
    except Exception as e:
        print("没有 档案管理按钮, 继续执行")
        return False
    time.sleep(3)

    return True


# 模拟输入用户名密码验证码并点击登录
def mock_to_login():
    username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "userAccount")))
    password = driver.find_element(By.ID, "password")
    verify_code = driver.find_element(By.ID, "verifyCode")
    btn_login = driver.find_element(By.XPATH, "//*[@id='tab1']/div[@class='login']/button[@class='btn-login1']")
    with open('original.jpg', 'wb') as file:
        #identify image to be captured
        verify_code_img = driver.find_element(By.ID, "code_img")
        #write file
        file.write(verify_code_img.screenshot_as_png)
    username.send_keys("test_user")
    password.send_keys("test_password")
    verify_code_text = get_verify_code()
    verify_code.send_keys(verify_code_text)
    time.sleep(1)
    if btn_login:
        btn_login.click()
    time.sleep(3)


# 按页浏览
def navi_by_page():
    # 获取总页数
    total_page_num = 1
    total_page_num_li = driver.find_element(By.XPATH, "//ul[@class='el-pager']/li[last()]")
    if total_page_num_li:
        total_page_num = int(total_page_num_li.text) + 1
        print(f"获取总页数: {total_page_num-1}")
    
    # 循环加载第一页
    for page_num in range(1, total_page_num):
        page_navi_button = driver.find_element(By.XPATH, f"//ul[@class='el-pager']/li[text()={page_num}]")
        if page_navi_button:
            page_navi_button.click()
            print(f"导航到第{page_num}页")
            time.sleep(2)

            # 找到所有的“查看档案”按钮
            view_doc_details_buttons = driver.find_elements(By.XPATH, "//button[contains(., '查看档案')]")
            if view_doc_details_buttons:
                print(f"找到所有的“查看档案”按钮")
                i = 1
                for details_button in view_doc_details_buttons:
                    print(f"点击第{i}个“查看档案”按钮")
                    details_button = driver.find_element(By.XPATH, f"(//button[contains(., '查看档案')])[{i}]")
                    if details_button:
                        # 点击“查看档案”按钮
                        details_button.click()
                        time.sleep(5)
                        print(f"抓取项目基本资料")
                        load_project_basic_info()
                    i = i + 1
            time.sleep(2)


# 加载项目基本信息
def load_project_basic_info():
    # 抓取基本资料
    # 项目编号, 项目名称
    xiangmu_bianhao = ""
    xiangmu_mingcheng = ""
    biaohao_mingcheng_spans = driver.find_elements(By.XPATH, "(//div[@class='el-row'])[2]/div/span")
    if biaohao_mingcheng_spans:
        xiangmu_bianhao = biaohao_mingcheng_spans[0].text
        xiangmu_mingcheng = biaohao_mingcheng_spans[1].text
    
    # 采购单位, 代理机构, 采购方式
    caigo_danwei = ""
    daili_jigou = ""
    caigo_fangshi = ""
    first_line_spans_of_project_details = driver.find_elements(By.XPATH, "(//div[@class='el-row'])[3]/div/span")
    if first_line_spans_of_project_details:
        caigo_danwei = first_line_spans_of_project_details[1].text
        daili_jigou = first_line_spans_of_project_details[3].text
        caigo_fangshi = first_line_spans_of_project_details[5].text
    
    # 采购单位联系人, 代理机构联系人, 采购预算（元）
    caigo_danwei_lianxiren = ""
    daili_jigou_lianxiren = ""
    caigo_yusuan_yuan = ""
    second_line_spans_of_project_details = driver.find_elements(By.XPATH, "(//div[@class='el-row'])[4]/div/span")
    if second_line_spans_of_project_details:
        caigo_danwei_lianxiren = second_line_spans_of_project_details[1].text
        daili_jigou_lianxiren = second_line_spans_of_project_details[3].text
        caigo_yusuan_yuan = second_line_spans_of_project_details[5].text
    
    #采购单位联系电话, 代理机构联系电话, 立项时间
    caigo_danwei_dianhua = ""
    daili_jigou_dianhua = ""
    lixiang_shijian = ""
    third_line_spans_of_project_details = driver.find_elements(By.XPATH, "(//div[@class='el-row'])[5]/div/span")
    if third_line_spans_of_project_details:
        caigo_danwei_dianhua = third_line_spans_of_project_details[1].text
        daili_jigou_dianhua = third_line_spans_of_project_details[3].text
        lixiang_shijian = third_line_spans_of_project_details[5].text
    
    # 创建下载目录
    project_directory = os.path.join(os.getcwd(), f'project_{xiangmu_bianhao}')
    if not os.path.exists(project_directory):
        os.makedirs(project_directory)
    # 这里往数据库里写东西
    project_basic_info = f"项目编号({xiangmu_bianhao}), 项目名称({xiangmu_mingcheng}), 采购单位({caigo_danwei}), 代理机构({daili_jigou}), 采购方式({caigo_fangshi}), 采购单位联系人({caigo_danwei_lianxiren}), 代理机构联系人({daili_jigou_lianxiren}), 采购预算（元）({caigo_yusuan_yuan}), 采购单位联系电话({caigo_danwei_dianhua}), 代理机构联系电话({daili_jigou_dianhua}), 立项时间({lixiang_shijian})"
    print(f"写入数据库: {project_basic_info}")
    project_file_path = f'{project_directory}/项目信息.txt'
    with open(project_file_path, 'w', encoding='utf-8') as f:
        f.write(project_basic_info)
    load_cuosang_wenjian(xiangmu_bianhao)


# 下载采购文件
def load_cuosang_wenjian(xiangmu_bianhao):
    project_directory = os.path.join(os.getcwd(), f'project_{xiangmu_bianhao}')
    # 点击 采购文件
    cuosang_wenjian_button = driver.find_element(By.XPATH, "//a[contains(., '采购文件')]")
    if cuosang_wenjian_button:
        cuosang_wenjian_button.click()
        print("点击 采购文件")
        time.sleep(1)
    
    # 标前文件资料
    all_collapse_items = driver.find_elements(By.XPATH, "(//div[@class='doc_class'])[1]/div[1]/div[1]/div[1]/div[@class='el-collapse-item']/div[1]/div[1]/div[1]/div")
    if all_collapse_items:
        print("展示所有的 标前文件资料")
        for collapse_item in all_collapse_items:
            collapse_item.click()
        time.sleep(1)
    all_biaoqian_wenjian_links = driver.find_elements(By.XPATH, "(//div[@class='doc_class'])[1]/div[1]/div[1]/div[1]/div[@class='el-collapse-item is-active']/div[2]/div/div/div/a")
    if all_biaoqian_wenjian_links:
        download_files(all_biaoqian_wenjian_links, "标前文件资料", project_directory)
        time.sleep(1)

    # 其他附件
    qita_fujian_button = driver.find_element(By.XPATH, "(//div[@class='el-badge item'])[2]")
    if qita_fujian_button:
        print("点击 其他附件")
        qita_fujian_button.click()
    all_collapse_items = driver.find_elements(By.XPATH, "(//div[@class='doc_class'])[2]/div[1]/div[1]/div[1]/div[@class='el-collapse-item']/div[1]/div[1]/div[1]/div")
    if all_collapse_items:
        print("展示所有的 其他附件")
        for collapse_item in all_collapse_items:
            collapse_item.click()
        time.sleep(1)
    all_qita_fujian_links = driver.find_elements(By.XPATH, "(//div[@class='doc_class'])[2]/div[2]/div[1]/div[1]/div[@class='el-collapse-item is-active']/div[2]/div/div/div/a")
    if all_qita_fujian_links:
        download_files(all_qita_fujian_links, "其他附件", project_directory)
        time.sleep(1)
    go_back_button = driver.find_element(By.XPATH, "//button[contains(., '返回')]")
    if go_back_button:
        print("点击 返回 按钮")
        go_back_button.click()


# 下载文件函数
def download_files(all_download_links, download_description, project_directory):
    if all_download_links:
        print(f"准备下载所有 {download_description} ...")
        for download_link in all_download_links:
            download_link.click()
            print(f"点击 {download_link.text}")
            download_folder= os.path.join(os.path.expanduser("~"), f"Downloads/")
            if download_link.text.endswith("html") or download_link.text.endswith("htm"):
                print(f"打开{download_link.text}...")
                time.sleep(10)
                download_button = driver.find_element(By.XPATH, "//button[@text='下载']")
                close_button = driver.find_element(By.XPATH, "//button[@text='关闭']")
                if download_button and close_button:
                    download_button.click()
                    downloaded_file_name = download_link.text.replace(".html", ".pdf")
                    downloaded_file_name = downloaded_file_name.replace(".htm", ".pdf")
                    while not os.path.exists(f"{download_folder}{downloaded_file_name}"):
                        print(f"正在下载{downloaded_file_name}...")
                        time.sleep(5)
                    shutil.move(f"{download_folder}{downloaded_file_name}", os.path.join(project_directory, f"{downloaded_file_name}"))
                    print(f"文件 {downloaded_file_name} 已下载至目录 ({project_directory}).")

                    if str(downloaded_file_name).endswith(".pdf") and driver.capabilities['browserName'] == 'firefox':
                        print(driver.window_handles)
                        driver.switch_to.window(driver.window_handles[1])
                        driver.close()
                        print(driver.window_handles)
                        driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)
            else:
                print(f"下载{download_link.text}...")
                while not os.path.exists(f"{download_folder}{download_link.text}"):
                    print(f"正在下载{download_link.text}...")
                    time.sleep(5)
                shutil.move(f"{download_folder}{download_link.text}", os.path.join(project_directory, f"{download_link.text}"))
                print(f"文件 {download_link.text} 已下载至目录 ({project_directory}).")

                if str(download_link.text).endswith(".pdf") and driver.capabilities['browserName'] == 'firefox':
                    print(driver.window_handles)
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                    print(driver.window_handles)
                    driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)


# 获取登录验证码
def get_verify_code():
    # Read image
    img = cv2.imread('original.jpg')

    # threshold red
    lower = np.array([0, 0, 0])
    upper = np.array([80, 80, 255])
    thresh = cv2.inRange(img, lower, upper)
        
    # Change non-red to white
    result = img.copy()
    result[thresh != 255] = (255,255,255)

    # save results
    cv2.imwrite('red_numerals_thresh.jpg', thresh)
    cv2.imwrite('red_numerals_result.jpg', result)

    img = Image.open('red_numerals_thresh.jpg')

    # text = pytesseract.image_to_string(img)

    import ddddocr
    ocr = ddddocr.DdddOcr()
    with open('red_numerals_thresh.jpg', 'rb') as f:
        img_bytes = f.read()
    text = ocr.classification(img_bytes)
    print("text:{}", text)
    return text


# 主函数
if __name__ == '__main__':
    ret = login()
    if ret:
        navi_by_page()
    else:
        print("登录失败, 请重试.")