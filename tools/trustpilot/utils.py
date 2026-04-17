# utils.py
import os
import requests
import re
import socket
import time
import socks

def create_directory(directory):
    """创建目录，如果目录不存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def extract_country_code(text, username):
    """
    从文本中提取有效的国家代码，避免将用户名误认为国家代码
    """
    from config import VALID_COUNTRY_CODES, COUNTRY_NAME_TO_CODE
    
    if not text:
        return "Unknown"
    
    words = text.strip().split()
    
    for word in words:
        cleaned_word = word.strip().upper()
        
        if cleaned_word.lower() == username.lower():
            continue
            
        if 2 <= len(cleaned_word) <= 3 and cleaned_word in VALID_COUNTRY_CODES:
            return cleaned_word
        
        if cleaned_word.lower() in COUNTRY_NAME_TO_CODE:
            return COUNTRY_NAME_TO_CODE[cleaned_word.lower()]
    
    return "Unknown"

def parse_proxy_string(proxy_str):
    """解析代理字符串 HOST:PORT:USER:PASS 为字典格式"""
    parts = proxy_str.split(':')
    if len(parts) == 4:
        # 处理特殊情况"none:none"表示无认证
        user = None if parts[2].lower() == 'none' else parts[2]
        password = None if parts[3].lower() == 'none' else parts[3]
        
        return {
            'host': parts[0],
            'port': parts[1],
            'user': user,
            'pass': password,
            'original_string': proxy_str,
            'requires_auth': user is not None and password is not None
        }
    print(f"警告：无法解析代理字符串：{proxy_str}。预期4个部分，实际得到{len(parts)}。")
    return None

def check_proxy_health(proxy_details):
    """检查SOCKS5代理是否工作正常，通过尝试多种协议和多个测试站点"""
    if not proxy_details:
        return False
    
    # 格式化不同协议的代理URL
    if proxy_details.get('requires_auth', True):
        proxy_auth = f"{proxy_details['user']}:{proxy_details['pass']}@{proxy_details['host']}:{proxy_details['port']}"
        
        proxy_urls = {
            'socks5h': f"socks5h://{proxy_auth}",
            'socks5': f"socks5://{proxy_auth}",
            'http': f"http://{proxy_auth}",
            'https': f"https://{proxy_auth}"
        }
    else:
        # 无认证的代理
        proxy_urls = {
            'socks5h': f"socks5h://{proxy_details['host']}:{proxy_details['port']}",
            'socks5': f"socks5://{proxy_details['host']}:{proxy_details['port']}",
            'http': f"http://{proxy_details['host']}:{proxy_details['port']}",
            'https': f"https://{proxy_details['host']}:{proxy_details['port']}"
        }
    
    test_sites = [
        "https://api.ipify.org?format=json",  # 主要测试
        "https://httpbin.org/ip",             # 备用测试1
        "https://ifconfig.me/ip"              # 备用测试2
    ]
    
    success = False
    # 尝试不同协议类型
    for protocol, proxy_url in proxy_urls.items():
        if success:
            break
            
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        print(f"测试代理 {proxy_details['host']}:{proxy_details['port']} 使用 {protocol} 协议...")
        
        # 依次尝试不同的测试站点
        for test_site in test_sites:
            try:
                # 较短超时以快速识别问题
                response = requests.get(test_site, proxies=proxies, timeout=10)
                
                # 验证响应
                if response.status_code == 200:
                    if 'ipify' in test_site:
                        returned_ip = response.json().get('ip')
                    elif 'httpbin' in test_site:
                        returned_ip = response.json().get('origin')
                    else:  # ifconfig.me
                        returned_ip = response.text.strip()
                    
                    print(f"代理 {proxy_details['host']}:{proxy_details['port']} 使用 {protocol} 成功！")
                    print(f"通过代理获取的外部IP: {returned_ip}")
                    
                    # 作为额外验证，确认返回的IP与代理IP不同
                    try:
                        local_ip = requests.get("https://api.ipify.org?format=json", timeout=5).json().get('ip')
                        if local_ip != returned_ip:
                            print(f"验证通过: 本地IP ({local_ip}) 与代理IP ({returned_ip}) 不同")
                            success = True
                            return True
                        else:
                            print(f"警告: 代理似乎未生效，返回的IP与本地IP相同: {local_ip}")
                    except Exception as e:
                        print(f"无法获取本地IP进行比较，但代理连接成功: {e}")
                        success = True
                        return True
                        
            except requests.exceptions.Timeout:
                print(f"使用 {protocol} 协议连接到 {test_site} 超时")
            except requests.exceptions.RequestException as e:
                print(f"使用 {protocol} 协议连接到 {test_site} 请求异常: {e}")
            except Exception as e:
                print(f"使用 {protocol} 协议连接到 {test_site} 未知错误: {e}")
    
    # 尝试使用套接字直接测试SOCKS5连接
    try:
        print(f"尝试套接字级别的SOCKS5连接测试...")
        # 创建套接字
        s = socks.socksocket()
        # 设置代理
        if proxy_details.get('requires_auth', True):
            s.set_proxy(
                proxy_type=socks.SOCKS5,
                addr=proxy_details['host'],
                port=int(proxy_details['port']),
                username=proxy_details['user'],
                password=proxy_details['pass']
            )
        else:
            s.set_proxy(
                proxy_type=socks.SOCKS5,
                addr=proxy_details['host'],
                port=int(proxy_details['port'])
            )
        # 设置超时
        s.settimeout(10)
        # 尝试连接一个常见网站
        s.connect(('www.google.com', 80))
        s.close()
        print(f"套接字级别连接成功！代理 {proxy_details['host']}:{proxy_details['port']} 可用")
        return True
    except Exception as e:
        print(f"套接字级别连接失败: {e}")
    
    print(f"代理 {proxy_details['host']}:{proxy_details['port']} 经过所有测试均不可用")
    return False

# It's good practice to keep existing utility functions like create_directory and extract_country_code
# Ensure extract_brand_name is also here if it was intended to be a general utility.
# For now, assuming extract_brand_name from scraper.py is used by main.py