# direct_proxy_test.py
import requests
import argparse
from utils import parse_proxy_string
from config import PROXIES

def test_direct_proxy(proxy_str):
    """直接测试代理连接，不使用V2Ray"""
    print(f"\n===== 直接测试远程代理: {proxy_str} =====")
    
    # 解析代理字符串
    proxy = parse_proxy_string(proxy_str)
    if not proxy:
        print("❌ 代理字符串格式不正确")
        return False
    
    # 构建代理URL (使用两种协议格式测试)
    if proxy.get('requires_auth', True):
        socks5_url = f"socks5://{proxy['user']}:{proxy['pass']}@{proxy['host']}:{proxy['port']}"
        http_url = f"http://{proxy['user']}:{proxy['pass']}@{proxy['host']}:{proxy['port']}"
    else:
        socks5_url = f"socks5://{proxy['host']}:{proxy['port']}"
        http_url = f"http://{proxy['host']}:{proxy['port']}"
    
    # 测试本地连接获取基准IP
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=10)
        if response.status_code == 200:
            local_ip = response.json().get('ip')
            print(f"✅ 本地网络连接正常，本地IP: {local_ip}")
        else:
            print(f"❌ 本地网络连接异常: 状态码 {response.status_code}")
            local_ip = None
    except Exception as e:
        print(f"❌ 本地网络连接测试失败: {e}")
        local_ip = None
    
    # 测试SOCKS5协议
    success = False
    proxies = {'http': socks5_url, 'https': socks5_url}
    print(f"\n----- 测试SOCKS5协议: {socks5_url} -----")
    
    try:
        response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=20)
        if response.status_code == 200:
            ip = response.json().get('ip')
            print(f"✅ SOCKS5协议连接成功, IP: {ip}")
            if local_ip and ip != local_ip:
                print(f"✅ 代理IP ({ip}) 与本地IP ({local_ip}) 不同，代理正常工作")
                success = True
            elif local_ip and ip == local_ip:
                print(f"⚠️ 代理IP ({ip}) 与本地IP相同，代理可能未生效")
            else:
                print(f"✅ 无法比较本地IP，但代理连接成功")
                success = True
        else:
            print(f"❌ SOCKS5连接失败: 状态码 {response.status_code}")
    except Exception as e:
        print(f"❌ SOCKS5测试失败: {e}")
    
    # 测试HTTP协议
    proxies = {'http': http_url, 'https': http_url}
    print(f"\n----- 测试HTTP协议: {http_url} -----")
    
    try:
        response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=20)
        if response.status_code == 200:
            ip = response.json().get('ip')
            print(f"✅ HTTP协议连接成功, IP: {ip}")
            if local_ip and ip != local_ip:
                print(f"✅ 代理IP ({ip}) 与本地IP ({local_ip}) 不同，代理正常工作")
                success = True
            elif local_ip and ip == local_ip:
                print(f"⚠️ 代理IP ({ip}) 与本地IP相同，代理可能未生效")
            else:
                print(f"✅ 无法比较本地IP，但代理连接成功")
                success = True
        else:
            print(f"❌ HTTP连接失败: 状态码 {response.status_code}")
    except Exception as e:
        print(f"❌ HTTP测试失败: {e}")
    
    # 返回测试结果
    if success:
        print(f"\n✅ 代理 {proxy_str} 测试成功！")
    else:
        print(f"\n❌ 代理 {proxy_str} 测试失败。")
    
    return success

def main():
    parser = argparse.ArgumentParser(description="直接测试远程代理连接")
    parser.add_argument("--proxy1", action="store_true", help="测试第一个远程代理 (93.89.220.26)")
    parser.add_argument("--proxy2", action="store_true", help="测试第二个远程代理 (149.18.52.92)")
    parser.add_argument("--all", action="store_true", help="测试所有远程代理")
    parser.add_argument("--proxy", type=str, help="指定要测试的代理字符串 (格式: HOST:PORT:USER:PASS)")
    
    args = parser.parse_args()
    
    # 如果没有指定参数，默认测试所有代理
    if not args.proxy1 and not args.proxy2 and not args.proxy and not args.all:
        args.all = True
    
    print("开始直接测试代理连接 (不通过V2Ray)")
    
    # 测试指定的代理
    if args.proxy:
        test_direct_proxy(args.proxy)
        return
    
    # 测试第一个代理
    if args.proxy1 or args.all:
        remote_proxies = [p for p in PROXIES if not p.startswith("127.0.0.1")]
        if len(remote_proxies) >= 1:
            test_direct_proxy(remote_proxies[0])
    
    # 测试第二个代理
    if args.proxy2 or args.all:
        remote_proxies = [p for p in PROXIES if not p.startswith("127.0.0.1")]
        if len(remote_proxies) >= 2:
            test_direct_proxy(remote_proxies[1])
    
    # 测试所有远程代理
    if args.all and not (args.proxy1 or args.proxy2):
        remote_proxies = [p for p in PROXIES if not p.startswith("127.0.0.1")]
        
        if not remote_proxies:
            print("❌ 配置文件中没有定义远程代理")
            return
        
        results = []
        for proxy in remote_proxies:
            if test_direct_proxy(proxy):
                results.append(proxy)
        
        # 显示测试结果摘要
        print("\n===== 测试结果摘要 =====")
        print(f"共测试 {len(remote_proxies)} 个代理，{len(results)} 个工作正常")
        
        if results:
            print("\n可用代理:")
            for i, proxy in enumerate(results, 1):
                print(f"{i}. {proxy}")

if __name__ == "__main__":
    main() 