"""
功能: 通过网络抓包获取金铲铲之战游戏数据

步骤:
1. 启用Root权限
2. 设置网络代理
3. 抓取并分析游戏网络请求
4. 解析数据并保存

注意事项:
- 需要启用模拟器Root权限
- 需要安装证书以解密HTTPS流量
- 建议使用代理工具(如Charles/Fiddler)配合分析
"""

import os
import subprocess
import time
import json
from typing import Optional, Dict, List


class TFTDataCollector:
    def __init__(self):
        """
        初始化数据采集器

        属性:
        - mumu_path: MuMu模拟器安装路径
        - charles_path: Charles安装路径
        - charles_port: Charles代理端口
        - vm_index: 模拟器实例索引
        - tft_package: 金铲铲之战包名
        """
        self.mumu_path = r"B:\Program Files\Netease\MuMu Player 12"
        self.charles_path = r"C:\Program Files\Charles"
        self.charles_port = 8888
        self.vm_index = 0  # 默认使用第一个模拟器实例
        self.tft_package = "com.tencent.jkchess"

        # 检查adb工具的几个可能位置
        adb_paths = [
            os.path.join(self.mumu_path, "shell", "tools", "adb.exe"),
            os.path.join(self.mumu_path, "tools", "adb.exe"),
            os.path.join(self.mumu_path, "adb.exe"),
            os.path.join(self.mumu_path, "shell", "adb.exe"),
        ]

        self.adb_path = None
        for path in adb_paths:
            if os.path.exists(path):
                self.adb_path = path
                break

    def setup_capture(self) -> bool:
        """设置抓包环境"""
        print("=== 金铲铲之战数据采集器 ===\n")
        print("1. 检查Charles...")

        # 获取项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 检查Charles是否已安装
        if not os.path.exists(self.charles_path):
            print(f"错误: 找不到Charles安装目录: {self.charles_path}")
            return False

        # 检查证书
        print("2. 检查Charles证书...")
        cert_path = os.path.join(root_dir, "shared", "jcc.pem")
        print(f"查找证书: {cert_path}")

        if not os.path.exists(cert_path):
            print(f"错误: 找不到证书文件: {cert_path}")
            return False

        print(f"找到证书文件: {cert_path}")

        print("3. 安装证书...")
        try:
            # 先在Windows上安装证书
            print("\n3.1 在Windows上安装证书...")
            import ctypes

            # 检查是否以管理员权限运行
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("请以管理员权限运行此脚本")
                print("1. 右键点击VS Code")
                print("2. 选择'以管理员身份运行'")
                print("3. 重新运行此脚本")
                return False

            # 导入证书到Windows
            import subprocess

            subprocess.run(
                ["certutil", "-addstore", "ROOT", cert_path],
                capture_output=True,
                text=True,
                check=True,
            )
            print("Windows证书安装完成!")

            # 在模拟器中安装证书
            print("\n3.2 安装证书到模拟器...")
            if not self.adb_path:
                print("错误: adb路径未设置")
                return False

            adb_path = str(self.adb_path)

            # 检查模拟器是否连接
            print("检查模拟器连接...")
            result = subprocess.run(
                [adb_path, "devices"],
                capture_output=True,
                text=True,
                check=True,
            )

            if "device" not in result.stdout:
                print("错误: 未检测到模拟器，请确保模拟器已启动")
                return False

            # 将证书复制到模拟器
            print("复制证书到模拟器...")
            subprocess.run(
                [
                    adb_path,
                    "push",
                    cert_path,
                    "/sdcard/Download/charles.pem",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            print("\n请按以下步骤在模拟器中安装证书:")
            print("\n第1步: ✓ 已完成 - 打开设置")

            print("\n第2步: 找到安全设置")
            print("➡️ 在设置列表中:")
            print("  1. 向下滚动找到'安全和紧急情况'")
            print("  2. 图标是一个❄️雪花图标")
            print("  3. 点击进入'安全和紧急情况'")
            print("\n提示: 在截图中它位于'密码和账号'选项的上方")
            input("找到并点击'安全和紧急情况'后按回车继续...")

            print("\n第3步: 找到证书安装选项")
            print("➡️ 在'安全'设置中:")
            print("  1. 找到'加密与凭据'")
            print("  2. 点击'安装证书'或'从存储设备安装'")
            print("  3. 选择'CA证书'类型")
            input("找到证书安装选项后按回车继续...")

            print("\n第4步: 选择证书文件")
            print("➡️ 在文件浏览器中:")
            print("  1. 点击左上角的菜单或'浏览'")
            print("  2. 找到'Download'文件夹")
            print("  3. 点击'charles.pem'文件")
            input("选择证书文件后按回车继续...")

            print("\n第5步: 完成安装")
            print("➡️ 在证书安装界面:")
            print("  1. 输入证书名称: charles")
            print("  2. 点击'确定'或'安装'")
            print("  3. 如果提示'不安全的证书'")
            print("     点击'仍然安装'")
            input("\n证书安装完成后按回车继续...")

            # 设置系统代理
            print("\n4. 设置系统代理...")
            subprocess.run(
                [
                    adb_path,
                    "shell",
                    "settings",
                    "put",
                    "global",
                    "http_proxy",
                    f"127.0.0.1:{self.charles_port}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            print("代理设置完成!")

        except Exception as e:
            print(f"设置失败: {e}")
            print("\n请检查:")
            print("1. 是否以管理员权限运行")
            print("2. 模拟器是否已启动")
            print("3. Root权限是否已开启")
            print("4. ADB调试是否已启用")
            return False

        print("\n设置完成! 现在可以开始抓包了。")
        print("提示: 如果还是看不到HTTPS请求，请:")
        print("1. 重启模拟器")
        print("2. 重启Chrome浏览器")
        print("3. 清除浏览器缓存")
        return True

    def connect_emulator(self) -> bool:
        """连接MuMu模拟器"""
        try:
            if not self.adb_path:
                print("错误: adb路径未设置")
                return False

            adb_path = str(self.adb_path)

            # 先测试共享文件夹连接
            print("测试模拟器共享文件夹连接...")
            shared_folder = os.path.join(
                os.getcwd(), "shared"
            )  # 使用项目目录下的shared文件夹
            os.makedirs(shared_folder, exist_ok=True)  # 确保文件夹存在

            test_file = os.path.join(shared_folder, "test_connection.txt")

            try:
                # 创建测试文件
                print("创建测试文件...")
                with open(test_file, "w", encoding="utf-8") as f:
                    f.write("测试模拟器连接")

                print("检查模拟器是否能读取文件...")
                # 检查模拟器是否能读取文件
                result = subprocess.run(
                    [
                        adb_path,
                        "shell",
                        "ls",  # 先列出目录内容
                        "/sdcard/MuMu12Shared/",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                print(f"共享目录内容:\n{result.stdout}")

                # 然后尝试读取文件
                result = subprocess.run(
                    [
                        adb_path,
                        "shell",
                        "cat",
                        "/sdcard/MuMu12Shared/test_connection.txt",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                if "测试模拟器连接" in result.stdout:
                    print("成功通过共享文件夹连接到模拟器!")
                else:
                    print("共享文件夹连接测试失败")

            except Exception as e:
                print(f"共享文件夹测试失败: {e}")
                print("\n请检查:")
                print("1. 模拟器文件传输设置:")
                print(f"   - 电脑共享路径是否为: {shared_folder}")
                print("   - 安卓共享路径是否为: /sdcard/MuMu12Shared")
                print("2. 重启模拟器后再试")
            finally:
                # 清理测试文件
                try:
                    os.remove(test_file)
                except:
                    pass

            # 等待模拟器完全启动
            print("等待模拟器完全启动...")
            time.sleep(10)

            # 尝试多次连接模拟器
            max_retries = 3
            for i in range(max_retries):
                try:
                    print(f"尝试连接模拟器 (第{i+1}次)...")

                    # 检查模拟器网络是否就绪
                    if i == 0:
                        print("检查模拟器网络...")
                        subprocess.run(
                            [
                                adb_path,
                                "shell",
                                "settings",
                                "get",
                                "global",
                                "adb_enabled",
                            ],
                            capture_output=True,
                            text=True,
                            check=True,
                        )

                    result = subprocess.run(
                        [adb_path, "connect", "127.0.0.1:16384"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                    if "connected" in result.stdout.lower():
                        print("成功连接到模拟器")
                        return True

                    time.sleep(2)

                except subprocess.CalledProcessError as e:
                    if "adb_enabled" in str(e):
                        print("\n错误: ADB调试未启用")
                        print("请在模拟器中:")
                        print("1. 点击'其他设置'")
                        print("2. 找到'Root权限'和'ADB调试'")
                        print("3. 确保两者都已开启")
                        print("4. 点击'保存设置'")
                        print("5. 重启模拟器")
                        return False

                    if i < max_retries - 1:
                        print("连接失败，等待后重试...")
                        time.sleep(2)
                        continue
                    raise

            print("\n连接失败。由于可以访问共享文件夹，请检查:")
            print("1. 在模拟器设置中:")
            print("   - 点击'其他设置'")
            print("   - 开启'Root权限'和'ADB调试'")
            print("   - 点击'保存设置'")
            print("2. 重启模拟器，等待完全启动（约30秒）")
            print("3. 如果还是不行，尝试:")
            print("   - 在模拟器中打开任意应用")
            print("   - 或重启电脑后再试")
            return False

        except Exception as e:
            print(f"连接模拟器时出错: {e}")
            return False

    def setup_proxy(self) -> bool:
        """设置系统代理到Charles"""
        try:
            if not self.adb_path:
                return False

            adb_path = str(self.adb_path)

            # 设置HTTP代理
            subprocess.run(
                [
                    adb_path,
                    "shell",
                    "settings",
                    "put",
                    "global",
                    "http_proxy",
                    f"127.0.0.1:{self.charles_port}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            print(f"已设置系统代理到Charles(127.0.0.1:{self.charles_port})")
            return True

        except subprocess.CalledProcessError as e:
            print(f"设置代理时出错: {e}")
            return False

    def install_charles_cert(self) -> bool:
        """安装Charles证书"""
        try:
            if not self.adb_path:
                return False

            adb_path = str(self.adb_path)

            # 打开证书下载页面
            subprocess.run(
                [
                    adb_path,
                    "shell",
                    "am",
                    "start",
                    "-a",
                    "android.intent.action.VIEW",
                    "-d",
                    "http://chls.pro/ssl",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            print("\n请在模拟器中完成以下步骤:")
            print("1. 下载证书")
            print("2. 点击下载的证书文件")
            print("3. 在证书安装界面输入证书名称(随意)")
            print("4. 点击确定完成安装")

            input("\n完成证书安装后按回车继续...")
            return True

        except subprocess.CalledProcessError as e:
            print(f"安装证书时出错: {e}")
            return False

    def launch_game(self):
        """启动金铲铲之战"""
        try:
            cmd = (
                f"MuMuManager.exe api -v {self.vm_index} launch_app {self.tft_package}"
            )
            subprocess.run(cmd, cwd=self.mumu_path, check=True)
            time.sleep(15)  # 等待游戏启动
            return True
        except Exception as e:
            print(f"启动游戏失败: {e}")
            return False

    def capture_screen(self):
        """获取当前屏幕截图"""
        try:
            # 截图保存到模拟器
            cmd = f"MuMuManager.exe adb -v {self.vm_index} shell screencap /data/screen.png"
            subprocess.run(cmd, cwd=self.mumu_path, check=True)

            # 将截图复制到电脑
            save_path = os.path.join(os.getcwd(), "screenshots")
            os.makedirs(save_path, exist_ok=True)

            cmd = f"MuMuManager.exe adb -v {self.vm_index} pull /data/screen.png {save_path}/screen.png"
            subprocess.run(cmd, cwd=self.mumu_path, check=True)

            return os.path.join(save_path, "screen.png")
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def _parse_adb_port(self, output):
        """解析ADB端口信息"""
        # 需要根据实际输出格式解析端口号
        pass

    def enable_root(self):
        """启用Root权限"""
        try:
            cmd = f"MuMuManager.exe setting -v {self.vm_index} -k root_permission -val true"
            subprocess.run(cmd, cwd=self.mumu_path, check=True)
            return True
        except Exception as e:
            print(f"启用Root失败: {e}")
            return False

    def capture_game_data(self) -> Optional[Dict]:
        """
        抓取游戏数据

        返回:
        - 游戏数据字典,包含:
          - 玩家信息
          - 装备数据
          - 英雄数据
          - 对局数据
        """
        try:
            # 1. 启动游戏
            if not self.launch_game():
                return None

            # 2. 开始抓包
            game_data = self._capture_network()

            # 3. 解析数据
            parsed_data = self._parse_game_data(game_data)

            return parsed_data
        except Exception as e:
            print(f"抓取游戏数据失败: {e}")
            return None

    def _capture_network(self) -> List[Dict]:
        """
        抓取网络请求

        返回:
        - 网络请求数据列表
        """
        try:
            # 这里需要实现网络抓包逻辑
            # 可以使用mitmproxy等工具
            captured_data = []
            return captured_data
        except Exception as e:
            print(f"抓取网络请求失败: {e}")
            return []

    def _parse_game_data(self, network_data: List[Dict]) -> Dict:
        """
        解析游戏数据

        输入:
        - network_data: 网络请求数据列表

        返回:
        - 解析后的游戏数据
        """
        game_data = {
            "player_info": {},
            "equipment": [],
            "heroes": [],
            "battle_info": {},
        }

        # 解析网络请求中的游戏数据
        for request in network_data:
            if "player/info" in request["url"]:
                game_data["player_info"] = self._parse_player_info(request)
            elif "equipment/list" in request["url"]:
                game_data["equipment"] = self._parse_equipment(request)
            elif "heroes/list" in request["url"]:
                game_data["heroes"] = self._parse_heroes(request)
            elif "battle/info" in request["url"]:
                game_data["battle_info"] = self._parse_battle_info(request)

        return game_data

    def _parse_player_info(self, request: Dict) -> Dict:
        """解析玩家信息"""
        # 实现玩家信息解析逻辑
        return {}

    def _parse_equipment(self, request: Dict) -> List:
        """解析装备数据"""
        # 实现装备数据解析逻辑
        return []

    def _parse_heroes(self, request: Dict) -> List:
        """解析英雄数据"""
        # 实现英雄数据解析逻辑
        return []

    def _parse_battle_info(self, request: Dict) -> Dict:
        """解析对局数据"""
        # 实现对局数据解析逻辑
        return {}


def main():
    """主函数"""
    collector = TFTDataCollector()

    print("=== 金铲铲之战数据采集器 ===")

    # 1. 检查Charles
    print("\n1. 检查Charles...")
    if not collector.setup_capture():
        print("请先启动Charles并按说明配置")
        return

    # 2. 连接模拟器
    print("\n2. 连接模拟器...")
    if not collector.connect_emulator():
        print("请确保MuMu模拟器已启动")
        return

    # 3. 设置抓包环境
    print("\n3. 设置抓包环境...")
    if not collector.setup_capture():
        print("设置抓包环境失败")
        return

    # 4. 启动游戏
    print("\n4. 启动金铲铲之战...")
    if not collector.launch_game():
        print("请确保金铲铲之战已安装")
        return

    print("\n5. 开始抓包...")
    print("请在游戏中操作,数据会显示在Charles中")
    print("按Ctrl+C结束抓包")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n抓包结束")


if __name__ == "__main__":
    main()
