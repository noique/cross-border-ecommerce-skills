# test_proxy.py
import requests
import socks
import socket
import json
import argparse
from utils import parse_proxy_string, check_proxy_health
from config import PROXIES

def test_local_connection():
    """测试本地网络连接"""
    print("\n===== 测试本地网络连接 =====")
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=10)
        if response.status_code == 200:
            ip_info = response.json()
            print(f"✅ 本地网络连接正常")
            print(f"🌐 本地IP地址: {ip_info.get('ip')}")
            return True
        else:
            print(f"❌ 本地网络连接异常: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 本地网络连接测试失败: {e}")
        return False

def test_socket_direct(host, port, username=None, password=None, proxy_type=socks.SOCKS5):
    """使用直接套接字方式测试代理连接"""
    print(f"\n----- 使用套接字直接测试连接 -----")
    try:
        # 创建套接字
        s = socks.socksocket()
        
        # 设置代理
        if username and password:
            s.set_proxy(
                proxy_type=proxy_type,
                addr=host,
                port=int(port),
                username=username,
                password=password
            )
        else:
            s.set_proxy(
                proxy_type=proxy_type,
                addr=host,
                port=int(port)
            )
        
        # 设置超时
        s.settimeout(10)
        
        # 尝试连接Google
        print(f"正在尝试通过代理连接 www.google.com...")
        s.connect(('www.google.com', 80))
        s.close()
        print(f"✅ 套接字级别连接成功!")
        return True
    except Exception as e:
        print(f"❌ 套接字级别连接失败: {e}")
        return False

def test_with_requests(proxy_url, protocol):
    """使用requests库测试代理连接"""
    print(f"\n----- 使用requests测试 {protocol} 协议 -----")
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    sites_to_test = [
        ("https://api.ipify.org?format=json", "ipify"),
        ("https://httpbin.org/ip", "httpbin"),
        ("https://ifconfig.me/ip", "ifconfig.me")
    ]
    
    for url, site_name in sites_to_test:
        try:
            print(f"正在尝试通过 {protocol} 代理访问 {site_name}...")
            response = requests.get(url, proxies=proxies, timeout=15)
            if response.status_code == 200:
                if site_name == "ipify":
                    ip = response.json().get('ip')
                elif site_name == "httpbin":
                    ip = response.json().get('origin')
                else:  # ifconfig.me
                    ip = response.text.strip()
                    
                print(f"✅ 成功通过 {protocol} 代理访问 {site_name}")
                print(f"🌐 通过代理获取的IP: {ip}")
                return True, ip
            else:
                print(f"❌ 访问 {site_name} 失败: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ 访问 {site_name} 异常: {e}")
    
    return False, None

def test_proxy(proxy_str):
    """测试指定的代理"""
    print(f"\n===== 测试代理: {proxy_str} =====")
    parsed_proxy = parse_proxy_string(proxy_str)
    if not parsed_proxy:
        print("❌ 代理字符串格式不正确")
        return False
    
    print(f"代理信息:")
    print(f"  主机: {parsed_proxy['host']}")
    print(f"  端口: {parsed_proxy['port']}")
    print(f"  用户名: {parsed_proxy['user']}")
    print(f"  密码: {'*' * len(parsed_proxy['pass'])}")
    
    # 测试不同的协议
    protocols_to_test = [
        ('socks5h', f"socks5h://{parsed_proxy['user']}:{parsed_proxy['pass']}@{parsed_proxy['host']}:{parsed_proxy['port']}"),
        ('socks5', f"socks5://{parsed_proxy['user']}:{parsed_proxy['pass']}@{parsed_proxy['host']}:{parsed_proxy['port']}"),
        ('http', f"http://{parsed_proxy['user']}:{parsed_proxy['pass']}@{parsed_proxy['host']}:{parsed_proxy['port']}"),
    ]
    
    success = False
    
    # 先测试套接字连接
    socket_success = test_socket_direct(
        parsed_proxy['host'], 
        parsed_proxy['port'], 
        parsed_proxy['user'],
        parsed_proxy['pass']
    )
    
    if socket_success:
        print("✅ 套接字测试成功，代理基本连接正常")
    else:
        print("⚠️ 套接字测试失败，但继续测试其他协议")
    
    # 测试不同的代理协议
    proxy_ip = None
    for protocol, url in protocols_to_test:
        protocol_success, ip = test_with_requests(url, protocol)
        if protocol_success:
            success = True
            proxy_ip = ip
            print(f"✅ {protocol} 协议测试成功")
        else:
            print(f"❌ {protocol} 协议测试失败")
    
    if success:
        print(f"\n✅ 代理 {proxy_str} 至少有一种协议工作正常")
        print(f"🌐 代理IP: {proxy_ip}")
    else:
        print(f"\n❌ 代理 {proxy_str} 所有协议测试均失败")
    
    return success

def main():
    parser = argparse.ArgumentParser(description="测试代理连接")
    parser.add_argument("--all", action="store_true", help="测试配置文件中的所有代理")
    parser.add_argument("--proxy", type=str, help="测试指定的代理字符串 (格式: HOST:PORT:USER:PASS)")
    parser.add_argument("--test_local", action="store_true", help="仅测试本地网络连接")
    parser.add_argument("--socks", action="store_true", help="测试SOCKS端口10808")
    parser.add_argument("--http", action="store_true", help="测试HTTP端口10809")
    
    args = parser.parse_args()
    
    # 测试本地连接
    if args.test_local or not (args.all or args.proxy or args.socks or args.http):
        test_local_connection()
    
    # 测试本地SOCKS端口10808
    if args.socks:
        print("\n===== 测试本地SOCKS端口10808 =====")
        socket_success = test_socket_direct("127.0.0.1", 10808)
        if socket_success:
            print("✅ 本地SOCKS 10808端口连接成功")
        else:
            print("❌ 本地SOCKS 10808端口连接失败")
        
        success, ip = test_with_requests("socks5://127.0.0.1:10808", "socks5")
        if success:
            print(f"✅ 本地SOCKS 10808端口工作正常，获取IP: {ip}")
        else:
            print("❌ 通过requests测试本地SOCKS 10808端口失败")
    
    # 测试本地HTTP端口10809
    if args.http:
        print("\n===== 测试本地HTTP端口10809 =====")
        success, ip = test_with_requests("http://127.0.0.1:10809", "http")
        if success:
            print(f"✅ 本地HTTP 10809端口工作正常，获取IP: {ip}")
        else:
            print("❌ 通过requests测试本地HTTP 10809端口失败")
    
    # 测试特定代理
    if args.proxy:
        test_proxy(args.proxy)
    
    # 测试所有配置的代理
    if args.all:
        print("\n===== 测试配置文件中的所有代理 =====")
        if not PROXIES:
            print("配置文件中没有定义代理")
            return
        
        working_proxies = []
        for proxy_str in PROXIES:
            if test_proxy(proxy_str):
                working_proxies.append(proxy_str)
        
        print("\n===== 测试结果汇总 =====")
        print(f"共测试 {len(PROXIES)} 个代理，{len(working_proxies)} 个工作正常")
        if working_proxies:
            print("可用代理:")
            for i, proxy in enumerate(working_proxies, 1):
                print(f"{i}. {proxy}")
        else:
            print("没有发现可用的代理")

if __name__ == "__main__":
    main() 