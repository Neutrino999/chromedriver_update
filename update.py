import os
import subprocess
import requests
from bs4 import BeautifulSoup
import zipfile
import shutil

def get_current_version():
    try:
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.split()[1]  # 获取版本号部分
        return version
    except Exception as e:
        print(f"获取当前版本时出错: {str(e)}")
        return None

def get_latest_version():
    try:
        url = "https://googlechromelabs.github.io/chrome-for-testing/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含 "chromedriver" 和 "win64" 的表格行
        for row in soup.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 2:
                # 确保第一个单元格包含 chromedriver，第二个包含 win64
                first_cell = cells[0].find('code')
                second_cell = cells[1].find('code')
                if (first_cell and second_cell and 
                    'chromedriver' in first_cell.text and 
                    'win64' in second_cell.text):
                    # 获取下载链接
                    download_link = cells[2].find('code')
                    if download_link and 'chromedriver-win64.zip' in download_link.text:
                        download_url = download_link.text.strip()
                        version = download_url.split('/')[4]
                        return version, download_url
        return None, None
    except Exception as e:
        print(f"获取最新版本时出错: {str(e)}")
        return None, None

def update_chromedriver():
    version, download_url = get_latest_version()
    if not version or not download_url:
        print("无法获取最新版本信息")
        return

    try:
        # 下载文件
        print(f"正在下载 ChromeDriver {version}...")
        response = requests.get(download_url)
        zip_file = "chromedriver-win64.zip"
        
        with open(zip_file, 'wb') as f:
            f.write(response.content)

        # 解压文件
        print("正在解压文件...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # 首先确保temp目录不存在
            if os.path.exists("temp"):
                shutil.rmtree("temp")
            os.makedirs("temp")
            # 解压所有文件
            zip_ref.extractall("temp")

        # 复制并覆盖文件
        chromedriver_dir = os.path.join("temp", "chromedriver-win64")
        for file_name in os.listdir(chromedriver_dir):
            source_file = os.path.join(chromedriver_dir, file_name)
            target_file = os.path.join(os.getcwd(), file_name)
            
            # 如果目标文件存在，先删除
            if os.path.exists(target_file):
                os.remove(target_file)
            # 复制文件
            shutil.copy2(source_file, target_file)
            print(f"已复制文件: {file_name}")

        # 清理临时文件
        shutil.rmtree("temp")
        os.remove(zip_file)
        
        print(f"ChromeDriver 已更新到版本 {version}")
    except Exception as e:
        print(f"更新过程中出错: {str(e)}")

def main():
    while True:
        print("\nChromeDriver 更新工具")
        print("1. 获取当前版本")
        print("2. 获取最新版本")
        print("3. 更新到最新版本")
        print("4. 退出")
        
        choice = input("请选择操作 (1-4): ")
        
        if choice == '1':
            current_version = get_current_version()
            if current_version:
                print(f"当前 ChromeDriver 版本: {current_version}")
        elif choice == '2':
            version, _ = get_latest_version()
            if version:
                print(f"最新 ChromeDriver 版本: {version}")
        elif choice == '3':
            update_chromedriver()
        elif choice == '4':
            break
        else:
            print("无效的选择，请重试")

if __name__ == "__main__":
    main()