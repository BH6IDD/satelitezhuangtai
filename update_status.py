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
    # 使用更新的浏览器标识，减少被拦截的概率
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 核心改进：遍历所有表格，寻找包含 "Satellite" 标题的那一个
        table = None
        for t in soup.find_all('table'):
            if "Satellite" in t.text:
                table = t
                break
        
        if not table:
            raise Exception("无法在页面上定位卫星数据表格")

        rows = table.find_all('tr')
        
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>业余无线电卫星状态 (中文镜像)</title>
            <style>
                body {{ font-family: -apple-system, system-ui, sans-serif; padding: 10px; background: #f0f2f5; color: #1c1e21; }}
                .container {{ max-width: 900px; margin: auto; background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
                h2 {{ color: #0055a4; text-align: center; margin-bottom: 5px; }}
                .time {{ text-align: center; color: #65676b; font-size: 0.9em; margin-bottom: 20px; }}
                table {{ border-collapse: collapse; width: 100%; font-size: 14px; border: none; }}
                th, td {{ padding: 12px 8px; text-align: left; border-bottom: 1px solid #ebedf0; }}
                th {{ background-color: #f8f9fa; color: #4b4f56; font-weight: 600; }}
                tr:hover {{ background-color: #f2f3f5; }}
                .status-cell {{ border-radius: 4px; padding: 4px 8px; font-weight: bold; font-size: 12px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #bcc0c4; text-align: center; border-top: 1px solid #ebedf0; padding-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🛰️ 卫星实时状态 (中文镜像)</h2>
                <p class="time">更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (北京时间)</p>
                <table>
                    <thead>
                        <tr><th>卫星名称</th><th>最后记录</th><th>当前状态</th><th>上/下行频率</th></tr>
                    </thead>
                    <tbody>
        """

        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) < 3: continue
            
            name = cols[0].get_text(strip=True)
            time = cols[1].get_text(strip=True)
            color = cols[2].get('bgcolor', 'transparent').upper()
            status_cn = STATUS_MAP.get(color, "未知")
            
            # 合并频率信息并简单处理换行
            up = cols[3].get_text(strip=True) if len(cols) > 3 else "-"
            down = cols[4].get_text(strip=True) if len(cols) > 4 else "-"
            
            # 处理状态单元格的文字颜色（如果是深色背景则用白色文字）
            text_color = "white" if color in ["#444444", "#FF0000"] else "black"
            
            html_content += f"""
                <tr>
                    <td><b>{name}</b></td>
                    <td>{time}</td>
                    <td><span class="status-cell" style="background-color:{color}; color:{text_color};">{status_cn}</span></td>
                    <td style="font-family: monospace; font-size: 12px;">上: {up}<br>下: {down}</td>
                </tr>
            """
            
        html_content += """
                    </tbody>
                </table>
                <div class='footer'>
                    数据源: AMSAT.org | 自动更新: GitHub Actions | BH6IDD 卫星状态监测
                </div>
            </div>
        </body>
        </html>
        """
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("网页生成成功！")

    except Exception as e:
        print(f"执行过程中出错: {e}")
        # 即使失败也保留一个基础页面
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(f"<html><body><h1>更新暂时受阻</h1><p>错误详情: {e}</p></body></html>")

if __name__ == "__main__":
    scrape_amsat()
