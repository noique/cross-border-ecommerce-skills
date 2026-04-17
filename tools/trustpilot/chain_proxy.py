# chain_proxy.py
import requests
import socks
import socket
from config import V2RAY_CONFIG, USE_CHAIN_PROXY, PROXY_MODE
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_v2ray_base_proxy():
    """配置基本的V2Ray代理连接信息"""
    socks_config = V2RAY_CONFIG['socks']
    http_config = V2RAY_CONFIG['http']
    
    return {
        'socks': {
            'url': f"{socks_config['protocol']}://{socks_config['host']}:{socks_config['port']}",
            'host': socks_config['host'],
            'port': socks_config['port'],
            'protocol': socks_config['protocol']
        },
        'http': {
            'url': f"{http_config['protocol']}://{http_config['host']}:{http_config['port']}",
            'host': http_config['host'],
            'port': http_config['port'],
            'protocol': http_config['protocol']
        }
    }

def create_chain_selenium_wire_options(remote_proxy_str, base_proxy_type="socks"):
    """创建适用于Selenium Wire的代理链配置"""
    from utils import parse_proxy_string
    
    # 解析远程代理
    remote_proxy = parse_proxy_string(remote_proxy_str)
    if not remote_proxy:
        print(f"❌ 无法解析远程代理: {remote_proxy_str}")
        return None
    
    # 获取V2Ray基本代理信息
    v2ray = setup_v2ray_base_proxy()
    base = v2ray[base_proxy_type]
    
    # 创建代理配置
    options = {}
    
    # 根据代理模式选择配置方式
    if PROXY_MODE == "chain" and USE_CHAIN_PROXY:
        # 使用代理链 - V2Ray作为上游代理
        options = {
            'proxy': {
                'http': base['url'],
                'https': base['url'],
                'no_proxy': 'localhost,127.0.0.1'
            },
            'connection_timeout': 30,
            'verify_ssl': False,
            'suppress_connection_errors': False
        }
        chain_info = f"{base['url']} -> {remote_proxy['host']}:{remote_proxy['port']}"
        print(f"设置代理链: {chain_info}")
    
    elif PROXY_MODE == "v2ray":
        # 只使用V2Ray代理，忽略远程代理
        options = {
            'proxy': {
                'http': base['url'],
                'https': base['url'],
                'no_proxy': 'localhost,127.0.0.1'
            },
            'connection_timeout': 30,
            'verify_ssl': False,
            'suppress_connection_errors': False
        }
        print(f"仅使用V2Ray代理: {base['url']}")
    
    elif PROXY_MODE == "direct":
        # 直接使用远程代理，不通过V2Ray
        if remote_proxy.get('requires_auth', True):
            proxy_url_http = f"http://{remote_proxy['user']}:{remote_proxy['pass']}@{remote_proxy['host']}:{remote_proxy['port']}"
            proxy_url_socks = f"socks5://{remote_proxy['user']}:{remote_proxy['pass']}@{remote_proxy['host']}:{remote_proxy['port']}"
        else:
            proxy_url_http = f"http://{remote_proxy['host']}:{remote_proxy['port']}"
            proxy_url_socks = f"socks5://{remote_proxy['host']}:{remote_proxy['port']}"
        
        options = {
            'proxy': {
                'http': proxy_url_http,
                'https': proxy_url_http,
                'no_proxy': 'localhost,127.0.0.1'
            },
            'connection_timeout': 30,
            'verify_ssl': False,
            'suppress_connection_errors': False
        }
        print(f"直接使用远程代理: {remote_proxy['host']}:{remote_proxy['port']}")
        
    elif PROXY_MODE == "local":
        # 不使用任何代理，保留空的代理配置
        print("使用本地网络，不使用代理")
        return None
    
    return options

def create_seleniumwire_driver(proxy_options, chrome_options=None):
    """创建使用代理链的Selenium Wire WebDriver"""
    if chrome_options is None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
            seleniumwire_options=proxy_options
        )
        return driver
    except Exception as e:
        print(f"创建WebDriver时出错: {e}")
        return None

def verify_proxy_connection(driver, thread_identifier):
    """验证代理连接是否工作正常"""
    try:
        print(f"[{thread_identifier}] 验证代理连接...")
        driver.get("https://api.ipify.org?format=json")
        
        # 等待页面加载
        import time
        import json
        time.sleep(3)
        
        # 提取IP信息
        try:
            body_text = driver.page_source.split("<body>")[1].split("</body>")[0].strip()
            ip_info = json.loads(body_text)
            print(f"[{thread_identifier}] 通过代理获取的IP: {ip_info.get('ip', '未知')}")
            return True
        except Exception as ip_err:
            print(f"[{thread_identifier}] 无法解析代理IP信息: {ip_err}")
            return False
    except Exception as e:
        print(f"[{thread_identifier}] 验证代理连接时出错: {e}")
        return False 