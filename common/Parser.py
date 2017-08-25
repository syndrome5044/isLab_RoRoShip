#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Classes and functions to parse json files
"""

import json
from Miscellaneous import *

SHIP_LAYOUT_INFO = "../common/inputLayout.json"
TYPE_INFO = "../common/freight_list.json"


# 선박의 정보를 파싱하는 클래스
# Class for retrieving information about a vessel and cargoes types from json files
class Parser:
    def __init__(self):
        # Variables for parse a ship
        self.floors = []
        self.typeList = []
        self.minWidth = 1000000
        self.minLength = 1000000

        self.parseShipInformation()
        self.parseTypeInformation()

    def parseShipInformation(self):
        # json 파일을 읽고 정보를 저장
        configJSON = self.readJSON(SHIP_LAYOUT_INFO)

        # Get information about floors
        FloorInfoList = []
        availSpace = []
        for floor in configJSON["loadingSpaceList"]["loadingSpace"]:
            FloorInfoList.append(Space(floor["width"], floor["length"], floor["height"]))
            availSpace.append(floor["width"] * floor["length"])

        # number of floors
        numOfFl = len(FloorInfoList)

        # 입구 정보를 리스트로 관리
        # List of entrances
        EnterInfoList = [[]]
        temp = 0
        for enterInfo in configJSON["enterList"]["enter"]:
            flNum = enterInfo["floor"] - 1

            # Because on each floor can be zero or more entrances
            # We append a new list only when changing of the floor number occurs
            while temp < flNum:
                EnterInfoList.append([])
                temp += 1

            EnterInfoList[flNum].append(
                Enter(Coordinate(flNum, enterInfo["coordinate"]["X"], enterInfo["coordinate"]["Y"]),
                      enterInfo["volume"]["width"], enterInfo["volume"]["length"], enterInfo["id"]))

            availSpace[flNum] -= enterInfo["volume"]["width"] * enterInfo["volume"]["length"]

        # generate dummy elements if last floors do not have entrances
        while len(EnterInfoList) < numOfFl:
            EnterInfoList.append([])

        # 장애물 정보를 리스트로 관리
        # List of obstacles on a vessel
        ObstacleInfoList = [[]]
        temp = 0
        for obstacleInfo in configJSON["obstacleList"]["obstacle"]:
            flNum = obstacleInfo["floor"] - 1

            # Because on each floor can be zero or more obstacles
            # We append a new list only when changing of the floor number occurs
            while temp < flNum:
                ObstacleInfoList.append([])
                temp += 1

            ObstacleInfoList[flNum].append(
                Obstacle(Coordinate(flNum, obstacleInfo["coordinate"]["X"], obstacleInfo["coordinate"]["Y"]),
                         obstacleInfo["volume"]["width"], obstacleInfo["volume"]["length"], obstacleInfo["id"]))

            availSpace[flNum] -= obstacleInfo["volume"]["width"] * obstacleInfo["volume"]["length"]

        # generate dummy elements if last floors do not have obstacles
        while len(ObstacleInfoList) < numOfFl:
            ObstacleInfoList.append([])

        # List of spaces where cargo placing is prohibited
        NotLoadableSpaceList = [[]]
        temp = 0
        for space in configJSON["notLoadableSpaceList"]["notLoadableSpace"]:
            flNum = space["floor"] - 1

            while temp < flNum:
                NotLoadableSpaceList.append([])
                temp += 1

            NotLoadableSpaceList[flNum].append(
                NotLoadableSpace(Coordinate(flNum, space["coordinate"]["X"], space["coordinate"]["Y"]),
                                 space["width"], space["length"]))

            availSpace[flNum] -= space["width"] * space["length"]

        # generate dummy elements
        while len(NotLoadableSpaceList) < numOfFl:
            NotLoadableSpaceList.append([])

        # List of ramps
        RampInfoList = [[]]
        temp = 0
        for ramp in configJSON["rampList"]["ramp"]:
            flNum1 = ramp["connection"]["lower_floor"] - 1
            flNum2 = ramp["connection"]["upper_floor"] - 1

            while temp < flNum2:
                RampInfoList.append([])
                temp += 1

                RampInfoList[flNum1].append(
                    Ramp(Coordinate(flNum1, ramp["coordinate"]["X"], ramp["coordinate"]["Y"]),
                         ramp["volume"]["width"], ramp["volume"]["length"], ramp["id"], [flNum1, flNum2]))

                RampInfoList[flNum2].append(
                    Ramp(Coordinate(flNum2, ramp["coordinate"]["X"], ramp["coordinate"]["Y"]),
                         ramp["volume"]["width"], ramp["volume"]["length"], ramp["id"], [flNum1, flNum2]))

            availSpace[flNum1] -= ramp["volume"]["width"] * ramp["volume"]["length"]
            availSpace[flNum2] -= ramp["volume"]["width"] * ramp["volume"]["length"]

        # generate dummy elements
        while len(RampInfoList) < numOfFl:
            RampInfoList.append([])

        # List of slopes
        SlopeInfoList = [[]]
        temp = 0
        for slope in configJSON["slopeList"]["slope"]:
            flNum = slope["floor"] - 1

            while temp < flNum:
                SlopeInfoList.append([])
                temp += 1

            SlopeInfoList[flNum].append(
                Slope(Coordinate(flNum, slope["coordinate"]["X"], slope["coordinate"]["Y"]),
                      slope["volume"]["width"], slope["volume"]["length"], slope["id"]))

            availSpace[flNum] -= slope["volume"]["width"] * slope["volume"]["length"]

        # generate dummy elements if last floors do not have obstacles
        while len(SlopeInfoList) < numOfFl:
            SlopeInfoList.append([])

        # List of lifting decks
        DeckInfoList = [[]]
        temp = 0
        for deck in configJSON["floatingDeckList"]["floatingDeck"]:
            flNum = deck["floor"] - 1

            while temp < flNum:
                DeckInfoList.append([])
                temp += 1

                DeckInfoList[flNum].append(
                    LiftingDeck(Coordinate(flNum, deck["coordinate"]["X"], deck["coordinate"]["Y"]),
                                deck["volume"]["width"], deck["volume"]["length"], deck["id"], deck["lifting_height"]))

            # Lifting deck increases available space
            # availSpace[flNum] += deck["volume"]["width"] * deck["volume"]["length"]

        # generate dummy elements if last floors do not have obstacles
        while len(DeckInfoList) < numOfFl:
            DeckInfoList.append([])

        # Create array of available space and entrances/obstacles in each floor
        for i in range(numOfFl):
            self.floors.append(Floor(
                FloorInfoList[i],
                availSpace[i],
                EnterInfoList[i],
                ObstacleInfoList[i],
                NotLoadableSpaceList[i],
                RampInfoList[i],
                SlopeInfoList[i],
                DeckInfoList[i]
            ))

    def parseTypeInformation(self):
        configJSON = self.readJSON(TYPE_INFO)

        for t in configJSON["freight"]["freight_type"]:
            width = int(t["Full_width"])
            length = int(t["Full_length"])
            self.typeList.append(Type(width, length, int(t["Wheel_base"]), int(t["MAX_steer_angle"])))

            if width < self.minWidth:
                self.minWidth = width

            if length < self.minLength:
                self.minLength = length

    # json 파일을 읽어오는 함수
    @staticmethod
    def readJSON(filename):
        f = open(filename, 'r')
        js = json.loads(f.read())
        f.close()
        return js
