# -*- coding: utf-8 -*-
import functools
import random
import sys
import copy

import loadInput
from deap import base
from deap import creator
from deap import tools

sys.path.insert(0, "C:\Python27\JolUp\position")
from position.PositionModule import *

typeList = [Type(8, 15, 100, 100), Type(9, 20, 100, 100), Type(9, 22, 100, 100), Type(13, 93, 100, 100), Type(11, 46, 100, 100)]

cargoList=[]
cargoIdList=[]

# JSON에서 읽고 저장함
filePath = "../order/cargo_input2.json"

def cargoShuffle(list):
    random.seed()
    random.shuffle(list)
    return list

cargoList = loadInput.loadInput(filePath)

# 리턴받은 리스트 처리
numOfCargoType = cargoList[0][0]
numOfGroupType = cargoList[0][1]
numOfCargo = cargoList[0][2]
del cargoList[0]

for i in range(len(cargoList)):
    cargoIdList.append(cargoList[i][0])


# Creator : 적합도(FitnessMax)와 후보해(Individual)를 생성한다.
# 이때 남은 공간이 많을 수록 optimal
creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


# Toolbox : 인자를 포함한 함수를 저장한다.
toolbox = base.Toolbox()

# Structure initializers
# individual(후보해) = cargoIdList에 random.suffle()을 적용한 것.
# population(군집) = 후보해의 리스트
genIndividual = functools.partial(cargoShuffle, cargoIdList)
toolbox.register("individual", tools.initIterate, creator.Individual, genIndividual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)




# The Evaluation Function
# 적합도(fitness)는 최소화되어야 한다.

def evalFunc(individual):
    space = Space()

    # 라우팅 모듈 생성
    routingModule = RoutingModule()
    # 위치결정 모듈 생성
    positionModule = PositionModule(space, routingModule, "MaxRects")

    objectList = []
    searchGroupid = 1
    searchCargoCount = 0

    while searchGroupid <= numOfGroupType:
        searchCargoCount = 0
        while searchCargoCount < numOfCargo:

            if cargoList[individual[searchCargoCount]][2] == searchGroupid:
                # group id / id / type
                tempObject = Object(searchGroupid, individual[searchCargoCount], typeList[cargoList[individual[searchCargoCount]][1]])
                objectList.append(tempObject)

            searchCargoCount = searchCargoCount + 1
        searchGroupid = searchGroupid + 1

    # 위치결정 모듈 사용. PositionResult 라는 형태의 클래스 리턴. 이 클래스는 PositionModule.py 파일에 정의되어 있음

    test = 1

    positionResult = positionModule.setPosition(objectList)

    print "남은 면적 : " + str(positionResult.remainArea)
    print "성공 여부 : " + str(positionResult.isAllSetted)
    return positionResult.remainArea,

# 연산자 추가
# 평가연산자
toolbox.register("evaluate", evalFunc)

# 교차연산자
# PMX교차 사용
toolbox.register("mate", tools.cxPartialyMatched)

# 변이연산자
# 짐ID의 순열을 유지하기 위한 변형된 함수 구현 필요
# 확률은 시험해보면서 조정할 것.
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

# 선택연산자
# 선택에 필요한 휴리스틱 구현할 것.
def select_heuristic():
    chosen = []
    return chosen

toolbox.register("select_heuristic", select_heuristic)
toolbox.register("select_rand", tools.selRandom, k=100)
toolbox.register("select", tools.selTournament, tournsize=numOfCargo)

# 메인함수
def main():
    random.seed(64)

    best_fitness_list = []

    # 300개의 후보해로 이루어진 초기 군집을 생성한다.
    # 각 후보해는 정수(화물ID)의 리스트이다.
    pop = toolbox.population(n=5)

    # CXPB : 두 후보해가 교차할 확률
    # MUTPB : 한 후보해가 변이할 확률
    # NGEN : 최대 세대의 수
    CXPB, MUTPB, NGEN = 0.5, 0.05, 40

    print("시작합니다.")

    # 전체 군집의 적합도 판단
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    print("  Evaluated %i individuals" % len(pop))

    # 진화 시작
    for g in range(NGEN):
        print("-- Generation %i --" % g)

        # 다음 세대를 위한 후보해 선택, 자손이라 명명
        offspring = toolbox.select(pop, len(pop))
        # 자손들을 복제하여 리스트에 저장
        offspring = list(map(toolbox.clone, offspring))

        # 자손 두명을 뽑는다
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # 난수를 생성하여 확률 CXPB보다 적을 경우 두 자손을 교차한다.
            if random.random() < CXPB:
                toolbox.mate(child1, child2)

                # 생성된 자손의 적합도를 평가한다
                del child1.fitness.values
                del child2.fitness.values

        '''
        newMutation를 정의한다.
        '''
        ospIndex = 0 # offspring의 mutant에 접근하기 위하여 인덱스선언. 변이된 individual(후보해)을 새로 덮어써야 하니까.
        for mutant in offspring: # offspring에서 후보해에 하나씩 접근
            newmutant = copy.deepcopy(mutant) # 그 mutant를 딥카피해서 newmutant에 대입한다. 이곳에 변이된 후의 후보해가 저장될 예정.
            numOfMutation = 0  # 후보해에서 변이가 일어난 CargoId의 개수
            oldIndex = []  # CargoId의 원래위치를 저장할 리스트.

            for i in range(0, len(mutant)): # i를 0부터 mutant의 길이-1 까지의 수를 증가시킴
                if random.random() < MUTPB: # 한 cargoId에 대해 난수 하나씩 생성한다. MUTPB보다 낮은 수가 나오면 변이한다.
                    numOfMutation = numOfMutation + 1 # 그럼 이제 변이할 거니까 변이 일어날 횟수가 늘어나겠지
                    oldIndex.append(i) # 변이가 일어날 cargoid의 위치를 리스트에 추가한다.

            if numOfMutation > 1: # 이게 1보다 크면 변이 발생.
                newIndex = copy.deepcopy(oldIndex)  # 변이는 섞는거니까 새로운 위치를 저장할 리스트도 필요하잖아. 그래서 일단은 oldIndex에서 딥카피해서 공간을 만듦.
                random.shuffle(newIndex)  # 우리의 변이는 선택된 cargoid끼리 뒤섞는 것이므로 셔플.

                for j in range(0, len(newIndex)):  # j를 0부터 newIndex의 길이-1 까지의 수를 증가시키면서
                    newmutant[oldIndex[j]] = mutant[
                        newIndex[j]]  # 이거좀 헷갈릴거 같네 newmutant에서 원래위치에 있던cargoId를 mutant의 나중 위치에 있는cargoId로 바꿈.
                offspring[ospIndex] = newmutant # offspring에 변이된 해로 업데이트시키고
                del mutant.fitness.values # 피트니스 지움
            ospIndex = ospIndex + 1 # 다음 후보해의 위치로 인덱스 증가시킴.
            '''
            # 난수를 생성하여 확률 MUTPB보다 적을 경우 한 자손을 변이한다.
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
            '''

        # 유효하지 않은 후보해의 적합도를 평가한다.(교차, 변이가 일어난 해)
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

         # best_fitness = min(fitnesses)
         # best_fitness_list.append(best_fitness)

        print("  Evaluated %i individuals" % len(invalid_ind))

        # 세대 교체
        pop[:] = offspring


    print("-- End of (successful) evolution --")
    print(best_fitness_list)

    #최적해 출력
    best_ind = tools.selBest(pop, 1)[0]


    #최적해 그룹 순서에 맞춰 정렬
    best_ind_sorted = []
    searchGroupid = 1
    searchCargoCount = 0

    while searchGroupid <= numOfGroupType:
        searchCargoCount = 0
        while searchCargoCount < numOfCargo:
            if cargoList[best_ind[searchCargoCount]][2] == searchGroupid:
                best_ind_sorted.append(best_ind[searchCargoCount])
            searchCargoCount = searchCargoCount + 1
        searchGroupid = searchGroupid + 1

    print("Best individual is %s" % (best_ind_sorted))
    print("Best fitness value is %s" % (best_ind.fitness.values))


if __name__ == "__main__":
    main()