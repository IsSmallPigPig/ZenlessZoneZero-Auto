# -*- coding: utf-8 -*-
""" 
@file:      others.py
@time:      2024/7/10 上午2:38
@author:    sMythicalBird
"""

import time
from datetime import datetime
from typing import Dict
import numpy as np
from schema import Position, info
from utils import control, get_map_info, auto_find_way, config, logger
from utils.task import task
from utils.detect.current import find_current

map_name = config.targetMap.Zone
map_level = config.targetMap.Level
logger.debug(f"地图名称: {map_name}, 地图等级: {map_level}")


# 进入地图读取信息
@task.page(
    name="地图层数",
    priority=0,
    target_texts=["背包", "^当前层数"],
    exclude_texts=["特殊区域"],
)
def grid_map(screen: np.ndarray):
    # 判断是否在进入事件对话，检查是否可以找到自身位置
    k = find_current()
    if not k:  # 不在地图中
        control.press("space")
        return
    # 超过地图最大时间
    if (datetime.now() - info.entryMapTime).total_seconds() > config.maxMapTime:
        logger.debug("长时间处于地图中，退出地图")
        control.esc()
        return
    control.scroll(-5)
    # 全通和零号业绩拆开做
    # 零号业绩相关的判断
    # 旧都列车地图需要移动，其他地图不需要
    if map_name == "旧都列车":
        if config.wholeCourse == False:
            if info.currentStage == 1 and (k := find_current()):
                control.move_at(k.x, k.y, 360, 500)
            # 不在往上走了
            # elif info.currentStage == 2 and (k := find_current()):
            #     control.move_at(k.x, k.y, 900, 500)
        else:  # 向下拖拽
            if info.currentStage == 5 and (k := find_current()):
                control.move_at(k.x, k.y, 640, 500)
    # 获取地图信息
    map_info = get_map_info(screen)
    if not map_info:
        logger.debug("未识别到地图信息")
        return
    # 寻路
    mapWay = auto_find_way(map_info)
    # 在地图但未识别到足够的地图信息做路径搜索
    if not mapWay:
        logger.debug("未找到路径")
        return
    (mc, dirct) = mapWay[0]  # 去除下一个地图位置
    # 炸弹判断:当下一关是战斗且解锁炸弹,炸掉
    if mc.weight == 4 and info.hasBoom:
        info.hasBoom = False
        control.press("r", duration=0.1)
        time.sleep(1)
        return
    # 传送点，暂时离开，boss站,将偏移量置0，在boss站之后赋值，控制旧都列车在零号业绩和银行的视角拖拽，当传送之后再还原
    if mc.weight == 5:
        info.currentStage = 0
    # if map_name == "旧都列车" and config.wholeCourse == False:
    #     if mc.weight == 5:  # 拿完零号业绩到传送点
    #         info.currentStage = 0
    control.press(str(dirct), duration=0.1)
    # info.lastDirct = dirct
    # 进战斗时需要计时，未防止战斗多次重置时间，不写在战斗函数中
    info.lastMoveTime = datetime.now()


@task.page(name="选择角色", target_texts=["出战"])
def action(positions: Dict[str, Position]):
    pos = positions.get("出战")
    control.click(pos.x, pos.y)
    info.entryMapTime = datetime.now()  # 进入地图时间
    info.fightCount += 1  # 战斗次数记录
    info.currentStage = 0  # 进入战斗，无偏移
    info.hasBoom = config.hasBoom
    # 等待加载进入动画，这个时间不能动，防止提前进行地图截取("施工废墟")


@task.page(name="选择副本", target_text="作战机略", target_texts=[map_name])
def select_map(positions: Dict[str, Position]):
    pos = positions.get(map_name)
    control.click(pos.x, pos.y)


@task.page(name="选择副本等级", target_texts=[map_level, "下一步"])
def select_level(positions: Dict[str, Position]):
    pos = positions.get(map_level)
    control.click(pos.x, pos.y)
    time.sleep(2)
    pos = positions.get("下一步")
    control.click(pos.x, pos.y)


@task.page(name="退出", target_texts=["^放弃$", "^暂离$"])
def exit_map(positions: Dict[str, Position]):
    pos = positions.get("^放弃$")
    control.click(pos.x, pos.y)


@task.page(name="结算界面", target_texts=["^完成$", "^执照等级$"])
def settle(positions: Dict[str, Position]):
    pos = positions.get("^完成$")
    control.click(pos.x, pos.y)
