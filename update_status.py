import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 状态映射字典
STATUS_MAP = {
    "#00FF00": "运行正常 (Active)",
    "#FFFF00": "仅遥测 (Telemetry Only)",
    "#FF0000": "冲突/异常 (Conflicted)",
    "#444444": "无信号 (No Signal)",
    "#C0C0C0": "数据过旧 (Heard)",
    "transparent": "未知"
}

def scrape_amsat():
    url = "https://www.amsat.org/status/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 定位状态表格 (AMSAT 页面通常只有一个主要的 table)
    table = soup.find('table', {'border': '1'})
    rows = table.find_all('tr')
    
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>业余无线电卫星状态 (中文版)</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; background: #f4f4f4; }}
            table {{ border-collapse: collapse; width: 100%; background: white; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #0055a4; color: white; }}
            .footer {{ margin-top: 20px; font-size: 0.8em; color: #666; }}
        </style>
    </head>
    <body>
        <h2>卫星实时状态报告 (中文镜像)</h2>
        <p>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (北京时间)</p>
        <table>
            <tr>
                <th>卫星名称</th><th>最后记录</th><th>状态</th><th>上行频率</th><th>下行频率/信标</th>
            </tr>
    """

    # 遍历表格行（跳过表头）
    for row in rows[1:]:
        cols = row.find_all('td')
        if len(cols) < 3: continue
        
        name = cols[0].text.strip()
        time = cols[1].text.strip()
        
        # 提取颜色来判断状态
        color = cols[2].get('bgcolor', 'transparent').upper()
        status_cn = STATUS_MAP.get(color, "未知")
        
        # 频率信息（简单汉化）
        up = cols[3].text.strip() if len(cols) > 3 else "-"
        down = cols[4].text.strip() if len(cols) > 4 else "-"
        
        html_content += f"""
            <tr>
                <td><b>{name}</b></td>
                <td>{time}</td>
                <td style="background-color:{color};">{status_cn}</td>
                <td>{up}</td>
                <td>{down}</td>
            </tr>
        """
        
    html_content += "</table><div class='footer'>数据来源: AMSAT.org | 自动更新自 GitHub Actions</div></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    scrape_amsat()
