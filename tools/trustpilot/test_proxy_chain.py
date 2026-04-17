# test_proxy_chain.py
import requests
import socks
import socket
import json
import argparse
from utils import parse_proxy_string
from config import PROXIES, V2RAY_CONFIG, USE_CHAIN_PROXY

def test_local_connection():
    """测试本地网络连接"""
    print("\n===== 测试本地网络连接 =====")
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=10)
        if response.status_code == 200:
            ip_info = response.json()
            print(f"✅ 本地网络连接正常")
            print(f"🌐 本地IP地址: {ip_info.get('ip')}")
            return True, ip_info.get('ip')
        else:
            print(f"❌ 本地网络连接异常: 状态码 {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ 本地网络连接测试失败: {e}")
        return False, None

def test_v2ray_proxies():
    """测试V2Ray代理"""
    print("\n===== 测试V2Ray代理 =====")
    
    results = {}
    # 测试SOCKS代理
    print("\n----- 测试V2Ray SOCKS代理 -----")
    socks_config = V2RAY_CONFIG['socks']
    socks_url = f"{socks_config['protocol']}://{socks_config['host']}:{socks_config['port']}"
    
    socks_success, socks_ip = test_proxy_connection(socks_url, "SOCKS")
    results['socks'] = {
        'success': socks_success,
        'ip': socks_ip
    }
    
    # 测试HTTP代理
    print("\n----- 测试V2Ray HTTP代理 -----")
    http_config = V2RAY_CONFIG['http']
    http_url = f"{http_config['protocol']}://{http_config['host']}:{http_config['port']}"
    
    http_success, http_ip = test_proxy_connection(http_url, "HTTP")
    results['http'] = {
        'success': http_success,
        'ip': http_ip
    }
    
    return results

def test_proxy_connection(proxy_url, proxy_type):
    """测试代理连接"""
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    print(f"正在测试 {proxy_type} 代理: {proxy_url}")
    
    try:
        response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=15)
        if response.status_code == 200:
            ip = response.json().get('ip')
            print(f"✅ {proxy_type} 代理工作正常")
            print(f"🌐 代理IP: {ip}")
            return True, ip
        else:
            print(f"❌ {proxy_type} 代理连接异常: 状态码 {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ {proxy_type} 代理连接失败: {e}")
        return False, None

def create_chain_proxy(remote_proxy, base_proxy_type="socks"):
    """创建二级代理链"""
    # 使用V2Ray作为基础代理
    if base_proxy_type == "socks":
        base_proxy = V2RAY_CONFIG['socks']
        base_url = f"{base_proxy['protocol']}://{base_proxy['host']}:{base_proxy['port']}"
    else:
        base_proxy = V2RAY_CONFIG['http']
        base_url = f"{base_proxy['protocol']}://{base_proxy['host']}:{base_proxy['port']}"
    
    # 解析远程代理
    remote = parse_proxy_string(remote_proxy)
    if not remote:
        print(f"❌ 无法解析远程代理: {remote_proxy}")
        return None, None
    
    # 构建代理链信息
    if remote.get('requires_auth', True):
        remote_auth = f"{remote['user']}:{remote['pass']}@"
    else:
        remote_auth = ""
    
    # 这里构建的是显示用信息，不是实际URL
    chain_info = f"{base_url} -> {remote['host']}:{remote['port']}"
    
    return {
        'base_proxy': base_url,
        'remote_proxy': remote_proxy,
        'chain_info': chain_info,
        'remote_host': remote['host'],
        'remote_port': remote['port'],
        'remote_auth': remote_auth,
        'remote_requires_auth': remote.get('requires_auth', True)
    }, chain_info

def test_through_v2ray(remote_proxy_str, base_proxy_type="socks"):
    """通过V2Ray测试远程代理"""
    chain_proxy, chain_info = create_chain_proxy(remote_proxy_str, base_proxy_type)
    if not chain_proxy:
        return False, None
    
    print(f"\n===== 通过V2Ray {base_proxy_type.upper()} 测试远程代理 =====")
    print(f"代理链: {chain_info}")
    
    # 通过V2Ray配置请求
    base_proxies = {
        'http': chain_proxy['base_proxy'],
        'https': chain_proxy['base_proxy']
    }
    
    try:
        # 使用Session对象以便于设置代理
        session = requests.Session()
        session.proxies.update(base_proxies)
        
        # 使用远程代理的详细信息进行连接测试
        print(f"尝试通过V2Ray连接到远程代理 {chain_proxy['remote_host']}:{chain_proxy['remote_port']}...")
        
        # 这里我们用不同的测试站点来验证我们是否真的通过远程代理访问
        test_urls = [
            "https://api.ipify.org?format=json",
            "https://httpbin.org/ip",
            "https://ifconfig.me/ip"
        ]
        
        for test_url in test_urls:
            try:
                print(f"测试URL: {test_url}")
                response = session.get(test_url, timeout=20)
                
                if response.status_code == 200:
                    if "api.ipify.org" in test_url:
                        ip = response.json().get('ip')
                    elif "httpbin.org" in test_url:
                        ip = response.json().get('origin')
                    else:  # ifconfig.me
                        ip = response.text.strip()
                    
                    print(f"✅ 测试成功! 返回IP: {ip}")
                    
                    # 验证IP是否与本地IP不同
                    _, local_ip = test_local_connection()
                    if local_ip and local_ip != ip:
                        print(f"✅ 确认代理工作正常! 代理IP ({ip}) 与本地IP ({local_ip}) 不同")
                        return True, ip
                    elif local_ip and local_ip == ip:
                        print(f"⚠️ 代理可能未生效! 返回IP ({ip}) 与本地IP相同")
                    else:
                        print(f"✅ 无法比较本地IP，但代理连接成功")
                        return True, ip
                else:
                    print(f"❌ 代理测试失败: 状态码 {response.status_code}")
            except Exception as e:
                print(f"❌ 测试 {test_url} 时出错: {e}")
        
        print("❌ 所有测试URL均失败")
        return False, None
    except Exception as e:
        print(f"❌ 通过V2Ray测试远程代理时出错: {e}")
        return False, None

def main():
    parser = argparse.ArgumentParser(description="测试带二级代理的代理链接")
    parser.add_argument("--local", action="store_true", help="测试本地网络连接")
    parser.add_argument("--v2ray", action="store_true", help="测试V2Ray代理")
    parser.add_argument("--chain", action="store_true", help="测试通过V2Ray连接远程代理")
    parser.add_argument("--proxy", type=str, help="指定要测试的远程代理 (格式: HOST:PORT:USER:PASS)")
    parser.add_argument("--all", action="store_true", help="测试所有配置")
    parser.add_argument("--socks", action="store_true", help="使用SOCKS协议测试")
    parser.add_argument("--http", action="store_true", help="使用HTTP协议测试")
    
    args = parser.parse_args()
    
    # 如果没有指定任何选项，默认测试所有
    if not (args.local or args.v2ray or args.chain or args.proxy):
        args.all = True
    
    # 如果没有指定代理协议，默认使用SOCKS
    if not (args.socks or args.http):
        args.socks = True
    
    # 测试本地连接
    if args.local or args.all:
        test_local_connection()
    
    # 测试V2Ray代理
    if args.v2ray or args.all:
        v2ray_results = test_v2ray_proxies()
        
        if not (v2ray_results['socks']['success'] or v2ray_results['http']['success']):
            print("\n❌ V2Ray代理测试失败，请检查V2Ray是否正常运行")
            return
    
    # 测试代理链
    base_proxy_types = []
    if args.socks:
        base_proxy_types.append("socks")
    if args.http:
        base_proxy_types.append("http")
    
    if args.chain or args.all:
        print("\n===== 测试通过V2Ray连接远程代理 =====")
        
        if args.proxy:
            # 测试指定的代理
            for base_type in base_proxy_types:
                test_through_v2ray(args.proxy, base_type)
        else:
            # 测试配置文件中的远程代理
            remote_proxies = [p for p in PROXIES if not p.startswith("127.0.0.1")]
            
            if not remote_proxies:
                print("❌ 配置文件中没有可用的远程代理")
                return
            
            results = []
            for proxy in remote_proxies:
                for base_type in base_proxy_types:
                    success, ip = test_through_v2ray(proxy, base_type)
                    if success:
                        results.append({
                            'proxy': proxy,
                            'base_type': base_type,
                            'ip': ip
                        })
            
            # 显示测试结果摘要
            print("\n===== 代理链测试结果摘要 =====")
            print(f"共测试 {len(remote_proxies) * len(base_proxy_types)} 个代理链组合，{len(results)} 个工作正常")
            
            if results:
                print("\n可用的代理链:")
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['base_type'].upper()} -> {result['proxy']} (IP: {result['ip']})")
            else:
                print("\n❌ 没有发现可用的代理链")

if __name__ == "__main__":
    main() 