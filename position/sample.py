#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Sample program
"""

from PositionModule import *
from routing.graph import *

def main():

    # 성능 측정기 생성
    performane = PerformanceTimer("해 평가 소요 시간")

    # 입력 데이터 생성
    ObjectList = getObjectSampleList()
    typeList = TypeInfoReader().preTypeList
    space= Space()

    # 위치 결정 모듈 생성
    positionModule = PositionModule(space, typeList, "GridSearcher")

    performane.start()
     # 위치결정 모듈 사용. PositionResult 라는 형태의 클래스 리턴. 이 클래스는 PositionModule.py 파일에 정의되어 있음
    positionResult = positionModule.setPosition(ObjectList)
    performane.end()

    print "남은 면적 : " + str(positionResult.remainArea)
    print "성공 여부 : " + str(positionResult.isAllSetted)

    print performane.sPrint()

if __name__ == '__main__':
    main()