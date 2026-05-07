import pytest
import allure
import requests
import math
import json
import re
import urllib3
from config.logger import *
from config.env_config import ENV, ENV_VARS
from config.settings import *


# =====================测试类=======================================
@allure.feature("数据导入模块")
@allure.story("角色判断+对象标识+组合索引+异步轮询验证+模拟关闭弹窗+打印导入结果统计")
class TestImportProcess:
    def test_complete_import(self, saml_session):
        s = saml_session
        logging.info("当前环境", ENV_VARS[ENV]['base_url'])
        import_id = None
        mapping_list = []
        result = {}
        all_data_list = []
        final_status = 'UNKNOEN'
        polling_success = False
        result_data = {}
        final_error_msg = ""
        success_count = 0
        fail_count = 0
        total_count = 0
