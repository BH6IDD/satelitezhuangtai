import requests
from bs4 import BeautifulSoup
from datetime import datetime

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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 改进的定位逻辑：直接找包含 "Satellite" 字样的表格
        table = None
        for t in soup.find_all('table'):
            if "Satellite" in t.text:
                table = t
                break
        
        if not table:
            raise Exception("无法定位数据表格")

        rows = table.find_all('tr')
        
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>业余无线电卫星状态 (中文版)</title>
            <style>
                body {{ font-family: -apple-system, sans-serif; padding: 10px; background: #f0f2f5; }}
                .container {{ max-width: 900px; margin: auto; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
                th, td {{ border: 1px solid #eee; padding: 10px; text-align: left; }}
                th {{ background-color: #0055a4; color: white; }}
                tr:nth-child(even) {{ background-color: #fafafa; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #888; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🛰️ 卫星实时状态 (中文镜像)</h2>
                <p>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (北京时间)</p>
                <table>
                    <tr><th>卫星名称</th><th>最后记录</th><th>状态</th><th>上/下行频率</th></tr>
        """

        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) < 3: continue
            
            name = cols[0].text.strip()
            time = cols[1].text.strip()
            color = cols[2].get('bgcolor', 'transparent').upper()
            status_cn = STATUS_MAP.get(color, "未知")
            
            # 合并频率信息减少宽度
            up = cols[3].text.strip() if len(cols) > 3 else "-"
            down = cols[4].text.strip() if len(cols) > 4 else "-"
            freq = f"上: {up}<br>下: {down}"
            
            html_content += f"""
                <tr>
                    <td><b>{name}</b></td>
                    <td>{time}</td>
                    <td style="background-color:{color}; color: {'white' if color=='#444444' else 'black'};"><b>{status_cn}</b></td>
                    <td>{freq}</td>
                </tr>
            """
            
        html_content += "</table><div class='footer'>数据来源: AMSAT.org | 自动更新自 GitHub Actions</div></div></body></html>"
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("抓取并生成成功！")

    except Exception as e:
        print(f"出错啦: {e}")
        # 如果出错，创建一个简单的错误页面，防止 Actions 报错
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(f"<html><body>数据更新暂时失败: {e}</body></html>")

if __name__ == "__main__":
    scrape_amsat()
