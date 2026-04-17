# config.py

# 有效国家代码列表（ISO 2字母代码）
VALID_COUNTRY_CODES = {
    'AF', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ',
    'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BA', 'BW', 'BV', 'BR',
    'IO', 'BN', 'BG', 'BF', 'BI', 'KH', 'CM', 'CA', 'CV', 'KY', 'CF', 'TD', 'CL', 'CN', 'CX',
    'CC', 'CO', 'KM', 'CG', 'CD', 'CK', 'CR', 'CI', 'HR', 'CU', 'CY', 'CZ', 'DK', 'DJ', 'DM',
    'DO', 'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF', 'PF',
    'TF', 'GA', 'GM', 'GE', 'DE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GG', 'GN',
    'GW', 'GY', 'HT', 'HM', 'VA', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM',
    'IL', 'IT', 'JM', 'JP', 'JE', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG', 'LA', 'LV',
    'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 'LU', 'MO', 'MK', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT',
    'MH', 'MQ', 'MR', 'MU', 'YT', 'MX', 'FM', 'MD', 'MC', 'MN', 'ME', 'MS', 'MA', 'MZ', 'MM',
    'NA', 'NR', 'NP', 'NL', 'NC', 'NZ', 'NI', 'NE', 'NG', 'NU', 'NF', 'MP', 'NO', 'OM', 'PK',
    'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN', 'PL', 'PT', 'PR', 'QA', 'RE', 'RO', 'RU',
    'RW', 'BL', 'SH', 'KN', 'LC', 'MF', 'PM', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'RS', 'SC',
    'SL', 'SG', 'SK', 'SI', 'SB', 'SO', 'ZA', 'GS', 'ES', 'LK', 'SD', 'SR', 'SJ', 'SZ', 'SE',
    'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TR', 'TM', 'TC',
    'TV', 'UG', 'UA', 'AE', 'GB', 'US', 'UM', 'UY', 'UZ', 'VU', 'VE', 'VN', 'VG', 'VI', 'WF',
    'EH', 'YE', 'ZM', 'ZW', 'UK', 'EU'
}

# 常见国家名称到代码的映射
COUNTRY_NAME_TO_CODE = {
    'united kingdom': 'GB',
    'uk': 'GB',
    'great britain': 'GB',
    'england': 'GB',
    'united states': 'US',
    'usa': 'US',
    'america': 'US',
    'australia': 'AU',
    'canada': 'CA',
    'germany': 'DE',
    'france': 'FR',
    'spain': 'ES',
    'italy': 'IT',
    'netherlands': 'NL',
    'ireland': 'IE',
    'scotland': 'GB',
    'wales': 'GB',
    'northern ireland': 'GB',
    'new zealand': 'NZ',
    'china': 'CN',
    'japan': 'JP',
    'india': 'IN',
    'brazil': 'BR',
    'russia': 'RU',
    'mexico': 'MX',
    'south africa': 'ZA',
    'sweden': 'SE',
    'norway': 'NO',
    'denmark': 'DK',
    'finland': 'FI',
    'belgium': 'BE',
    'switzerland': 'CH',
    'austria': 'AT',
    'portugal': 'PT',
    'greece': 'GR',
    'turkey': 'TR',
    'poland': 'PL',
    'singapore': 'SG',
    'hong kong': 'HK',
    'united arab emirates': 'AE',
    'uae': 'AE',
    'saudi arabia': 'SA',
    'europe': 'EU'
}

# List of SOCKS5 proxies in the format: HOST:PORT:USER:PASS
PROXIES = [
    "93.89.220.26:12323:14a5bbed33ad1:2df01fef65",
    "149.18.52.92:12323:14a5bbed33ad1:2df01fef65",
    "127.0.0.1:10808:none:none",  # 本地SOCKS代理，端口10808
    "127.0.0.1:10809:none:none",  # 本地HTTP代理，端口10809
    # Add more proxies here if needed
]

# V2Ray代理配置
V2RAY_CONFIG = {
    "socks": {
        "host": "127.0.0.1",
        "port": 10808,
        "protocol": "socks5"
    },
    "http": {
        "host": "127.0.0.1",
        "port": 10809,
        "protocol": "http"
    }
}

# 代理使用模式，可选值:
# "direct" - 直接使用远程代理，不通过V2Ray
# "v2ray" - 仅使用本地V2Ray代理
# "chain" - 通过V2Ray代理访问远程代理(二级代理链)
# "local" - 只使用本地网络，不使用任何代理
PROXY_MODE = "direct"

# 二级代理使用模式，设置为True表示远程代理需要通过本地V2Ray代理访问
USE_CHAIN_PROXY = True