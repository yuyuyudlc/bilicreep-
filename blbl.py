from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
import requests
import json

# 定义命令触发器
fetch_data = on_command("fetch_stats", aliases={"统计弹幕"}, priority=5)

@fetch_data.handle()
async def handle_first_receive(bot: Bot, event: Event):
    # 获取用户输入的 UID
    args = str(event.get_message()).strip()
    if not args:
        await fetch_data.finish("请提供 UID，例如：/fetch_stats 1234s5")
    
    uid = args.split()[-1]  # 获取 UID 参数，避免命令词影响
    url = f"https://api.aicu.cc/api/v3/search/getlivedm?uid={uid}&pn=1&ps=100&keyword="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    # 爬取数据
    await fetch_data.send(f"正在爬取 {uid} 的数据...")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
            # 解析 JSON 数据
            try:
                data = response.json()
            except json.JSONDecodeError:
                await fetch_data.finish("响应内容不是有效的 JSON 格式，请检查接口返回的数据。")

            if not data or not isinstance(data, dict):
                await fetch_data.finish("接口返回的数据为空或格式不正确，请检查 UID 是否正确。")

            # 获取房间列表
            data_field = data.get("data", {})
            if not isinstance(data_field, dict):
                await fetch_data.finish("接口返回的数据格式不符合预期，缺少 'data' 字段。")

            room_list = data_field.get("list", [])
            if not isinstance(room_list, list):
                await fetch_data.finish("弹幕为空")

            # 统计弹幕数量
            stats = {}
            for room in room_list:
                room_info = room.get("roominfo", {})
                if not isinstance(room_info, dict):
                    continue
                danmus = room.get("danmu", [])
                if not isinstance(danmus, list):
                    continue
                upname = room_info.get("upname", "未知主播")
                stats[upname] = stats.get(upname, 0) + len(danmus)

            # 构造结果字符串
            result = "弹幕统计结果：\n"
            for upname, count in stats.items():
                result += f"主播名称: {upname}, 弹幕数量: {count}\n"
            
            # 发送统计结果
            await fetch_data.finish(result)
    else:
            await fetch_data.finish(f"请求失败，状态码：{response.status_code}")
