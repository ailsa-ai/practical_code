import sys
import os
import re
from PyPDF2 import PdfReader
import tkinter as tk
from tkinter import messagebox


# 获取 EXE 所在目录
def get_exe_dir():
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


# 读取 form_config.txt，确保一定读到
def load_form_list():
    try:
        # form_file = os.path.join(get_exe_dir(), "form_config.txt")
        # form_list = []
        #
        # if os.path.exists(form_file):
        #     with open(form_file, "r", encoding="utf-8") as f:
        #         for line in f:
        #             line = line.strip()
        #             if line and not line.startswith("#"):
        #                 form_list.append(line)
        form_list = [
            "实习入职审批表",
            "入职审批表",
            "实习入职申请表",
            "入职申请表",
            "离职申请表",
            "离职审批表",
            "加班申请表",
            "加班审批表",
            "请假申请表",
            "报销申请表",
            "员工信息表",
            "劳动合同",
            "岗位说明书",
            # 你可以无限加...
        ]

        # 长表名优先，防止短名称抢先匹配
        form_list = sorted(form_list, key=len, reverse=True)
        return form_list
    except:
        return []


# 提取信息（完全保留：独占一行表名识别）
def extract_info(text):
    name = None
    emp_id = None
    form_name = None

    # 姓名提取
    # 把所有换行、多空格、制表符统一压缩成单个空格
    s = re.sub(r'\s+', ' ', text)
    name_pattern = re.search(r"姓名\s*([A-Za-z\u4e00-\u9fa5 ]{2,30})", s)
    # 如果匹配到姓名，取出内容并去掉首尾空格
    if name_pattern:
        raw_name = name_pattern.group(1).strip()
        # 定义停止词：遇到这些词就说明不是名字了
        stop_words = ["部门", "职位", "入职日期", "工号", "银行卡号", "应聘者来源"]
        # 循环检查：如果名字里包含停止词，就截断
        for stop in stop_words:
            if stop in raw_name:
                raw_name = raw_name.split(stop)[0].strip()
                break
        name = re.sub(r"\s+", " ", raw_name)

    # 工号提取
    id_pattern = re.search(r"工号\s*([A-Za-z0-9]+)", text)
    if id_pattern:
        emp_id = id_pattern.group(1).strip()

    # ==============================
    # 独占一行表名 空白清理
    # ==============================
    clean_text = re.sub(r"\s+", "", text)

    # 读取配置
    form_list = load_form_list()

    # 【调试用】能看到加载了哪些表名（可打开看）
    # print("加载的表单列表：", form_list)

    # 轮询匹配
    for form in form_list:
        try:
            clean_form = re.sub(r"\s+", "", form)
            if clean_form in clean_text:
                form_name = form
                break
        except:
            continue

    return name, emp_id, form_name


# 批量重命名
def batch_rename():
    current_dir = get_exe_dir()
    pdf_files = [f for f in os.listdir(current_dir) if f.lower().endswith(".pdf")]

    for filename in pdf_files:
        pdf_path = os.path.join(current_dir, filename)
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t

            name, emp_id, form_name = extract_info(text)

            # 命名规则
            if name and emp_id and form_name:
                new_name = f"{name}_{emp_id}_{form_name}.pdf"
            elif name and emp_id:
                new_name = f"{name}_{emp_id}.pdf"
            elif name and form_name:
                new_name = f"{name}_{form_name}.pdf"
            elif emp_id and form_name:
                new_name = f"{emp_id}_{form_name}.pdf"
            elif name:
                new_name = f"{name}.pdf"
            elif emp_id:
                new_name = f"{emp_id}.pdf"
            elif form_name:
                new_name = f"{form_name}.pdf"
            else:
                new_name = f"未识别_{filename}"

            new_path = os.path.join(current_dir, new_name)

            idx = 1
            while os.path.exists(new_path):
                new_path = os.path.join(current_dir, f"{os.path.splitext(new_name)[0]}_{idx}.pdf")
                idx += 1

            os.rename(pdf_path, new_path)

        except Exception:
            continue


# 主程序
if __name__ == '__main__':
    batch_rename()
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("完成", "PDF批量重命名完成！")
    root.destroy()
